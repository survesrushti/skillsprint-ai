from rules import (
    get_rules,
    get_rule
)


rules = get_rules()


print("Total rules:", len(rules))

print()

print(
    "Scarce + Behind:",
    get_rule("Scarce", "Behind")
)

print(
    "Scarce + OnTrack:",
    get_rule("Scarce", "OnTrack")
)

print(
    "Adequate + Ahead:",
    get_rule("Adequate", "Ahead")
)

print(
    "Ample + Ahead:",
    get_rule("Ample", "Ahead")
)

print()

print("All fuzzy rules:")

for index, rule in enumerate(rules, start=1):
    print(
        f"Rule {index}: "
        f"IF Time is {rule['time']} "
        f"AND Progress is {rule['progress']} "
        f"THEN Adjustment is {rule['output']}"
    )