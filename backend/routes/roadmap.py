import re
from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, current_app, jsonify, request

from extensions import db
from models import (
    Goal,
    Roadmap,
    RoadmapItem,
    StudyLog,
    Topic,
    TopicPrerequisite
)
from ci_engines.rescheduler.engine import Rescheduler
from middleware.auth import check_goal_access


roadmap_bp = Blueprint(
    "roadmap",
    __name__,
    url_prefix="/api/v1/roadmap"
)


@roadmap_bp.post("/generate")
def generate_roadmap():
    data = request.get_json(silent=True) or {}

    goal_id = data.get("goal_id")

    if not goal_id:
        return jsonify({
            "status": "error",
            "message": "goal_id is required."
        }), 400

    try:
        goal = db.session.get(
            Goal,
            int(goal_id)
        )

        if goal is None:
            return jsonify({
                "status": "error",
                "message": "Goal not found."
            }), 404

        allowed, msg = check_goal_access(goal)
        if not allowed:
            code = 401 if ("Authentication required" in msg or "token" in msg.lower()) else 403
            return jsonify({
                "status": "error",
                "message": msg
            }), code

        topics = Topic.query.filter_by(
            track_id=goal.track_id
        ).order_by(
            Topic.id
        ).all()

        if not topics:
            return jsonify({
                "status": "error",
                "message": "No topics found for this learning track."
            }), 404

        topic_ids = {
            topic.id
            for topic in topics
        }

        prerequisite_rows = TopicPrerequisite.query.filter(
            TopicPrerequisite.topic_id.in_(topic_ids),
            TopicPrerequisite.prerequisite_topic_id.in_(topic_ids)
        ).all()

        search_topics = []

        for topic in topics:
            search_topics.append({
                "id": topic.id,
                "name": topic.name,
                "estimated_minutes": topic.estimated_minutes,
                "difficulty": topic.difficulty,
                "priority": topic.priority,
                "is_optional": topic.is_optional
            })

        prerequisites = [
            (
                row.topic_id,
                row.prerequisite_topic_id
            )
            for row in prerequisite_rows
        ]

        selected_topics = {
            topic.id
            for topic in topics
            if not topic.is_optional
        }

        # Resolve known topics specified in the learner's goal
        completed_topics = _resolve_known_topics(goal.known_topics, topics)

        # Exclude completed topics from required minutes so search and capacity accurately reflect remaining work
        required_minutes = sum(
            topic.estimated_minutes
            for topic in topics
            if not topic.is_optional and topic.id not in completed_topics
        )

        study_hours = float(
            goal.study_hours_per_day
        )

        daily_capacity = int(
            study_hours * 60
        )

        days_remaining = (
            goal.target_date - date.today()
        ).days + 1

        if days_remaining < 1:
            days_remaining = 1

        available_minutes = (
            days_remaining * daily_capacity
        )

        progress_ratio = 0.0

        optional_topics_remaining = sum(
            1
            for topic in topics
            if topic.is_optional
        )

        rescheduler = Rescheduler()

        result = rescheduler.evaluate(
            progress_ratio=progress_ratio,
            available_minutes=available_minutes,
            required_minutes=required_minutes,
            missed_days=0,
            backlog_minutes=0,
            optional_topics_remaining=optional_topics_remaining,
            current_streak=0,
            recent_replans=0,
            days_remaining=days_remaining,
            topics=search_topics,
            prerequisites=prerequisites,
            selected_topics=selected_topics,
            completed_topics=completed_topics,
            study_hours_per_day=study_hours
        )

        search_result = result.get("search")

        if not search_result:
            return jsonify({
                "status": "error",
                "message": "Roadmap search did not return a result.",
                "ci": {
                    "fuzzy": result.get("fuzzy"),
                    "expert": result.get("expert")
                }
            }), 500

        if not search_result.get("success"):
            return jsonify({
                "status": "error",
                "message": search_result.get(
                    "message",
                    "Could not generate roadmap."
                ),
                "ci": {
                    "fuzzy": result.get("fuzzy"),
                    "expert": result.get("expert"),
                    "search": search_result
                }
            }), 422

        topic_lookup = {
            topic.id: topic
            for topic in topics
        }

        daily_plan = []

        for index, day in enumerate(
            search_result.get(
                "daily_plan",
                []
            ),
            start=1
        ):
            day_tasks = []

            for task in day.get(
                "tasks",
                []
            ):
                topic_id = task.get("topic_id")

                topic = topic_lookup.get(
                    topic_id
                )

                if topic is None:
                    continue

                minutes = task.get(
                    "minutes",
                    0
                )

                day_tasks.append({
                    "topic_id": topic.id,
                    "name": topic.name,
                    "minutes": minutes,
                    "difficulty": topic.difficulty,
                    "is_optional": topic.is_optional
                })

            daily_plan.append({
                "day": day.get("day") or index,
                "total_minutes": sum(
                    task["minutes"]
                    for task in day_tasks
                ),
                "tasks": day_tasks
            })

        # ------------------------------------------------------------
        # SAVE THE ROADMAP TO MYSQL
        # Each call creates a new version. Older active versions for
        # this goal are marked "superseded" so history is kept.
        # ------------------------------------------------------------
        try:
            latest_version = db.session.query(
                db.func.max(Roadmap.version_number)
            ).filter(
                Roadmap.goal_id == goal.id
            ).scalar()

            next_version = (latest_version or 0) + 1

            db.session.query(Roadmap).filter(
                Roadmap.goal_id == goal.id,
                Roadmap.status == "active"
            ).update(
                {"status": "superseded"},
                synchronize_session=False
            )

            roadmap = Roadmap(
                goal_id=goal.id,
                version_number=next_version,
                status="active"
            )

            db.session.add(roadmap)
            db.session.flush()  # gives roadmap.id before the commit

            items = []

            for day in daily_plan:
                for task in day["tasks"]:
                    items.append(
                        RoadmapItem(
                            roadmap_id=roadmap.id,
                            topic_id=task["topic_id"],
                            day_number=int(day["day"]),
                            planned_minutes=int(
                                round(task["minutes"])
                            ),
                            status="pending"
                        )
                    )

            db.session.add_all(items)
            db.session.commit()

            saved_roadmap_id = roadmap.id
            saved_roadmap_version = roadmap.version_number
            saved_item_count = len(items)

        except Exception as save_error:
            db.session.rollback()

            return jsonify({
                "status": "error",
                "message": "Roadmap was generated but could not be saved.",
                "error": str(save_error)
            }), 500

        return jsonify({
            "status": "success",
            "message": "Personalized roadmap generated successfully.",

            "roadmap_id": saved_roadmap_id,
            "roadmap_version": saved_roadmap_version,
            "items_saved": saved_item_count,

            "goal": {
                "id": goal.id,
                "track_id": goal.track_id,
                "skill_level": goal.skill_level,
                "study_hours_per_day": goal.study_hours_per_day,
                "target_date": goal.target_date.strftime(
                    "%d/%m/%Y"
                ),
                "known_topics": (
                    goal.known_topics.split(",")
                    if goal.known_topics
                    else []
                )
            },

            "ci": {
                "fuzzy": result.get("fuzzy"),
                "expert": result.get("expert"),

                "search": {
                    "success": search_result.get(
                        "success"
                    ),
                    "sequence": search_result.get(
                        "sequence",
                        []
                    ),
                    "total_minutes": search_result.get(
                        "total_minutes",
                        0
                    ),
                    "daily_capacity": search_result.get(
                        "daily_capacity",
                        daily_capacity
                    ),
                    "total_days": search_result.get(
                        "total_days",
                        len(daily_plan)
                    ),
                    "search_cost": search_result.get(
                        "search_cost"
                    ),
                    "nodes_expanded": search_result.get(
                        "nodes_expanded"
                    )
                }
            },

            "roadmap": daily_plan
        }), 200

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "goal_id must be a valid number."
        }), 400

    except Exception as error:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Could not generate roadmap.",
            "error": str(error)
        }), 500


def _resolve_known_topics(known_topics_input, track_topics):
    """
    Parses known_topics (string or list of strings) and matches them by slug,
    name, normalized alphanumeric comparison, or distinctive keyword against
    the track's topics.
    Returns a set of matched topic IDs (int).
    """
    if not known_topics_input or not track_topics:
        return set()

    if isinstance(known_topics_input, str):
        raw_items = [
            t.strip()
            for t in known_topics_input.split(",")
            if t.strip()
        ]
    elif isinstance(known_topics_input, (list, tuple, set)):
        raw_items = [
            str(t).strip()
            for t in known_topics_input
            if str(t).strip()
        ]
    else:
        return set()

    def _get_val(obj, attr):
        if isinstance(obj, dict):
            return obj.get(attr)
        return getattr(obj, attr, None)

    matched_ids = set()

    for item in raw_items:
        clean = item.strip().lower()
        if not clean:
            continue

        normalized = re.sub(r"[^a-z0-9]", "", clean)
        if not normalized:
            continue

        # 1. Exact match on slug or name (case-insensitive)
        matched = False
        for topic in track_topics:
            t_id = _get_val(topic, "id")
            t_name = str(_get_val(topic, "name") or "").strip().lower()
            t_slug = str(_get_val(topic, "slug") or "").strip().lower()

            if clean == t_name or clean == t_slug:
                if t_id is not None:
                    matched_ids.add(t_id)
                matched = True
                break

        if matched:
            continue

        # 2. Normalized match (ignoring spaces, hyphens, and punctuation)
        for topic in track_topics:
            t_id = _get_val(topic, "id")
            t_name = str(_get_val(topic, "name") or "").strip().lower()
            t_slug = str(_get_val(topic, "slug") or "").strip().lower()

            norm_name = re.sub(r"[^a-z0-9]", "", t_name)
            norm_slug = re.sub(r"[^a-z0-9]", "", t_slug)

            if normalized == norm_name or normalized == norm_slug:
                if t_id is not None:
                    matched_ids.add(t_id)
                matched = True
                break

        if matched:
            continue

        # 3. Distinctive prefix / word match (e.g. "html" -> "HTML Fundamentals")
        potential_matches = []
        for topic in track_topics:
            t_id = _get_val(topic, "id")
            t_name = str(_get_val(topic, "name") or "").strip().lower()

            norm_name = re.sub(r"[^a-z0-9]", "", t_name)
            words = [
                w for w in re.split(r"[\s\-_]+", t_name)
                if w
            ]

            if norm_name.startswith(normalized) or clean in words:
                if t_id is not None:
                    potential_matches.append(t_id)

        if len(potential_matches) == 1:
            matched_ids.add(potential_matches[0])

    return matched_ids


def _reschedule_start_date(roadmap):
    created = roadmap.created_at or datetime.utcnow()

    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)

    return created.astimezone().date()


def _flag(value):
    return value is True or str(value).strip().lower() in (
        "1",
        "true",
        "yes"
    )


def _progress_ratio(items, current_day):
    """
    1.0 means exactly on schedule.
    = minutes completed / minutes that were due before today.
    Work done ahead of schedule counts, so the ratio can be above 1.
    """
    due_minutes = sum(
        item.planned_minutes
        for item in items
        if item.day_number < current_day
    )

    done_minutes = sum(
        item.planned_minutes
        for item in items
        if item.status == "completed"
    )

    if due_minutes <= 0:
        return 1.0

    return round(min(done_minutes / due_minutes, 2.0), 3)


def _used_minutes_by_day(items):
    used = {}

    for item in items:
        if item.status == "completed":
            used[item.day_number] = (
                used.get(item.day_number, 0)
                + item.planned_minutes
            )

    return used


def _current_streak(completed_dates, today):
    end_day = today

    if end_day not in completed_dates:
        end_day = today - timedelta(days=1)

    streak = 0

    while end_day in completed_dates:
        streak += 1
        end_day -= timedelta(days=1)

    return streak



def _layout_new_tasks(
    daily_plan,
    first_open_day,
    capacity,
    used_by_day
):
    """
    Lay out ordered tasks across available study days.

    - Rounds fractional daily capacity to the nearest minute.
    - Combines consecutive entries for the same topic.
    - Preserves topic order and completed study time.
    - Avoids creating unnecessary tiny task fragments.
    """
    capacity = max(1, int(round(float(capacity))))

    # Flatten the search plan while merging consecutive entries
    # for the same topic.
    queue = []

    for day in daily_plan:
        for task in day.get("tasks", []):
            topic_id = task.get("topic_id")
            minutes = max(
                0,
                int(round(float(task.get("minutes", 0))))
            )

            if minutes <= 0 or topic_id is None:
                continue

            if queue and queue[-1][0] == topic_id:
                queue[-1] = (
                    topic_id,
                    queue[-1][1] + minutes
                )
            else:
                queue.append((topic_id, minutes))

    placed = []
    day_number = first_open_day
    room = max(
        0,
        capacity - used_by_day.get(day_number, 0)
    )

    for topic_id, original_minutes in queue:
        minutes = original_minutes

        while minutes > 0:
            if room <= 0:
                day_number += 1
                room = max(
                    0,
                    capacity - used_by_day.get(day_number, 0)
                )
                continue

            # If using this remaining space would create a tiny
            # fragment, move the task to the next day instead.
            if minutes > room and room < 5:
                day_number += 1
                room = max(
                    0,
                    capacity - used_by_day.get(day_number, 0)
                )
                continue

            chunk = min(minutes, room)

            placed.append({
                "topic_id": topic_id,
                "day_number": day_number,
                "planned_minutes": chunk
            })

            minutes -= chunk
            room -= chunk

    return placed



def _roadmap_payload(entries, topic_lookup, start_date):
    from routes.resources import get_item_resource

    days = {}

    for entry in entries:
        topic = topic_lookup.get(entry["topic_id"])
        item_id = entry.get("id")
        resource, _ = get_item_resource(item_id, entry["topic_id"]) if item_id else (None, [])

        days.setdefault(entry["day_number"], []).append({
            "id": entry.get("id"),
            "topic_id": entry["topic_id"],
            "name": topic.name if topic else "Unknown topic",
            "minutes": entry["planned_minutes"],
            "status": entry["status"],
            "difficulty": topic.difficulty if topic else None,
            "is_optional": topic.is_optional if topic else False,
            "resource": resource
        })

    return [
        {
            "day": day_number,
            "date": (
                start_date + timedelta(days=day_number - 1)
            ).isoformat(),
            "total_minutes": sum(
                task["minutes"] for task in days[day_number]
            ),
            "tasks": days[day_number]
        }
        for day_number in sorted(days)
    ]


@roadmap_bp.get("/active")
def get_active_roadmap():
    goal_id = request.args.get("goal_id", type=int)

    if not goal_id:
        return jsonify({
            "status": "error",
            "message": "goal_id query parameter is required."
        }), 400

    try:
        goal = db.session.get(Goal, goal_id)

        if goal is None:
            return jsonify({
                "status": "error",
                "message": "Goal not found."
            }), 404

        allowed, msg = check_goal_access(goal)
        if not allowed:
            code = 401 if ("Authentication required" in msg or "token" in msg.lower()) else 403
            return jsonify({
                "status": "error",
                "message": msg
            }), code

        roadmap = Roadmap.query.filter_by(
            goal_id=goal.id,
            status="active"
        ).order_by(
            Roadmap.version_number.desc()
        ).first()

        if roadmap is None:
            return jsonify({
                "status": "error",
                "message": "No active roadmap found for this goal."
            }), 404

        items = RoadmapItem.query.filter_by(
            roadmap_id=roadmap.id
        ).order_by(
            RoadmapItem.day_number,
            RoadmapItem.id
        ).all()

        if not items:
            return jsonify({
                "status": "error",
                "message": "The active roadmap has no tasks."
            }), 404

        topics = Topic.query.filter_by(
            track_id=goal.track_id
        ).all()

        topic_lookup = {
            topic.id: topic
            for topic in topics
        }

        start_date = _reschedule_start_date(roadmap)

        entries = [
            {
                "id": item.id,
                "topic_id": item.topic_id,
                "day_number": item.day_number,
                "planned_minutes": item.planned_minutes,
                "status": item.status
            }
            for item in items
        ]

        daily_plan = _roadmap_payload(entries, topic_lookup, start_date)

        total_planned_minutes = sum(item.planned_minutes for item in items)
        daily_capacity = int(float(goal.study_hours_per_day) * 60)
        total_days = max((item.day_number for item in items), default=len(daily_plan))

        return jsonify({
            "status": "success",
            "message": "Active roadmap loaded successfully.",
            "roadmap_id": roadmap.id,
            "roadmap_version": roadmap.version_number,
            "items_saved": len(items),
            "goal": {
                "id": goal.id,
                "track_id": goal.track_id,
                "skill_level": goal.skill_level,
                "study_hours_per_day": goal.study_hours_per_day,
                "target_date": goal.target_date.strftime("%d/%m/%Y"),
                "known_topics": (
                    goal.known_topics.split(",")
                    if goal.known_topics
                    else []
                )
            },
            "ci": {
                "fuzzy": None,
                "expert": {
                    "selected_strategy": "NO_CHANGE"
                },
                "search": {
                    "success": True,
                    "sequence": [item.topic_id for item in items],
                    "total_minutes": total_planned_minutes,
                    "daily_capacity": daily_capacity,
                    "total_days": total_days,
                    "search_cost": 0.0,
                    "nodes_expanded": 0
                }
            },
            "roadmap": daily_plan
        }), 200

    except Exception as error:
        current_app.logger.exception("Failed to load active roadmap")
        return jsonify({
            "status": "error",
            "message": "Could not load active roadmap.",
            "error": str(error) if current_app.debug else None
        }), 500


@roadmap_bp.post("/reschedule")
def reschedule_roadmap():
    data = request.get_json(silent=True) or {}
    goal_id = data.get("goal_id")

    if not goal_id:
        return jsonify({
            "status": "error",
            "message": "goal_id is required."
        }), 400

    try:
        goal_id = int(goal_id)
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "goal_id must be a valid number."
        }), 400

    preview = _flag(data.get("preview"))
    force = _flag(data.get("force"))
    date_text = data.get("date")

    try:
        today = (
            datetime.strptime(date_text, "%Y-%m-%d").date()
            if date_text
            else date.today()
        )
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "date must look like YYYY-MM-DD."
        }), 400

    try:
        goal = db.session.get(Goal, goal_id)

        if goal is None:
            return jsonify({
                "status": "error",
                "message": "Goal not found."
            }), 404

        allowed, msg = check_goal_access(goal)
        if not allowed:
            code = 401 if ("Authentication required" in msg or "token" in msg.lower()) else 403
            return jsonify({
                "status": "error",
                "message": msg
            }), code

        old_roadmap = Roadmap.query.filter_by(
            goal_id=goal.id,
            status="active"
        ).order_by(
            Roadmap.version_number.desc()
        ).first()

        if old_roadmap is None:
            return jsonify({
                "status": "error",
                "message": "No active roadmap found."
            }), 404

        old_items = RoadmapItem.query.filter_by(
            roadmap_id=old_roadmap.id
        ).order_by(
            RoadmapItem.day_number,
            RoadmapItem.id
        ).all()

        if not old_items:
            return jsonify({
                "status": "error",
                "message": "The active roadmap has no tasks."
            }), 400

        # ---------------- where are we in the plan? ----------------

        start_date = _reschedule_start_date(old_roadmap)
        current_day = (today - start_date).days + 1

        # Skipping something today closes today: new work starts tomorrow.
        skipped_today = any(
            item.status == "skipped"
            and item.day_number == current_day
            for item in old_items
        )

        first_open_day = max(1, current_day) + (
            1 if skipped_today else 0
        )

        backlog_items = [
            item for item in old_items
            if item.status == "skipped"
            or (
                item.day_number < current_day
                and item.status == "pending"
            )
        ]

        progress_ratio = _progress_ratio(old_items, current_day)

        if not backlog_items and not force:
            return jsonify({
                "status": "success",
                "message": (
                    "No skipped or overdue tasks, so the current "
                    "roadmap was kept."
                ),
                "replanned": False,
                "preview": preview,
                "saved": False,
                "goal_id": goal.id,
                "roadmap_id": old_roadmap.id,
                "roadmap_version": old_roadmap.version_number,
                "date": today.isoformat(),
                "current_day": current_day,
                "metrics": {
                    "progress_ratio": progress_ratio
                }
            }), 200

        # ---------------- what work is left? ----------------

        topics = Topic.query.filter_by(
            track_id=goal.track_id
        ).order_by(Topic.id).all()

        topic_lookup = {topic.id: topic for topic in topics}
        items_by_topic = {}

        for item in old_items:
            items_by_topic.setdefault(
                item.topic_id,
                []
            ).append(item)

        completed_topics = set()
        remaining_minutes = {}

        for topic_id, topic_items in items_by_topic.items():
            if all(item.status == "completed" for item in topic_items):
                completed_topics.add(topic_id)

            remaining_minutes[topic_id] = sum(
                item.planned_minutes
                for item in topic_items
                if item.status != "completed"
            )

        # Preserve known topics from the original goal so they are not re-planned
        known_completed = _resolve_known_topics(goal.known_topics, topics)
        completed_topics.update(known_completed)

        topic_ids = set(topic_lookup)

        prerequisite_rows = TopicPrerequisite.query.filter(
            TopicPrerequisite.topic_id.in_(topic_ids),
            TopicPrerequisite.prerequisite_topic_id.in_(topic_ids)
        ).all()

        prerequisites = [
            (row.topic_id, row.prerequisite_topic_id)
            for row in prerequisite_rows
        ]

        # Required topics, plus optional topics already in the roadmap.
        selected_topics = {
            topic.id
            for topic in topics
            if not topic.is_optional or topic.id in items_by_topic
        }

        search_topics = []

        for topic in topics:
            remaining = remaining_minutes.get(topic.id, 0)

            search_topics.append({
                "id": topic.id,
                "name": topic.name,
                "estimated_minutes": (
                    remaining if remaining > 0
                    else topic.estimated_minutes
                ),
                "difficulty": topic.difficulty,
                "priority": topic.priority,
                "is_optional": topic.is_optional
            })

        required_minutes = sum(
            remaining_minutes.get(
                topic_id,
                topic_lookup[topic_id].estimated_minutes
            )
            for topic_id in selected_topics
            if topic_id not in completed_topics
        )

        # ---------------- time available until the deadline ----------------

        base_capacity = max(
            1,
            int(float(goal.study_hours_per_day) * 60)
        )

        used_by_day = _used_minutes_by_day(old_items)

        deadline_day = current_day + (goal.target_date - today).days

        available_minutes = sum(
            max(0, base_capacity - used_by_day.get(day, 0))
            for day in range(first_open_day, deadline_day + 1)
        )

        days_remaining = max(
            1,
            (goal.target_date - today).days + 1
        )

        # ---------------- streak ----------------

        logs = StudyLog.query.filter(
            StudyLog.goal_id == goal.id,
            StudyLog.status == "completed",
            StudyLog.study_date >= start_date,
            StudyLog.study_date <= today
        ).all()

        current_streak = _current_streak(
            {log.study_date for log in logs},
            today
        )

        missed_days = len({
            item.day_number for item in backlog_items
        })

        backlog_minutes = sum(
            item.planned_minutes for item in backlog_items
        )

        # ---------------- Fuzzy -> Expert -> Search ----------------

        result = Rescheduler().evaluate(
            progress_ratio=progress_ratio,
            available_minutes=available_minutes,
            required_minutes=required_minutes,
            missed_days=missed_days,
            backlog_minutes=backlog_minutes,
             optional_topics_remaining=sum(
                1 for topic in topics
                if topic.is_optional
                and topic.id in selected_topics
                and topic.id not in completed_topics
            ),
            current_streak=current_streak,
            recent_replans=max(0, old_roadmap.version_number - 1),
            days_remaining=days_remaining,
            topics=search_topics,
            prerequisites=prerequisites,
            selected_topics=selected_topics,
            completed_topics=completed_topics,
            study_hours_per_day=float(goal.study_hours_per_day),
            apply_strategy=True
        )

        search_result = result.get("search")

        if not search_result or not search_result.get("success"):
            return jsonify({
                "status": "error",
                "message": (
                    search_result.get(
                        "message",
                        "Could not reschedule roadmap."
                    )
                    if search_result
                    else "Search returned no result."
                ),
                "ci": {
                    "fuzzy": result.get("fuzzy"),
                    "expert": result.get("expert"),
                    "adaptation": result.get("adaptation")
                }
            }), 422

        adaptation = result.get("adaptation") or {}
        expert = result.get("expert") or {}

        # ---------------- build the new plan (nothing saved yet) ----------------

        effective_capacity = max(
            1,
            int(round(float(
                search_result.get("daily_capacity", base_capacity)
            )))
        )

        placed = _layout_new_tasks(
            daily_plan=search_result.get("daily_plan", []),
            first_open_day=first_open_day,
            capacity=effective_capacity,
            used_by_day=used_by_day
        )

        if not placed:
            return jsonify({
                "status": "success",
                "message": "There is no remaining work to schedule.",
                "replanned": False,
                "preview": preview,
                "saved": False,
                "goal_id": goal.id,
                "roadmap_id": old_roadmap.id,
                "roadmap_version": old_roadmap.version_number
            }), 200

        entries = []

        for item in old_items:
            if item.status == "completed":
                entries.append({
                    "id": None,
                    "topic_id": item.topic_id,
                    "day_number": item.day_number,
                    "planned_minutes": item.planned_minutes,
                    "status": "completed"
                })

        completed_count = len(entries)

        for task in placed:
            entries.append({
                "id": None,
                "topic_id": task["topic_id"],
                "day_number": task["day_number"],
                "planned_minutes": task["planned_minutes"],
                "status": "pending"
            })

        entries.sort(key=lambda entry: (
            entry["day_number"],
            0 if entry["status"] == "completed" else 1
        ))

        plan_end_day = max(entry["day_number"] for entry in entries)
        plan_end_date = start_date + timedelta(days=plan_end_day - 1)

        old_target = goal.target_date
        new_target = old_target
        warnings = []

        if plan_end_date > old_target:
            if adaptation.get("extend_deadline"):
                new_target = plan_end_date
                warnings.append(
                    "The target date moves to "
                    f"{plan_end_date.strftime('%d/%m/%Y')} so the "
                    "plan fits."
                )
            else:
                warnings.append(
                    "The revised plan ends on "
                    f"{plan_end_date.strftime('%d/%m/%Y')}, after "
                    "your target date "
                    f"{old_target.strftime('%d/%m/%Y')}."
                )

        next_version = (db.session.query(
            db.func.max(Roadmap.version_number)
        ).filter(
            Roadmap.goal_id == goal.id
        ).scalar() or 0) + 1

        response = {
            "status": "success",
            "message": (
                "Preview only: nothing was saved."
                if preview
                else "Adaptive roadmap created successfully."
            ),
            "replanned": True,
            "preview": preview,
            "saved": False,
            "goal_id": goal.id,
            "previous_roadmap_id": old_roadmap.id,
            "previous_roadmap_version": old_roadmap.version_number,
            "roadmap_id": None,
            "roadmap_version": next_version,
            "date": today.isoformat(),
            "current_day": current_day,
            "first_new_day": first_open_day,
            "completed_tasks_preserved": completed_count,
            "tasks_replanned": len(placed),
            "plan_end_date": plan_end_date.isoformat(),
            "target_date": {
                "old": old_target.strftime("%d/%m/%Y"),
                "new": new_target.strftime("%d/%m/%Y"),
                "changed": new_target != old_target
            },
            "strategy": expert.get("selected_strategy"),
            "warnings": warnings,
            "metrics": {
                "progress_ratio": progress_ratio,
                "backlog_minutes": backlog_minutes,
                "missed_days": missed_days,
                "current_streak": current_streak,
                "required_minutes": required_minutes,
                "available_minutes": available_minutes,
                "days_remaining": days_remaining,
                "today_closed": skipped_today
            },
            "ci": {
                "fuzzy": result.get("fuzzy"),
                "expert": expert,
                "adaptation": adaptation,
                "search": {
                    "success": search_result.get("success"),
                    "sequence": search_result.get("sequence", []),
                    "total_minutes": search_result.get(
                        "total_minutes",
                        0
                    ),
                    "daily_capacity": search_result.get(
                        "daily_capacity"
                    ),
                    "search_cost": search_result.get("search_cost"),
                    "nodes_expanded": search_result.get(
                        "nodes_expanded",
                        0
                    )
                }
            },
            "roadmap": _roadmap_payload(
                entries,
                topic_lookup,
                start_date
            )
        }

        if preview:
            return jsonify(response), 200

        # ---------------- save everything in ONE transaction ----------------

        if new_target != old_target:
            goal.target_date = new_target

        old_roadmap.status = "superseded"

        new_roadmap = Roadmap(
            goal_id=goal.id,
            version_number=next_version,
            status="active",
            created_at=old_roadmap.created_at
        )

        db.session.add(new_roadmap)
        db.session.flush()

        new_objects = [
            RoadmapItem(
                roadmap_id=new_roadmap.id,
                topic_id=entry["topic_id"],
                day_number=entry["day_number"],
                planned_minutes=entry["planned_minutes"],
                status=entry["status"]
            )
            for entry in entries
        ]

        db.session.add_all(new_objects)
        db.session.flush()

        for entry, saved_item in zip(entries, new_objects):
            entry["id"] = saved_item.id

        db.session.commit()

        response["saved"] = True
        response["roadmap_id"] = new_roadmap.id
        response["items_saved"] = len(entries)
        response["roadmap"] = _roadmap_payload(
            entries,
            topic_lookup,
            start_date
        )

        return jsonify(response), 200

    except Exception as error:
        db.session.rollback()

        current_app.logger.exception("Reschedule failed")

        body = {
            "status": "error",
            "message": "Could not reschedule roadmap."
        }

        if current_app.debug:
            body["error"] = str(error)

        return jsonify(body), 500