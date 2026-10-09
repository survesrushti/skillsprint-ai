EXPERT_RULES = [
    {
        "id": "R1",
        "condition": "critical_deadline",
        "strategy": "EXTEND_DEADLINE",
        "priority": 100,
        "reason": "The remaining workload cannot safely fit within the available time."
    },
    {
        "id": "R2",
        "condition": "severe_backlog",
        "strategy": "COMPRESS",
        "priority": 90,
        "reason": "A large backlog requires additional workload to recover."
    },
    {
        "id": "R3",
        "condition": "behind_and_missed",
        "strategy": "COMPRESS",
        "priority": 80,
        "reason": "The learner is behind and has missed study sessions."
    },
    {
        "id": "R4",
        "condition": "behind",
        "strategy": "REDISTRIBUTE",
        "priority": 70,
        "reason": "The learner is behind schedule, so remaining tasks should be redistributed."
    },
    {
        "id": "R5",
        "condition": "fuzzy_large_increase",
        "strategy": "COMPRESS",
        "priority": 65,
        "reason": "Fuzzy Logic recommends a significant workload increase."
    },
    {
        "id": "R6",
        "condition": "optional_topics_and_backlog",
        "strategy": "DEFER_OPTIONAL",
        "priority": 60,
        "reason": "Optional topics can be deferred to protect important learning tasks."
    },
    {
        "id": "R7",
        "condition": "long_absence",
        "strategy": "REDISTRIBUTE",
        "priority": 55,
        "reason": "A long absence requires the remaining tasks to be redistributed."
    },
    {
        "id": "R8",
        "condition": "ahead",
        "strategy": "RELAX",
        "priority": 50,
        "reason": "The learner is ahead of the expected progress."
    },
    {
        "id": "R9",
        "condition": "high_streak",
        "strategy": "NO_CHANGE",
        "priority": 40,
        "reason": "The learner has maintained a strong study streak."
    },
    {
        "id": "R10",
        "condition": "recent_replans",
        "strategy": "RELAX",
        "priority": 35,
        "reason": "Repeated replanning suggests that another aggressive change should be avoided."
    },
    {
        "id": "R11",
        "condition": "ample_capacity",
        "strategy": "RELAX",
        "priority": 30,
        "reason": "Available study capacity is comfortably above the remaining requirement."
    },
    {
        "id": "R12",
        "condition": "on_track",
        "strategy": "NO_CHANGE",
        "priority": 20,
        "reason": "The learner is progressing according to the expected schedule."
    },
    {
        "id": "R13",
        "condition": "no_missed_sessions",
        "strategy": "NO_CHANGE",
        "priority": 10,
        "reason": "There are no missed sessions requiring corrective action."
    },
    {
        "id": "R14",
        "condition": "default",
        "strategy": "NO_CHANGE",
        "priority": 0,
        "reason": "No stronger rule was triggered, so the current roadmap is retained."
    }
]


def get_rules():
    return EXPERT_RULES.copy()


def get_rules_by_priority():
    return sorted(
        EXPERT_RULES,
        key=lambda rule: rule["priority"],
        reverse=True
    )