class CapacityCalculator:
    def __init__(self, study_hours_per_day):
        self.study_hours_per_day = study_hours_per_day
        self.minutes_per_day = study_hours_per_day * 60

    def daily_capacity(self):
        return self.minutes_per_day

    def total_capacity(self, number_of_days):
        return self.minutes_per_day * number_of_days

    def can_complete(self, required_minutes, number_of_days):
        available_minutes = self.total_capacity(number_of_days)

        return required_minutes <= available_minutes

    def remaining_capacity(self, required_minutes, number_of_days):
        available_minutes = self.total_capacity(number_of_days)

        return available_minutes - required_minutes