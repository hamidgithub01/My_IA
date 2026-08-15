from math import isnan

from ml.targets.financial import (
    create_financial_targets,
)


print()
print('========== SYNTHETIC FINANCIAL TARGET TEST ==========')
print()


# =========================================================
# TEST 1: NO EXPENSE / NO INCOME
# =========================================================

print('========== TEST 1: NO EXPENSE / NO INCOME ==========')
print()

future_rows = [
    {
        'Expense_Total': 0,
        'Income_Total': 0,
    }
]

result = create_financial_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Expense_Total_1D'] == 0
assert result['Target_Income_Total_1D'] == 0
assert result['Target_Balance_1D'] == 0
assert result['Target_Expense_Days_1D'] == 0
assert result['Target_Income_Days_1D'] == 0
assert result['Target_High_Expense_1D'] == 0

print('Zero financial activity: VALID')


# =========================================================
# TEST 2: EXPENSE ONLY
# =========================================================

print()
print('========== TEST 2: EXPENSE ONLY ==========')
print()

future_rows = [
    {
        'Expense_Total': 100,
        'Income_Total': 0,
    }
]

result = create_financial_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Expense_Total_1D'] == 100
assert result['Target_Income_Total_1D'] == 0
assert result['Target_Balance_1D'] == -100
assert result['Target_Expense_Days_1D'] == 1
assert result['Target_Income_Days_1D'] == 0

print('Expense-only day: VALID')


# =========================================================
# TEST 3: INCOME ONLY
# =========================================================

print()
print('========== TEST 3: INCOME ONLY ==========')
print()

future_rows = [
    {
        'Expense_Total': 0,
        'Income_Total': 500,
    }
]

result = create_financial_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Expense_Total_1D'] == 0
assert result['Target_Income_Total_1D'] == 500
assert result['Target_Balance_1D'] == 500
assert result['Target_Expense_Days_1D'] == 0
assert result['Target_Income_Days_1D'] == 1

print('Income-only day: VALID')


# =========================================================
# TEST 4: INCOME AND EXPENSE
# =========================================================

print()
print('========== TEST 4: INCOME AND EXPENSE ==========')
print()

future_rows = [
    {
        'Expense_Total': 150,
        'Income_Total': 500,
    }
]

result = create_financial_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Expense_Total_1D'] == 150
assert result['Target_Income_Total_1D'] == 500
assert result['Target_Balance_1D'] == 350
assert result['Target_Expense_Days_1D'] == 1
assert result['Target_Income_Days_1D'] == 1

print('Income and expense calculation: VALID')


# =========================================================
# TEST 5: HIGH EXPENSE BELOW THRESHOLD
# =========================================================

print()
print('========== TEST 5: HIGH EXPENSE BELOW THRESHOLD ==========')
print()

previous_rows = [
    {'Expense_Total': 100},
    {'Expense_Total': 100},
    {'Expense_Total': 100},
]

future_rows = [
    {
        'Expense_Total': 149,
        'Income_Total': 0,
    }
]

result = create_financial_targets(
    future_rows,
    '1D',
    previous_rows,
)

print(result)

assert result['Target_High_Expense_1D'] == 0

print('Expense below 150% threshold: VALID')


# =========================================================
# TEST 6: HIGH EXPENSE AT THRESHOLD
# =========================================================

print()
print('========== TEST 6: HIGH EXPENSE AT THRESHOLD ==========')
print()

previous_rows = [
    {'Expense_Total': 100},
    {'Expense_Total': 100},
    {'Expense_Total': 100},
]

future_rows = [
    {
        'Expense_Total': 150,
        'Income_Total': 0,
    }
]

result = create_financial_targets(
    future_rows,
    '1D',
    previous_rows,
)

print(result)

assert result['Target_High_Expense_1D'] == 1

print('Expense at 150% threshold: VALID')


# =========================================================
# TEST 7: NO HISTORICAL BASELINE
# =========================================================

print()
print('========== TEST 7: NO HISTORICAL BASELINE ==========')
print()

future_rows = [
    {
        'Expense_Total': 1000,
        'Income_Total': 0,
    }
]

result = create_financial_targets(
    future_rows,
    '1D',
    [],
)

print(result)

assert result['Target_High_Expense_1D'] == 0

print('No historical baseline: VALID')


# =========================================================
# TEST 8: PERIOD TOTALS
# =========================================================

print()
print('========== TEST 8: PERIOD TOTALS ==========')
print()

future_rows = [
    {
        'Expense_Total': 100,
        'Income_Total': 500,
    },
    {
        'Expense_Total': 50,
        'Income_Total': 0,
    },
    {
        'Expense_Total': 0,
        'Income_Total': 200,
    },
]

result = create_financial_targets(
    future_rows,
    '8_15D',
)

print(result)

assert result['Target_Expense_Total_8_15D'] == 150
assert result['Target_Income_Total_8_15D'] == 700
assert result['Target_Balance_8_15D'] == 550

print('Period totals: VALID')


# =========================================================
# TEST 9: PERIOD EXPENSE / INCOME DAYS
# =========================================================

print()
print('========== TEST 9: PERIOD EXPENSE / INCOME DAYS ==========')
print()

future_rows = [
    {
        'Expense_Total': 100,
        'Income_Total': 500,
    },
    {
        'Expense_Total': 50,
        'Income_Total': 0,
    },
    {
        'Expense_Total': 0,
        'Income_Total': 200,
    },
    {
        'Expense_Total': 0,
        'Income_Total': 0,
    },
]

result = create_financial_targets(
    future_rows,
    '16_30D',
)

print(result)

assert result['Target_Expense_Days_16_30D'] == 2
assert result['Target_Income_Days_16_30D'] == 2

print('Period expense/income day counts: VALID')


# =========================================================
# TEST 10: PERIOD HIGH EXPENSE
# =========================================================

print()
print('========== TEST 10: PERIOD HIGH EXPENSE ==========')
print()

previous_rows = [
    {'Expense_Total': 100},
    {'Expense_Total': 100},
    {'Expense_Total': 100},
]

future_rows = [
    {
        'Expense_Total': 100,
        'Income_Total': 0,
    },
    {
        'Expense_Total': 150,
        'Income_Total': 0,
    },
    {
        'Expense_Total': 50,
        'Income_Total': 0,
    },
]

result = create_financial_targets(
    future_rows,
    '30D',
    previous_rows,
)

print(result)

assert result['Target_High_Expense_30D'] == 1

print('Period high expense detection: VALID')


# =========================================================
# TEST 11: EMPTY FUTURE PERIOD
# =========================================================

print()
print('========== TEST 11: EMPTY FUTURE PERIOD ==========')
print()

result = create_financial_targets(
    [],
    '30D',
)

print(result)

assert isnan(
    result['Target_Expense_Total_30D']
)

assert isnan(
    result['Target_Income_Total_30D']
)

assert isnan(
    result['Target_Balance_30D']
)

assert isnan(
    result['Target_Expense_Days_30D']
)

assert isnan(
    result['Target_Income_Days_30D']
)

assert isnan(
    result['Target_High_Expense_30D']
)

print('Empty future period handling: VALID')


# =========================================================
# TEST 12: ZERO EXPENSE DOES NOT BECOME HIGH EXPENSE
# =========================================================

print()
print('========== TEST 12: ZERO EXPENSE HIGH-EXPENSE BOUNDARY ==========')
print()

previous_rows = [
    {'Expense_Total': 100},
    {'Expense_Total': 100},
    {'Expense_Total': 100},
]

future_rows = [
    {
        'Expense_Total': 0,
        'Income_Total': 0,
    }
]

result = create_financial_targets(
    future_rows,
    '1D',
    previous_rows,
)

print(result)

assert result['Target_High_Expense_1D'] == 0

print('Zero expense boundary: VALID')


# =========================================================
# PASSED
# =========================================================

print()
print('========== SYNTHETIC FINANCIAL TARGET TEST PASSED ==========')