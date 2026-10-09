from engine import FuzzyEngine


engine = FuzzyEngine()


result = engine.calculate(
    time_availability_ratio=0.3,
    progress_ratio=0.6
)


print("Time availability ratio:")
print(result["time_availability_ratio"])

print()

print("Progress ratio:")
print(result["progress_ratio"])

print()

print("Time memberships:")
print(result["time_memberships"])

print()

print("Progress memberships:")
print(result["progress_memberships"])

print()

print("Output strengths:")

for output, strength in result["output_strengths"].items():
    print(
        f"{output}: {strength:.3f}"
    )

print()

print("Crisp workload adjustment:")
print(
    f"{result['crisp_adjustment']:.4f}"
)

print()

print("Workload adjustment percentage:")
print(
    f"{result['crisp_adjustment'] * 100:.2f}%"
)