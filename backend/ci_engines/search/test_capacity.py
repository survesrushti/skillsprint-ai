from capacity import CapacityCalculator


calculator = CapacityCalculator(
    study_hours_per_day=2
)


print("Daily capacity:", calculator.daily_capacity(), "minutes")

print(
    "10-day capacity:",
    calculator.total_capacity(10),
    "minutes"
)

print(
    "Can complete 1000 minutes:",
    calculator.can_complete(1000, 10)
)

print(
    "Can complete 1500 minutes:",
    calculator.can_complete(1500, 10)
)

print(
    "Remaining capacity:",
    calculator.remaining_capacity(1000, 10),
    "minutes"
)