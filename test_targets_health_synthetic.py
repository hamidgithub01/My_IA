from ml.targets.health import (
    create_health_targets,
)


print()
print('========== SYNTHETIC HEALTH TARGET TEST ==========')
print()


# =========================================================
# TEST 1: NO HEALTH PROBLEM
# =========================================================

print('========== TEST 1: NO HEALTH PROBLEM ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 8,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Health_Problem_1D'] == 0
assert result['Target_High_Health_Severity_1D'] == 0
assert result['Target_Low_Energy_1D'] == 0
assert result['Target_Significant_Health_Day_1D'] == 0

print('No health problem: VALID')


# =========================================================
# TEST 2: HEALTH PROBLEM
# =========================================================

print()
print('========== TEST 2: HEALTH PROBLEM ==========')
print()

future_rows = [
    {
        'Health_Problem': 'yes',
        'Health_Severity': 2,
        'Energy_Level': 8,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Health_Problem_1D'] == 1
assert result['Target_High_Health_Severity_1D'] == 0
assert result['Target_Low_Energy_1D'] == 0
assert result['Target_Significant_Health_Day_1D'] == 1

print('Health problem: VALID')


# =========================================================
# TEST 3: HIGH SEVERITY BELOW THRESHOLD
# =========================================================

print()
print('========== TEST 3: HIGH SEVERITY BELOW THRESHOLD ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 6,
        'Energy_Level': 8,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_High_Health_Severity_1D'] == 0
assert result['Target_Significant_Health_Day_1D'] == 0

print('Severity 6: VALID')


# =========================================================
# TEST 4: HIGH SEVERITY BOUNDARY
# =========================================================

print()
print('========== TEST 4: HIGH SEVERITY BOUNDARY ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 7,
        'Energy_Level': 8,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_High_Health_Severity_1D'] == 1
assert result['Target_Significant_Health_Day_1D'] == 1

print('Severity 7 boundary: VALID')


# =========================================================
# TEST 5: ENERGY AT 4
# =========================================================

print()
print('========== TEST 5: ENERGY AT 4 ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 4,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Low_Energy_1D'] == 0
assert result['Target_Significant_Health_Day_1D'] == 0

print('Energy 4 boundary: VALID')


# =========================================================
# TEST 6: LOW ENERGY
# =========================================================

print()
print('========== TEST 6: LOW ENERGY ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 3,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Low_Energy_1D'] == 1
assert result['Target_Significant_Health_Day_1D'] == 1

print('Low energy: VALID')


# =========================================================
# TEST 7: ZERO ENERGY IS NOT LOW ENERGY
# =========================================================

print()
print('========== TEST 7: ZERO ENERGY ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 0,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Low_Energy_1D'] == 0
assert result['Target_Significant_Health_Day_1D'] == 0

print('Zero energy treated as unknown: VALID')


# =========================================================
# TEST 8: BOOLEAN HEALTH PROBLEM
# =========================================================

print()
print('========== TEST 8: BOOLEAN HEALTH PROBLEM ==========')
print()

future_rows = [
    {
        'Health_Problem': True,
        'Health_Severity': 2,
        'Energy_Level': 8,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Health_Problem_1D'] == 1
assert result['Target_Significant_Health_Day_1D'] == 1

print('Boolean health problem: VALID')


# =========================================================
# TEST 9: TEXT NORMALIZATION
# =========================================================

print()
print('========== TEST 9: TEXT NORMALIZATION ==========')
print()

future_rows = [
    {
        'Health_Problem': ' YES ',
        'Health_Severity': 2,
        'Energy_Level': 8,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Health_Problem_1D'] == 1
assert result['Target_Significant_Health_Day_1D'] == 1

print('Health problem text normalization: VALID')


# =========================================================
# TEST 10: SIGNIFICANT HEALTH DAY BY SEVERITY
# =========================================================

print()
print('========== TEST 10: SIGNIFICANT HEALTH DAY BY SEVERITY ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 7,
        'Energy_Level': 8,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Health_Problem_1D'] == 0
assert result['Target_High_Health_Severity_1D'] == 1
assert result['Target_Significant_Health_Day_1D'] == 1

print('Significant day by severity: VALID')


# =========================================================
# TEST 11: SIGNIFICANT HEALTH DAY BY LOW ENERGY
# =========================================================

print()
print('========== TEST 11: SIGNIFICANT HEALTH DAY BY LOW ENERGY ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 3,
    }
]

result = create_health_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Health_Problem_1D'] == 0
assert result['Target_High_Health_Severity_1D'] == 0
assert result['Target_Low_Energy_1D'] == 1
assert result['Target_Significant_Health_Day_1D'] == 1

print('Significant day by low energy: VALID')


# =========================================================
# TEST 12: PERIOD HEALTH DETECTION
# =========================================================

print()
print('========== TEST 12: PERIOD HEALTH DETECTION ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 8,
    },
    {
        'Health_Problem': 'yes',
        'Health_Severity': 3,
        'Energy_Level': 8,
    },
    {
        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 8,
    },
]

result = create_health_targets(
    future_rows,
    '8_15D',
)

print(result)

assert result['Target_Health_Problem_8_15D'] == 1
assert result['Target_High_Health_Severity_8_15D'] == 0
assert result['Target_Low_Energy_8_15D'] == 0
assert result['Target_Significant_Health_Day_8_15D'] == 1

print('Period health detection: VALID')


# =========================================================
# TEST 13: PERIOD HIGH SEVERITY
# =========================================================

print()
print('========== TEST 13: PERIOD HIGH SEVERITY ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 8,
    },
    {
        'Health_Problem': 'no',
        'Health_Severity': 7,
        'Energy_Level': 8,
    },
]

result = create_health_targets(
    future_rows,
    '16_30D',
)

print(result)

assert result['Target_Health_Problem_16_30D'] == 0
assert result['Target_High_Health_Severity_16_30D'] == 1
assert result['Target_Low_Energy_16_30D'] == 0
assert result['Target_Significant_Health_Day_16_30D'] == 1

print('Period high severity detection: VALID')


# =========================================================
# TEST 14: PERIOD LOW ENERGY
# =========================================================

print()
print('========== TEST 14: PERIOD LOW ENERGY ==========')
print()

future_rows = [
    {
        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 8,
    },
    {
        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 3,
    },
]

result = create_health_targets(
    future_rows,
    '30D',
)

print(result)

assert result['Target_Health_Problem_30D'] == 0
assert result['Target_High_Health_Severity_30D'] == 0
assert result['Target_Low_Energy_30D'] == 1
assert result['Target_Significant_Health_Day_30D'] == 1

print('Period low energy detection: VALID')


# =========================================================
# TEST 15: EMPTY FUTURE PERIOD
# =========================================================

print()
print('========== TEST 15: EMPTY FUTURE PERIOD ==========')
print()

future_rows = []

result = create_health_targets(
    future_rows,
    '30D',
)

print(result)

assert result['Target_Health_Problem_30D'] != result['Target_Health_Problem_30D']
assert result['Target_High_Health_Severity_30D'] != result['Target_High_Health_Severity_30D']
assert result['Target_Low_Energy_30D'] != result['Target_Low_Energy_30D']
assert result['Target_Significant_Health_Day_30D'] != result['Target_Significant_Health_Day_30D']

print('Empty future period handling: VALID')


# =========================================================
# TEST 16: INVALID HORIZON
# =========================================================

print()
print('========== TEST 16: INVALID HORIZON ==========')
print()

try:
    create_health_targets(
        [
            {
                'Health_Problem': 'no',
                'Health_Severity': 2,
                'Energy_Level': 8,
            }
        ],
        'INVALID',
    )

except ValueError:
    print('Invalid horizon handling: VALID')

else:
    raise AssertionError(
        'Invalid horizon did not raise ValueError'
    )


# =========================================================
# FINAL
# =========================================================

print()
print('========== SYNTHETIC HEALTH TARGET TEST PASSED ==========')