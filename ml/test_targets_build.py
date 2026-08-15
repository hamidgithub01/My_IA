from ml.targets.build import (
    build_target_dataset,
    validate_target_dataset,
    get_target_names,
)


print()
print('========== TARGET DATASET TEST ==========')
print()

dataset = build_target_dataset()

print(f'Total rows: {len(dataset)}')

if not dataset:
    print()
    print('No target data available.')
    raise SystemExit


# =========================================================
# STRUCTURE VALIDATION
# =========================================================

validate_target_dataset(dataset)

print('Target dataset structure: VALID')


# =========================================================
# TARGET COUNT
# =========================================================

actual_target_count = len(dataset[0]) - 1
expected_target_count = len(get_target_names())

print()
print('========== TARGET COUNT ==========')
print()

print(f'Actual targets:   {actual_target_count}')
print(f'Expected targets: {expected_target_count}')

if actual_target_count != expected_target_count:
    raise AssertionError(
        'Target count mismatch.'
    )


# =========================================================
# DATE RANGE
# =========================================================

print()
print('========== DATE RANGE ==========')
print()

print(f"From: {dataset[0]['Date']}")
print(f"To:   {dataset[-1]['Date']}")


# =========================================================
# FIRST ROW
# =========================================================

print()
print('========== FIRST TARGET ROW ==========')
print()

for key, value in dataset[0].items():
    print(f'{key}: {value}')


# =========================================================
# LAST ROW
# =========================================================

print()
print('========== LAST TARGET ROW ==========')
print()

for key, value in dataset[-1].items():
    print(f'{key}: {value}')


# =========================================================
# PASSED
# =========================================================

print()
print('========== TARGET DATASET TEST PASSED ==========')