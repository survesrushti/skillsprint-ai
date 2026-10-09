class LearningFacts:

    def __init__(
        self,
        progress_ratio,
        available_minutes,
        required_minutes,
        missed_days=0,
        backlog_minutes=0,
        optional_topics_remaining=0,
        current_streak=0,
        recent_replans=0,
        fuzzy_adjustment=0.0,
        days_remaining=7
    ):
        self.progress_ratio = progress_ratio
        self.available_minutes = available_minutes
        self.required_minutes = required_minutes
        self.missed_days = missed_days
        self.backlog_minutes = backlog_minutes
        self.optional_topics_remaining = optional_topics_remaining
        self.current_streak = current_streak
        self.recent_replans = recent_replans
        self.fuzzy_adjustment = fuzzy_adjustment
        self.days_remaining = days_remaining

    def to_dict(self):
        return {
            "progress_ratio": self.progress_ratio,
            "available_minutes": self.available_minutes,
            "required_minutes": self.required_minutes,
            "missed_days": self.missed_days,
            "backlog_minutes": self.backlog_minutes,
            "optional_topics_remaining": self.optional_topics_remaining,
            "current_streak": self.current_streak,
            "recent_replans": self.recent_replans,
            "fuzzy_adjustment": self.fuzzy_adjustment,
            "days_remaining": self.days_remaining
        }