from variables import FuzzyVariables


fuzzy = FuzzyVariables()


print("Time Availability = 0.3")
print(
    fuzzy.time_availability(0.3)
)

print()

print("Progress = 1.0")
print(
    fuzzy.progress(1.0)
)

print()

print("Progress = 1.7")
print(
    fuzzy.progress(1.7)
)

print()

print("Workload Adjustment = 0.15")
print(
    fuzzy.workload_adjustment(0.15)
)