from ml.targets.behavioral import (
    create_behavioral_targets,
)


print()
print('========== SYNTHETIC BEHAVIORAL TARGET TEST ==========')
print()


# =========================================================
# TEST 1: LOW STRESS
# =========================================================

print('========== TEST 1: LOW STRESS ==========')
print()

future_rows = [
    {
        'Stress_Level': 3,
        'Sleep_Hours': 8,
        'Social_Activity': 'low',
        'Work_Status': 'off',
    }
]

result = create_behavioral_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_High_Stress_1D'] == 0
assert result['Target_Moderate_or_High_Stress_1D'] == 0

print('Low stress: VALID')


# =========================================================
# TEST 2: MODERATE STRESS BOUNDARY
# =========================================================

print()
print('========== TEST 2: MODERATE STRESS BOUNDARY ==========')
print()

future_rows = [
    {
        'Stress_Level': 5,
        'Sleep_Hours': 8,
        'Social_Activity': 'low',
        'Work_Status': 'off',
    }
]

result = create_behavioral_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_High_Stress_1D'] == 0
assert result['Target_Moderate_or_High_Stress_1D'] == 1

print('Stress level 5 boundary: VALID')


# =========================================================
# TEST 3: HIGH STRESS BOUNDARY
# =========================================================

print()
print('========== TEST 3: HIGH STRESS BOUNDARY ==========')
print()

future_rows = [
    {
        'Stress_Level': 7,
        'Sleep_Hours': 8,
        'Social_Activity': 'low',
        'Work_Status': 'off',
    }
]

result = create_behavioral_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_High_Stress_1D'] == 1
assert result['Target_Moderate_or_High_Stress_1D'] == 1

print('Stress level 7 boundary: VALID')


# =========================================================
# TEST 4: SLEEP AT 6 HOURS
# =========================================================

print()
print('========== TEST 4: SLEEP AT 6 HOURS ==========')
print()

future_rows = [
    {
        'Stress_Level': 2,
        'Sleep_Hours': 6,
        'Social_Activity': 'low',
        'Work_Status': 'off',
    }
]

result = create_behavioral_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Low_Sleep_1D'] == 0
assert result['Target_Very_Low_Sleep_1D'] == 0

print('Sleep 6 hours boundary: VALID')


# =========================================================
# TEST 5: LOW SLEEP
# =========================================================

print()
print('========== TEST 5: LOW SLEEP ==========')
print()

future_rows = [
    {
        'Stress_Level': 2,
        'Sleep_Hours': 5.5,
        'Social_Activity': 'low',
        'Work_Status': 'off',
    }
]

result = create_behavioral_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Low_Sleep_1D'] == 1
assert result['Target_Very_Low_Sleep_1D'] == 0

print('Low sleep: VALID')


# =========================================================
# TEST 6: VERY LOW SLEEP
# =========================================================

print()
print('========== TEST 6: VERY LOW SLEEP ==========')
print()

future_rows = [
    {
        'Stress_Level': 2,
        'Sleep_Hours': 4.5,
        'Social_Activity': 'low',
        'Work_Status': 'off',
    }
]

result = create_behavioral_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Low_Sleep_1D'] == 1
assert result['Target_Very_Low_Sleep_1D'] == 1

print('Very low sleep: VALID')


# =========================================================
# TEST 7: HIGH SOCIAL ACTIVITY
# =========================================================

print()
print('========== TEST 7: HIGH SOCIAL ACTIVITY ==========')
print()

future_rows = [
    {
        'Stress_Level': 2,
        'Sleep_Hours': 8,
        'Social_Activity': 'high',
        'Work_Status': 'off',
    }
]

result = create_behavioral_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_High_Social_Activity_1D'] == 1
assert result['Target_Moderate_or_High_Social_Activity_1D'] == 1
print('High social activity: VALID')

# =========================================================
# TEST 8: WORKING DAY
# =========================================================

print()
print('========== TEST 8: WORKING DAY ==========')
print()

future_rows = [
    {
        'Stress_Level': 2,
        'Sleep_Hours': 8,
        'Social_Activity': 'low',
        'Work_Status': 'working',
    }
]

result = create_behavioral_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Working_Day_1D'] == 1

print('Working day: VALID')

# =========================================================
# TEST 9: MODERATE SOCIAL ACTIVITY
# =========================================================

print()
print('========== TEST 9: MODERATE SOCIAL ACTIVITY ==========')
print()

future_rows = [
    {
        'Stress_Level': 2,
        'Sleep_Hours': 8,
        'Social_Activity': 'moderate',
        'Work_Status': 'off',
    }
]

result = create_behavioral_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_High_Social_Activity_1D'] == 0
assert result['Target_Moderate_or_High_Social_Activity_1D'] == 1

print('Moderate social activity: VALID')

# =========================================================
# TEST 10: MEDIUM SOCIAL ACTIVITY
# =========================================================

print()
print('========== TEST 10: MEDIUM SOCIAL ACTIVITY ==========')
print()

future_rows = [
    {
        'Stress_Level': 2,
        'Sleep_Hours': 8,
        'Social_Activity': 'medium',
        'Work_Status': 'off',
    }
]

result = create_behavioral_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_High_Social_Activity_1D'] == 0
assert result['Target_Moderate_or_High_Social_Activity_1D'] == 1

print('Medium social activity: VALID')