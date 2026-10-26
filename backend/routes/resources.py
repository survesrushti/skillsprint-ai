from flask import Blueprint, jsonify, request

from extensions import db
from models import Resource, Topic, RoadmapItem, Roadmap, Goal
from middleware.auth import check_goal_access


resources_bp = Blueprint(
    "resources",
    __name__,
    url_prefix="/api/v1"
)

# In-memory storage for user-selected resource overrides per roadmap item
_ITEM_RESOURCE_SELECTION = {}

# Curated alternative learning resources by topic slug / keyword
# Guarantees that every topic has rich, high-quality alternatives (documentation, courses, interactive guides)
CURATED_ALTERNATIVES = {
    "html-fundamentals": [
        {
            "id": 101,
            "title": "freeCodeCamp Responsive Web Design HTML Tutorial",
            "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
            "resource_type": "interactive course",
            "estimated_minutes": 180,
        },
        {
            "id": 102,
            "title": "W3Schools HTML5 Comprehensive Guide",
            "url": "https://www.w3schools.com/html/",
            "resource_type": "reference",
            "estimated_minutes": 120,
        },
    ],
    "css-fundamentals": [
        {
            "id": 201,
            "title": "CSS-Tricks: Complete Guide to Flexbox & Grid",
            "url": "https://css-tricks.com/snippets/css/a-guide-to-flexbox/",
            "resource_type": "guide",
            "estimated_minutes": 150,
        },
        {
            "id": 202,
            "title": "Kevin Powell CSS Masterclass on YouTube",
            "url": "https://www.youtube.com/@KevinPowell",
            "resource_type": "video",
            "estimated_minutes": 200,
        },
    ],
    "javascript-fundamentals": [
        {
            "id": 301,
            "title": "JavaScript.info: The Modern JavaScript Tutorial",
            "url": "https://javascript.info/",
            "resource_type": "tutorial",
            "estimated_minutes": 240,
        },
        {
            "id": 302,
            "title": "Eloquent JavaScript (Interactive Digital Book)",
            "url": "https://eloquentjavascript.net/",
            "resource_type": "book",
            "estimated_minutes": 300,
        },
    ],
    "git-and-github": [
        {
            "id": 401,
            "title": "Pro Git Book (Official Free Edition)",
            "url": "https://git-scm.com/book/en/v2",
            "resource_type": "book",
            "estimated_minutes": 180,
        },
        {
            "id": 402,
            "title": "Git Immersion - Hands-on Guided Tour",
            "url": "https://gitimmersion.com/",
            "resource_type": "interactive guide",
            "estimated_minutes": 120,
        },
    ],
    "react-fundamentals": [
        {
            "id": 501,
            "title": "Scrimba: Interactive Learn React Course",
            "url": "https://scrimba.com/learn/learnreact",
            "resource_type": "interactive course",
            "estimated_minutes": 300,
        },
        {
            "id": 502,
            "title": "Codevolution React & TypeScript Playlist",
            "url": "https://www.youtube.com/@Codevolution",
            "resource_type": "video",
            "estimated_minutes": 240,
        },
    ],
    "backend-with-flask": [
        {
            "id": 601,
            "title": "Corey Schafer: Python Flask Series",
            "url": "https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgVECeBE8BI",
            "resource_type": "video series",
            "estimated_minutes": 300,
        },
        {
            "id": 602,
            "title": "The Flask Mega-Tutorial by Miguel Grinberg",
            "url": "https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world",
            "resource_type": "tutorial",
            "estimated_minutes": 360,
        },
    ],
    "sql-and-databases": [
        {
            "id": 701,
            "title": "SQLBolt: Learn SQL with Interactive Exercises",
            "url": "https://sqlbolt.com/",
            "resource_type": "interactive course",
            "estimated_minutes": 180,
        },
        {
            "id": 702,
            "title": "Mode Analytics SQL Tutorial for Beginners",
            "url": "https://mode.com/sql-tutorial/",
            "resource_type": "tutorial",
            "estimated_minutes": 240,
        },
    ],
    "python-fundamentals": [
        {
            "id": 1001,
            "title": "Automate the Boring Stuff with Python",
            "url": "https://automatetheboringstuff.com/",
            "resource_type": "book",
            "estimated_minutes": 300,
        },
        {
            "id": 1002,
            "title": "Corey Schafer: Python OOP & Core Fundamentals",
            "url": "https://www.youtube.com/playlist?list=PL-osiE80TeTskrapid348esswvmF3G765",
            "resource_type": "video",
            "estimated_minutes": 240,
        },
    ],
    "numpy-fundamentals": [
        {
            "id": 1101,
            "title": "NumPy Illustrated: Visual Guide to NumPy",
            "url": "https://betterprogramming.pub/numpy-illustrated-the-visually-stunning-guide-to-data-manipulation-in-python-9ec01124613b",
            "resource_type": "visual guide",
            "estimated_minutes": 120,
        },
        {
            "id": 1102,
            "title": "Keith Galli: Complete Python NumPy Tutorial",
            "url": "https://www.youtube.com/watch?v=GB9BytXXCVE",
            "resource_type": "video",
            "estimated_minutes": 90,
        },
    ],
    "pandas-fundamentals": [
        {
            "id": 1201,
            "title": "10 Minutes to Pandas - Official Guide",
            "url": "https://pandas.pydata.org/docs/user_guide/10min.html",
            "resource_type": "guide",
            "estimated_minutes": 120,
        },
        {
            "id": 1202,
            "title": "Data School: Python Pandas Video Series",
            "url": "https://www.youtube.com/playlist?list=PL5-da3qGB5ICCsgW1MxlZ0Hq8834KeUuL",
            "resource_type": "video series",
            "estimated_minutes": 240,
        },
    ],
    "data-visualization": [
        {
            "id": 1501,
            "title": "Seaborn: Statistical Data Visualization Tutorial",
            "url": "https://seaborn.pydata.org/tutorial.html",
            "resource_type": "documentation",
            "estimated_minutes": 150,
        },
        {
            "id": 1502,
            "title": "Matplotlib: Visualization with Python",
            "url": "https://matplotlib.org/stable/tutorials/index.html",
            "resource_type": "tutorial",
            "estimated_minutes": 150,
        },
    ],
    "statistics-for-data-analysis": [
        {
            "id": 1401,
            "title": "StatQuest with Josh Starmer: Statistics Fundamentals",
            "url": "https://statquest.org/video-index/",
            "resource_type": "video series",
            "estimated_minutes": 240,
        },
        {
            "id": 1402,
            "title": "OpenIntro Statistics (Free Textbook & Exercises)",
            "url": "https://www.openintro.org/book/os/",
            "resource_type": "book",
            "estimated_minutes": 300,
        },
    ],
    "introduction-to-ui-ux": [
        {
            "id": 1901,
            "title": "Laws of UX: Psychology in Design",
            "url": "https://lawsofux.com/",
            "resource_type": "interactive guide",
            "estimated_minutes": 120,
        },
        {
            "id": 1902,
            "title": "Interaction Design Foundation: What is UX?",
            "url": "https://www.interaction-design.org/literature/topics/ux-design",
            "resource_type": "article",
            "estimated_minutes": 90,
        },
    ],
    "user-research": [
        {
            "id": 2001,
            "title": "Interaction Design Foundation: User Research Basics",
            "url": "https://www.interaction-design.org/literature/topics/user-research",
            "resource_type": "guide",
            "estimated_minutes": 150,
        },
        {
            "id": 2002,
            "title": "GV (Google Ventures) Guide to Research Sprints",
            "url": "https://library.gv.com/the-gv-research-sprint-a-4-day-process-for-answering-critical-questions-408f654b0949",
            "resource_type": "case study",
            "estimated_minutes": 120,
        },
    ],
    "wireframing": [
        {
            "id": 2201,
            "title": "Balsamiq Wireframing Academy",
            "url": "https://balsamiq.com/learn/",
            "resource_type": "tutorial",
            "estimated_minutes": 150,
        },
        {
            "id": 2202,
            "title": "CareerFoundry: Beginner's Guide to Wireframing",
            "url": "https://careerfoundry.com/en/blog/ui-design/how-to-wireframe/",
            "resource_type": "guide",
            "estimated_minutes": 90,
        },
    ],
    "visual-design": [
        {
            "id": 2301,
            "title": "Refactoring UI: Design Tips for Developers",
            "url": "https://www.refactoringui.com/",
            "resource_type": "book & tips",
            "estimated_minutes": 180,
        },
        {
            "id": 2302,
            "title": "Apple Human Interface Guidelines",
            "url": "https://developer.apple.com/design/human-interface-guidelines",
            "resource_type": "design system",
            "estimated_minutes": 180,
        },
    ],
    "prototyping": [
        {
            "id": 2501,
            "title": "Framer Interactive Prototyping Tutorial",
            "url": "https://www.framer.com/academy/",
            "resource_type": "interactive guide",
            "estimated_minutes": 180,
        },
        {
            "id": 2502,
            "title": "InVision: Principles of Prototyping",
            "url": "https://www.invisionapp.com/inside-design/principles-of-prototyping/",
            "resource_type": "article",
            "estimated_minutes": 90,
        },
    ],
}


def _serialize_resource(resource):
    return {
        "id": resource.id,
        "topic_id": resource.topic_id,
        "title": resource.title,
        "url": resource.url,
        "resource_type": resource.resource_type or "documentation",
        "estimated_minutes": resource.estimated_minutes,
    }


def get_topic_resources_list(topic_id):
    """
    Returns all resources available for a given topic ID,
    including database records and curated high-quality alternatives.
    """
    resources = []
    seen_urls = set()

    # 1. Fetch DB resources
    db_resources = Resource.query.filter_by(topic_id=topic_id).all()
    for r in db_resources:
        if r.url not in seen_urls:
            seen_urls.add(r.url)
            resources.append(_serialize_resource(r))

    # 2. Add curated alternatives by topic slug if available
    topic = db.session.get(Topic, topic_id)
    if topic and topic.slug in CURATED_ALTERNATIVES:
        for alt in CURATED_ALTERNATIVES[topic.slug]:
            if alt["url"] not in seen_urls:
                seen_urls.add(alt["url"])
                resources.append({
                    "id": alt["id"],
                    "topic_id": topic_id,
                    "title": alt["title"],
                    "url": alt["url"],
                    "resource_type": alt["resource_type"],
                    "estimated_minutes": alt.get("estimated_minutes"),
                })

    # 3. Fallback generic documentation if empty
    if not resources and topic:
        fallback = {
            "id": 9000 + topic_id,
            "topic_id": topic_id,
            "title": f"{topic.name} Reference",
            "url": f"https://www.google.com/search?q={topic.name.replace(' ', '+')}+tutorial",
            "resource_type": "tutorial",
            "estimated_minutes": topic.estimated_minutes,
        }
        resources.append(fallback)

    return resources


def get_item_resource(item_id, topic_id):
    """
    Returns (selected_resource, available_resources) for a task / roadmap item.
    """
    available = get_topic_resources_list(topic_id)
    
    if item_id and item_id in _ITEM_RESOURCE_SELECTION:
        override = _ITEM_RESOURCE_SELECTION[item_id]
        # Match override if in available
        for res in available:
            if res.get("id") == override.get("id") or res.get("url") == override.get("url"):
                return res, available
        return override, available

    selected = available[0] if available else None
    return selected, available


@resources_bp.get("/topics/<int:topic_id>/resources")
def get_topic_resources(topic_id):
    topic = db.session.get(Topic, topic_id)
    if topic is None:
        return jsonify({
            "status": "error",
            "message": f"Topic with ID {topic_id} not found."
        }), 404

    resources = get_topic_resources_list(topic_id)

    return jsonify({
        "status": "success",
        "topic_id": topic_id,
        "topic_name": topic.name,
        "count": len(resources),
        "resources": resources,
    }), 200


@resources_bp.get("/resources")
def list_resources():
    topic_id = request.args.get("topic_id", type=int)

    if topic_id:
        topic = db.session.get(Topic, topic_id)
        if topic is None:
            return jsonify({
                "status": "error",
                "message": f"Topic with ID {topic_id} not found."
            }), 404
        resources = get_topic_resources_list(topic_id)
    else:
        db_resources = Resource.query.all()
        resources = [_serialize_resource(r) for r in db_resources]

    return jsonify({
        "status": "success",
        "count": len(resources),
        "resources": resources,
    }), 200


@resources_bp.get("/resources/<int:resource_id>")
def get_resource(resource_id):
    res = db.session.get(Resource, resource_id)
    if res:
        return jsonify({
            "status": "success",
            "resource": _serialize_resource(res),
        }), 200

    # Check curated pool
    for topic_slug, alts in CURATED_ALTERNATIVES.items():
        for alt in alts:
            if alt["id"] == resource_id:
                return jsonify({
                    "status": "success",
                    "resource": alt,
                }), 200

    return jsonify({
        "status": "error",
        "message": f"Resource with ID {resource_id} not found."
    }), 404


@resources_bp.put("/roadmap-items/<int:item_id>/resource")
@resources_bp.put("/tasks/<int:item_id>/resource")
def swap_item_resource(item_id):
    item = db.session.get(RoadmapItem, item_id)
    if item is None:
        return jsonify({
            "status": "error",
            "message": f"Roadmap item with ID {item_id} not found."
        }), 404

    roadmap = db.session.get(Roadmap, item.roadmap_id)
    if roadmap is None:
        return jsonify({
            "status": "error",
            "message": "Associated roadmap not found."
        }), 404

    goal = db.session.get(Goal, roadmap.goal_id)
    if goal is None:
        return jsonify({
            "status": "error",
            "message": "Associated goal not found."
        }), 404

    allowed, msg = check_goal_access(goal)
    if not allowed:
        code = 401 if ("Authentication required" in msg or "token" in msg.lower()) else 403
        return jsonify({
            "status": "error",
            "message": msg
        }), code

    payload = request.get_json(silent=True) or {}
    resource_id = payload.get("resource_id")
    target_url = payload.get("url")

    available = get_topic_resources_list(item.topic_id)
    selected = None

    if resource_id:
        for r in available:
            if r.get("id") == resource_id:
                selected = r
                break
    elif target_url:
        for r in available:
            if r.get("url") == target_url:
                selected = r
                break

    if selected is None:
        # If specific resource ID was requested but not found in available list for this topic
        if resource_id:
            # Check if it exists in DB for this topic
            db_res = db.session.get(Resource, resource_id)
            if db_res and db_res.topic_id == item.topic_id:
                selected = _serialize_resource(db_res)
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Resource {resource_id} is not valid for topic {item.topic_id}."
                }), 400
        else:
            return jsonify({
                "status": "error",
                "message": "resource_id or url is required."
            }), 400

    _ITEM_RESOURCE_SELECTION[item_id] = selected

    return jsonify({
        "status": "success",
        "message": "Resource swapped successfully.",
        "item_id": item_id,
        "resource": selected,
    }), 200

