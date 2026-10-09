FUZZY_RULES = [
    {
        "time": "Scarce",
        "progress": "Behind",
        "output": "LargeIncrease"
    },
    {
        "time": "Scarce",
        "progress": "OnTrack",
        "output": "SmallIncrease"
    },
    {
        "time": "Scarce",
        "progress": "Ahead",
        "output": "NoChange"
    },
    {
        "time": "Adequate",
        "progress": "Behind",
        "output": "SmallIncrease"
    },
    {
        "time": "Adequate",
        "progress": "OnTrack",
        "output": "NoChange"
    },
    {
        "time": "Adequate",
        "progress": "Ahead",
        "output": "SmallDecrease"
    },
    {
        "time": "Ample",
        "progress": "Behind",
        "output": "NoChange"
    },
    {
        "time": "Ample",
        "progress": "OnTrack",
        "output": "SmallDecrease"
    },
    {
        "time": "Ample",
        "progress": "Ahead",
        "output": "LargeDecrease"
    }
]


def get_rules():
    return FUZZY_RULES.copy()


def get_rule(
    time_category,
    progress_category
):
    for rule in FUZZY_RULES:
        if (
            rule["time"] == time_category
            and
            rule["progress"] == progress_category
        ):
            return rule

    return None