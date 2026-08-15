from ml.targets.build import build_target_dataset
from ml.preparation.preparation import get_prepared_dataset


print()
print('========== TARGET NO-LEAKAGE TEST ==========')
print()

target_dataset = build_target_dataset()
prepared_data = get_prepared_dataset()

print(f'Total target rows: {len(target_dataset)}')
print(f'Total prepared rows: {len(prepared_data)}')

if not target_dataset:
    print()
    print('No target data available.')
    raise SystemExit

if not prepared_data:
    print()
    print('No prepared data available.')
    raise SystemExit


# =========================================================
# TEST 1: T+1 MUST NOT USE CURRENT DAY
# =========================================================

print()
print('========== TEST 1: T+1 CURRENT-DAY LEAKAGE ==========')
print()

current_index = 0

current_row = prepared_data[current_index]
future_row = prepared_data[current_index + 1]

current_expense = current_row.get(
    'Expense_Total'
)

future_expense = future_row.get(
    'Expense_Total'
)

target_expense = target_dataset[current_index].get(
    'Target_Expense_Total_1D'
)

print(f"Current date: {current_row['Date']}")
print(f"T+1 date:     {future_row['Date']}")

print(f'Current expense: {current_expense}')
print(f'T+1 expense:     {future_expense}')
print(f'Target expense:  {target_expense}')


# The target must equal T+1, not T.

assert float(target_expense) == float(future_expense)

print('T+1 does not use current-day expense: VALID')


# =========================================================
# TEST 2: T+5 MUST NOT USE CURRENT DAY
# =========================================================

print()
print('========== TEST 2: T+5 CURRENT-DAY LEAKAGE ==========')
print()

future_row = prepared_data[current_index + 5]

current_location = current_row.get(
    'Location'
)

future_location = future_row.get(
    'Location'
)

target_location = target_dataset[current_index].get(
    'Target_Location_5D'
)

print(f"Current date: {current_row['Date']}")
print(f"T+5 date:     {future_row['Date']}")

print(f'Current location: {current_location}')
print(f'T+5 location:     {future_location}')
print(f'Target location:  {target_location}')


assert (
    str(target_location).strip().lower()
    == str(future_location).strip().lower()
)

print('T+5 does not use current-day location: VALID')


# =========================================================
# PASSED
# =========================================================

print()
print('========== TARGET NO-LEAKAGE TEST PASSED ==========')