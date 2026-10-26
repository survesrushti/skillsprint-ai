from ci_engines.rescheduler.engine import Rescheduler


TOPICS = [
    {"id": 1, "name": "HTML", "estimated_minutes": 120,
     "difficulty": 1, "priority": 1.0, "is_optional": False},
    {"id": 2, "name": "CSS", "estimated_minutes": 120,
     "difficulty": 2, "priority": 1.0, "is_optional": False},
    {"id": 3, "name": "Bonus", "estimated_minutes": 60,
     "difficulty": 1, "priority": 0.5, "is_optional": True},
    {"id": 4, "name": "JavaScript", "estimated_minutes": 120,
     "difficulty": 3, "priority": 1.0, "is_optional": False},
]

# (topic_id, prerequisite_topic_id)
PREREQUISITES = [(2, 1), (4, 2)]


class StubExpert:
    def __init__(self, strategy):
        self.strategy = strategy

    def evaluate(self, facts):
        return {
            "facts": facts.to_dict(),
            "selected_strategy": self.strategy,
            "fired_rules": [],
        }


def run(strategy=None, apply_strategy=True, **overrides):
    rescheduler = Rescheduler()

    if strategy is not None:
        rescheduler.expert_system = StubExpert(strategy)

    settings = dict(
        progress_ratio=1.0,
        available_minutes=1000,
        required_minutes=420,
        missed_days=1,
        backlog_minutes=120,
        optional_topics_remaining=1,
        days_remaining=10,
        topics=TOPICS,
        prerequisites=PREREQUISITES,
        selected_topics={1, 2, 3, 4},
        completed_topics=set(),
        study_hours_per_day=2,
        apply_strategy=apply_strategy,
    )
    settings.update(overrides)

    return rescheduler.evaluate(**settings)


def test_switch_off_keeps_original_behaviour():
    result = run(strategy="COMPRESS", apply_strategy=False)

    assert result["adaptation"] is None
    assert result["search"]["success"] is True
    assert result["search"]["daily_capacity"] == 120


def test_compress_raises_daily_capacity():
    result = run(strategy="COMPRESS")

    assert 1.05 <= result["adaptation"]["capacity_factor"] <= 1.40
    assert result["search"]["daily_capacity"] > 120


def test_relax_lowers_capacity_but_not_below_what_deadline_needs():
    result = run(
        strategy="RELAX",
        progress_ratio=1.5,
        available_minutes=3000,
        required_minutes=420,
    )

    factor = result["adaptation"]["capacity_factor"]
    assert 0.7 <= factor <= 1.0

    tight = run(
        strategy="RELAX",
        progress_ratio=1.5,
        available_minutes=450,
        required_minutes=420,
    )

    assert tight["adaptation"]["capacity_factor"] >= 0.95


def test_extend_deadline_keeps_pace_and_sets_flag():
    result = run(strategy="EXTEND_DEADLINE")

    assert result["adaptation"]["extend_deadline"] is True
    assert result["search"]["daily_capacity"] == 120


def test_defer_optional_puts_optional_topic_last():
    result = run(strategy="DEFER_OPTIONAL")
    sequence = result["search"]["sequence"]

    assert set(sequence) == {1, 2, 3, 4}
    assert sequence[-1] == 3
    assert sequence.index(1) < sequence.index(2) < sequence.index(4)
    assert result["adaptation"]["deferred_topic_ids"] == [3]


def test_completed_topics_are_not_planned_again():
    result = run(
        strategy="REDISTRIBUTE",
        selected_topics={1, 2, 4},
        completed_topics={1},
    )

    assert result["search"]["sequence"] == [2, 4]


def test_partial_topic_uses_remaining_minutes_only():
    topics = [dict(topic) for topic in TOPICS]
    topics[1]["estimated_minutes"] = 45

    result = run(
        strategy="REDISTRIBUTE",
        topics=topics,
        selected_topics={1, 2, 4},
        completed_topics={1},
    )

    css_minutes = sum(
        task["minutes"]
        for day in result["search"]["daily_plan"]
        for task in day["tasks"]
        if task["topic_id"] == 2
    )

    assert css_minutes == 45