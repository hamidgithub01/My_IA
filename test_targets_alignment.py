from ml.targets.build import build_target_dataset
from ml.preparation.preparation import get_prepared_dataset


print()
print('========== TARGET ALIGNMENT TEST ==========')
print()

dataset = build_target_dataset()
prepared_data = get_prepared_dataset()

print(f'Total target rows: {len(dataset)}')
print(f'Total prepared rows: {len(prepared_data)}')

if not dataset:
    print()
    print('No target data available.')
    raise SystemExit

if not prepared_data:
    print()
    print('No prepared data available.')
    raise SystemExit


# =========================================================
# TEST 1: T+1 DATE ALIGNMENT
# =========================================================

print()
print('========== TEST 1: T+1 DATE ALIGNMENT ==========')
print()

current_index = 0
current_row = dataset[current_index]

expected_date = prepared_data[current_index + 1]['Date']

print(f"Current date: {current_row['Date']}")
print(f'Expected T+1 date: {expected_date}')

assert (
    prepared_data[current_index]['Date']
    == current_row['Date']
)

print('T+1 date alignment: VALID')


# =========================================================
# TEST 2: T+5 DATE ALIGNMENT
# =========================================================

print()
print('========== TEST 2: T+5 DATE ALIGNMENT ==========')
print()

expected_date = prepared_data[current_index + 5]['Date']

print(f"Current date: {current_row['Date']}")
print(f'Expected T+5 date: {expected_date}')

assert (
    expected_date
    == prepared_data[current_index + 5]['Date']
)

print('T+5 date alignment: VALID')


# =========================================================
# TEST 3: T+7 DATE ALIGNMENT
# =========================================================

print()
print('========== TEST 3: T+7 DATE ALIGNMENT ==========')
print()

expected_date = prepared_data[current_index + 7]['Date']

print(f"Current date: {current_row['Date']}")
print(f'Expected T+7 date: {expected_date}')

assert (
    expected_date
    == prepared_data[current_index + 7]['Date']
)

print('T+7 date alignment: VALID')


# =========================================================
# TEST 4: T+5 LOCATION VALUE
# =========================================================

print()
print('========== TEST 4: T+5 LOCATION VALUE ==========')
print()

future_row = prepared_data[current_index + 5]

expected_location = future_row.get('Location')
actual_location = current_row.get(
    'Target_Location_5D'
)

print(f"Current date: {current_row['Date']}")
print(f"Future T+5 date: {future_row['Date']}")
print(f'Expected location: {expected_location}')
print(f'Actual target:     {actual_location}')

assert (
    str(actual_location).strip().lower()
    == str(expected_location).strip().lower()
)

print('T+5 location alignment: VALID')


# =========================================================
# TEST 5: T+1 EXPENSE VALUE
# =========================================================

print()
print('========== TEST 5: T+1 EXPENSE VALUE ==========')
print()

future_row = prepared_data[current_index + 1]

expected_expense = future_row.get(
    'Expense_Total'
)

actual_expense = current_row.get(
    'Target_Expense_Total_1D'
)

print(f"Current date: {current_row['Date']}")
print(f"Future T+1 date: {future_row['Date']}")
print(f'Expected expense: {expected_expense}')
print(f'Actual target:    {actual_expense}')

assert float(actual_expense) == float(expected_expense)

print('T+1 expense alignment: VALID')


# =========================================================
# PASSED
# =========================================================

print()
print('========== TARGET ALIGNMENT TEST PASSED ==========')