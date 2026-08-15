from ml.targets.activity import (
    create_activity_targets,
)


print()
print('========== SYNTHETIC ACTIVITY TARGET TEST ==========')
print()


# =========================================================
# TEST 1: NO ACTIVITY
# =========================================================

print('========== TEST 1: NO ACTIVITY ==========')
print()

future_rows = [
    {
        'Activity_Count': 0,
        'Activity_Duration_Minutes': 0,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Activity_1D'] == 0
assert result['Target_High_Activity_1D'] == 0
assert result['Target_Long_Activity_1D'] == 0

print('No activity: VALID')


# =========================================================
# TEST 2: NORMAL ACTIVITY
# =========================================================

print()
print('========== TEST 2: NORMAL ACTIVITY ==========')
print()

future_rows = [
    {
        'Activity_Count': 1,
        'Activity_Duration_Minutes': 30,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Activity_1D'] == 1
assert result['Target_High_Activity_1D'] == 0
assert result['Target_Long_Activity_1D'] == 0

print('Normal activity: VALID')


# =========================================================
# TEST 3: LONG ACTIVITY
# =========================================================

print()
print('========== TEST 3: LONG ACTIVITY ==========')
print()

future_rows = [
    {
        'Activity_Count': 1,
        'Activity_Duration_Minutes': 60,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Activity_1D'] == 1
assert result['Target_High_Activity_1D'] == 0
assert result['Target_Long_Activity_1D'] == 1

print('Long activity: VALID')


# =========================================================
# TEST 4: HIGH ACTIVITY BY COUNT
# =========================================================

print()
print('========== TEST 4: HIGH ACTIVITY BY COUNT ==========')
print()

future_rows = [
    {
        'Activity_Count': 2,
        'Activity_Duration_Minutes': 30,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Activity_1D'] == 1
assert result['Target_High_Activity_1D'] == 1
assert result['Target_Long_Activity_1D'] == 0

print('High activity by count: VALID')


# =========================================================
# TEST 5: HIGH ACTIVITY BY DURATION
# =========================================================

print()
print('========== TEST 5: HIGH ACTIVITY BY DURATION ==========')
print()

future_rows = [
    {
        'Activity_Count': 1,
        'Activity_Duration_Minutes': 120,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Activity_1D'] == 1
assert result['Target_High_Activity_1D'] == 1
assert result['Target_Long_Activity_1D'] == 1

print('High activity by duration: VALID')

# =========================================================
# TEST 6: PERIOD WITH ACTIVITY ON ONE DAY
# =========================================================

print()
print('========== TEST 6: PERIOD ACTIVITY ==========')
print()

future_rows = [
    {
        'Activity_Count': 0,
        'Activity_Duration_Minutes': 0,
    },
    {
        'Activity_Count': 0,
        'Activity_Duration_Minutes': 0,
    },
    {
        'Activity_Count': 1,
        'Activity_Duration_Minutes': 60,
    },
]

result = create_activity_targets(
    future_rows,
    '8_15D',
)

print(result)

assert result['Target_Has_Activity_8_15D'] == 1
assert result['Target_High_Activity_8_15D'] == 0
assert result['Target_Long_Activity_8_15D'] == 1

print('Period activity detection: VALID')


# =========================================================
# TEST 7: PERIOD WITH HIGH ACTIVITY
# =========================================================

print()
print('========== TEST 7: PERIOD HIGH ACTIVITY ==========')
print()

future_rows = [
    {
        'Activity_Count': 0,
        'Activity_Duration_Minutes': 0,
    },
    {
        'Activity_Count': 2,
        'Activity_Duration_Minutes': 30,
    },
    {
        'Activity_Count': 0,
        'Activity_Duration_Minutes': 0,
    },
]

result = create_activity_targets(
    future_rows,
    '16_30D',
)

print(result)

assert result['Target_Has_Activity_16_30D'] == 1
assert result['Target_High_Activity_16_30D'] == 1
assert result['Target_Long_Activity_16_30D'] == 0

print('Period high activity detection: VALID')


# =========================================================
# TEST 8: EMPTY FUTURE PERIOD
# =========================================================

print()
print('========== TEST 8: EMPTY FUTURE PERIOD ==========')
print()

future_rows = []

result = create_activity_targets(
    future_rows,
    '30D',
)

print(result)

assert result['Target_Has_Activity_30D'] != 0
assert result['Target_High_Activity_30D'] != 0
assert result['Target_Long_Activity_30D'] != 0

print('Empty future period handling: VALID')


# =========================================================
# TEST 9: ACTIVITY COUNT BOUNDARY
# =========================================================

print()
print('========== TEST 9: ACTIVITY COUNT BOUNDARY ==========')
print()

future_rows = [
    {
        'Activity_Count': 1,
        'Activity_Duration_Minutes': 30,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

assert result['Target_High_Activity_1D'] == 0

future_rows = [
    {
        'Activity_Count': 2,
        'Activity_Duration_Minutes': 30,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

assert result['Target_High_Activity_1D'] == 1

print('Activity count boundary: VALID')


# =========================================================
# TEST 10: LONG ACTIVITY BOUNDARY
# =========================================================

print()
print('========== TEST 10: LONG ACTIVITY BOUNDARY ==========')
print()

future_rows = [
    {
        'Activity_Count': 1,
        'Activity_Duration_Minutes': 59,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

assert result['Target_Long_Activity_1D'] == 0

future_rows = [
    {
        'Activity_Count': 1,
        'Activity_Duration_Minutes': 60,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

assert result['Target_Long_Activity_1D'] == 1

print('Long activity boundary: VALID')


# =========================================================
# TEST 11: HIGH ACTIVITY DURATION BOUNDARY
# =========================================================

print()
print('========== TEST 11: HIGH ACTIVITY DURATION BOUNDARY ==========')
print()

future_rows = [
    {
        'Activity_Count': 1,
        'Activity_Duration_Minutes': 119,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

assert result['Target_High_Activity_1D'] == 0

future_rows = [
    {
        'Activity_Count': 1,
        'Activity_Duration_Minutes': 120,
    }
]

result = create_activity_targets(
    future_rows,
    '1D',
)

assert result['Target_High_Activity_1D'] == 1

print('High activity duration boundary: VALID')

print()
print('========== SYNTHETIC ACTIVITY TEST PASSED ==========')