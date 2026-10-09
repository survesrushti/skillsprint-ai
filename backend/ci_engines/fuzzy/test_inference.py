from variables import FuzzyVariables
from rules import get_rules
from inference import MamdaniInference


fuzzy = FuzzyVariables()

time_memberships = fuzzy.time_availability(0.3)

progress_memberships = fuzzy.progress(0.6)

inference = MamdaniInference(
    rules=get_rules()
)

result = inference.evaluate(
    time_memberships=time_memberships,
    progress_memberships=progress_memberships
)


print("Time memberships:")
print(time_memberships)

print()

print("Progress memberships:")
print(progress_memberships)

print()

print("Rule firing strengths:")

for rule in result["fired_rules"]:
    print(
        f"Rule {rule['rule_number']}: "
        f"{rule['time']} + {rule['progress']} "
        f"-> {rule['output']} "
        f"= {rule['firing_strength']:.3f}"
    )

print()

print("Final output strengths:")

for output, strength in result["output_strengths"].items():
    print(
        f"{output}: {strength:.3f}"
    )