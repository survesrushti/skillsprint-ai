from datetime import date
from types import SimpleNamespace

from routes.roadmap import (
    _current_streak,
    _layout_new_tasks,
    _progress_ratio,
    _used_minutes_by_day,
)


def item(day, minutes, status):
    return SimpleNamespace(
        day_number=day,
        planned_minutes=minutes,
        status=status
    )


def plan(*tasks):
    return [{
        "day": 1,
        "tasks": [
            {"topic_id": topic_id, "minutes": minutes}
            for topic_id, minutes in tasks
        ]
    }]


def test_ratio_is_one_when_nothing_is_due_yet():
    items = [item(1, 120, "pending")]
    assert _progress_ratio(items, current_day=1) == 1.0


def test_ratio_is_one_when_exactly_on_schedule():
    items = [item(1, 120, "completed"), item(2, 120, "pending")]
    assert _progress_ratio(items, current_day=2) == 1.0


def test_ratio_is_zero_when_nothing_done_but_work_was_due():
    items = [item(1, 120, "pending"), item(2, 120, "pending")]
    assert _progress_ratio(items, current_day=3) == 0.0


def test_ratio_counts_work_done_ahead_and_is_capped_at_two():
    items = [
        item(1, 120, "completed"),
        item(2, 120, "completed"),
        item(3, 120, "completed"),
    ]
    assert _progress_ratio(items, current_day=2) == 2.0


def test_used_minutes_counts_only_completed_items():
    items = [
        item(3, 60, "completed"),
        item(3, 30, "completed"),
        item(3, 90, "skipped"),
        item(4, 50, "pending"),
    ]
    assert _used_minutes_by_day(items) == {3: 90}


def test_layout_leaves_room_for_work_already_done_that_day():
    placed = _layout_new_tasks(
        plan((10, 120)),
        first_open_day=3,
        capacity=120,
        used_by_day={3: 60}
    )

    assert [(p["day_number"], p["planned_minutes"]) for p in placed] == [
        (3, 60),
        (4, 60),
    ]


def test_layout_skips_days_that_are_already_full():
    placed = _layout_new_tasks(
        plan((10, 60)),
        first_open_day=3,
        capacity=120,
        used_by_day={3: 120}
    )

    assert placed[0]["day_number"] == 4


def test_layout_keeps_order_and_never_exceeds_capacity():
    placed = _layout_new_tasks(
        plan((1, 100), (2, 100), (3, 100)),
        first_open_day=5,
        capacity=120,
        used_by_day={}
    )

    assert [p["topic_id"] for p in placed] == [1, 2, 2, 3, 3]
    assert [p["day_number"] for p in placed] == [5, 5, 6, 6, 7]

    per_day = {}
    for p in placed:
        per_day[p["day_number"]] = (
            per_day.get(p["day_number"], 0) + p["planned_minutes"]
        )

    assert all(total <= 120 for total in per_day.values())
    assert sum(per_day.values()) == 300


def test_streak_counts_consecutive_days_ending_today_or_yesterday():
    dates = {date(2026, 10, 8), date(2026, 10, 9), date(2026, 10, 10)}

    assert _current_streak(dates, date(2026, 10, 10)) == 3
    assert _current_streak(dates, date(2026, 10, 11)) == 3
    assert _current_streak(dates, date(2026, 10, 12)) == 0
