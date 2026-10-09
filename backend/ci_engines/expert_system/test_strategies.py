from strategies import (
    get_strategy,
    get_all_strategies
)


print("Available strategies:")
print("=====================")

for strategy_id, strategy in get_all_strategies().items():
    print(
        f"{strategy_id}: "
        f"{strategy['name']}"
    )

print()

print("Selected strategy:")

strategy = get_strategy("COMPRESS")

print(
    f"Name: {strategy['name']}"
)

print(
    f"Description: {strategy['description']}"
)