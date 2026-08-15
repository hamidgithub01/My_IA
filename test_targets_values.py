from math import isnan

from ml.targets.build import (
    build_target_dataset,
)


print()
print('========== TARGET VALUES TEST ==========')
print()

dataset = build_target_dataset()

if not dataset:
    print('No target data available.')
    raise SystemExit


# =========================================================
# HELPERS
# =========================================================

def is_missing(value):
    """
    Return True when a target value is missing.
    """

    if value is None:
        return True

    if isinstance(value, float):
        return isnan(value)

    return False


def assert_equal(
    actual,
    expected,
    description,
):
    """
    Assert that two values are equal.
    """

    if actual != expected:
        raise AssertionError(
            f'{description}\n'
            f'Expected: {expected}\n'
            f'Actual:   {actual}'
        )


# =========================================================
# BASIC DATASET CHECK
# =========================================================

print('Dataset loaded successfully.')
print(f'Total rows: {len(dataset)}')


# =========================================================
# DATE ORDER
# =========================================================

print()
print('========== DATE ORDER ==========')
print()

dates = [
    row['Date']
    for row in dataset
]

if dates != sorted(dates):
    raise AssertionError(
        'Target dataset is not chronologically ordered.'
    )

print('Date order: VALID')


# =========================================================
# TEST 1 — T+1 EXPENSE
# =========================================================

print()
print('========== TEST 1: T+1 EXPENSE ==========')
print()

row = dataset[0]

value = row[
    'Target_Expense_Total_1D'
]

print(
    f"Date: {row['Date']}"
)

print(
    f'Target_Expense_Total_1D: {value}'
)

print('T+1 expense target generated successfully.')


# =========================================================
# TEST 2 — T+5 LOCATION
# =========================================================

print()
print('========== TEST 2: T+5 LOCATION ==========')
print()

value = row[
    'Target_Location_5D'
]

print(
    f"Date: {row['Date']}"
)

print(
    f'Target_Location_5D: {value}'
)

if value is None:
    print(
        'T+5 location is missing.'
    )
else:
    print(
        'T+5 location value exists.'
    )


# =========================================================
# TEST 3 — T+5 EVENT
# =========================================================

print()
print('========== TEST 3: T+5 EVENT ==========')
print()

value = row[
    'Target_Has_Event_5D'
]

print(
    f'Target_Has_Event_5D: {value}'
)

if value not in (0, 1):
    raise AssertionError(
        'Target_Has_Event_5D must be 0 or 1.'
    )

print(
    'T+5 event target: VALID'
)


# =========================================================
# TEST 4 — T+5 SOCIAL ACTIVITY
# =========================================================

print()
print(
    '========== TEST 4: T+5 SOCIAL ACTIVITY =========='
)
print()

value = row[
    'Target_High_Social_Activity_5D'
]

print(
    f'Target_High_Social_Activity_5D: {value}'
)

if value not in (0, 1):
    raise AssertionError(
        'Target_High_Social_Activity_5D '
        'must be 0 or 1.'
    )

print(
    'T+5 social activity target: VALID'
)


# =========================================================
# TEST 5 — PERIOD TARGET MUST BE MISSING
# =========================================================

print()
print(
    '========== TEST 5: INCOMPLETE FUTURE PERIOD =========='
)
print()

period_targets = [
    'Target_Expense_Total_8_15D',
    'Target_Expense_Total_16_30D',
    'Target_Expense_Total_30D',
]

for target_name in period_targets:

    value = row[target_name]

    print(
        f'{target_name}: {value}'
    )

    if not is_missing(value):
        raise AssertionError(
            f'{target_name} should be missing '
            'because the complete future period '
            'does not exist.'
        )

print(
    'Incomplete future periods: VALID'
)


# =========================================================
# TEST 6 — TARGET VALUES MUST NOT BE NEGATIVE
# =========================================================

print()
print(
    '========== TEST 6: FINANCIAL TARGETS =========='
)
print()

financial_targets = [
    'Target_Expense_Total_1D',
    'Target_Expense_Total_2D',
    'Target_Expense_Total_3D',
    'Target_Expense_Total_4D',
    'Target_Expense_Total_5D',
    'Target_Expense_Total_6D',
    'Target_Expense_Total_7D',
]

for row in dataset:

    for target_name in financial_targets:

        value = row[target_name]

        if is_missing(value):
            continue

        if value < 0:
            raise AssertionError(
                f'{target_name} contains a negative '
                f'value: {value}'
            )

print(
    'Financial target values: VALID'
)


# =========================================================
# TEST 7 — BINARY TARGETS
# =========================================================

print()
print(
    '========== TEST 7: BINARY TARGETS =========='
)
print()

binary_prefixes = (
    'Target_Has_',
    'Target_High_',
    'Target_Low_',
    'Target_Very_Low_',
    'Target_Moderate_or_High_',
    'Target_Working_Day_',
    'Target_Difficult_',
    'Target_Multiple_',
    'Target_Special_',
    'Target_Health_Problem_',
    'Target_Significant_',
    'Target_Location_Changed_',
    'Target_Same_Location_',
    'Target_Busy_Day_',
    'Target_Financial_Activity_',
    'Target_Active_Day_',
    'Target_Travel_Day_',
)

binary_columns = [
    column
    for column in dataset[0].keys()
    if column.startswith(
        binary_prefixes
    )
]

for row_index, row in enumerate(dataset):

    for column in binary_columns:

        value = row[column]

        if is_missing(value):
            continue

        if value not in (0, 1):
            raise AssertionError(
                f'Invalid binary target value.\n'
                f'Row: {row_index}\n'
                f'Target: {column}\n'
                f'Value: {value}'
            )

print(
    f'Binary targets checked: '
    f'{len(binary_columns)}'
)

print(
    'Binary target values: VALID'
)


# =========================================================
# PASSED
# =========================================================

print()
print(
    '========== TARGET VALUES TEST PASSED =========='
)