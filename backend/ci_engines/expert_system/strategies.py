STRATEGIES = {
    "NO_CHANGE": {
        "name": "No Change",
        "description": "Keep the current learning roadmap unchanged."
    },
    "REDISTRIBUTE": {
        "name": "Redistribute",
        "description": "Redistribute pending tasks across the remaining study days."
    },
    "COMPRESS": {
        "name": "Compress",
        "description": "Increase the workload to recover from a backlog."
    },
    "DEFER_OPTIONAL": {
        "name": "Defer Optional",
        "description": "Move optional topics later to protect important topics."
    },
    "EXTEND_DEADLINE": {
        "name": "Extend Deadline",
        "description": "Extend the target date when the remaining workload is not safely achievable."
    },
    "RELAX": {
        "name": "Relax",
        "description": "Reduce workload when the learner is ahead or has excess capacity."
    }
}


def get_strategy(strategy_id):
    return STRATEGIES.get(strategy_id)


def get_all_strategies():
    return STRATEGIES.copy()