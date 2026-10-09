from rules import (
    get_rules,
    get_rules_by_priority
)


rules = get_rules()

print("Total expert rules:", len(rules))

print()

print("Rules by priority:")
print("===================")

for rule in get_rules_by_priority():
    print(
        f"{rule['id']} | "
        f"Priority: {rule['priority']} | "
        f"{rule['condition']} -> "
        f"{rule['strategy']}"
    )

print()

print("Highest priority rule:")

highest = get_rules_by_priority()[0]

print(
    f"{highest['id']}: "
    f"{highest['condition']} -> "
    f"{highest['strategy']}"
)

print(
    f"Reason: {highest['reason']}"
)