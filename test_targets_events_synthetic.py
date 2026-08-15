from math import isnan

from ml.targets.events import (
    create_event_targets,
)


print()
print('========== SYNTHETIC EVENT TARGET TEST ==========')
print()


# =========================================================
# TEST 1: NO EVENT
# =========================================================

print('========== TEST 1: NO EVENT ==========')
print()

future_rows = [
    {
        'Event_Count': 0,
        'Special_Event': '',
    }
]

result = create_event_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Event_1D'] == 0
assert result['Target_Multiple_Events_1D'] == 0
assert result['Target_Has_Special_Event_1D'] == 0

print('No event: VALID')


# =========================================================
# TEST 2: ONE EVENT
# =========================================================

print()
print('========== TEST 2: ONE EVENT ==========')
print()

future_rows = [
    {
        'Event_Count': 1,
        'Special_Event': '',
    }
]

result = create_event_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Event_1D'] == 1
assert result['Target_Multiple_Events_1D'] == 0
assert result['Target_Has_Special_Event_1D'] == 0

print('One event: VALID')


# =========================================================
# TEST 3: MULTIPLE EVENTS BOUNDARY
# =========================================================

print()
print('========== TEST 3: MULTIPLE EVENTS BOUNDARY ==========')
print()

future_rows = [
    {
        'Event_Count': 2,
        'Special_Event': '',
    }
]

result = create_event_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Event_1D'] == 1
assert result['Target_Multiple_Events_1D'] == 1
assert result['Target_Has_Special_Event_1D'] == 0

print('Two events boundary: VALID')


# =========================================================
# TEST 4: MANY EVENTS
# =========================================================

print()
print('========== TEST 4: MANY EVENTS ==========')
print()

future_rows = [
    {
        'Event_Count': 5,
        'Special_Event': '',
    }
]

result = create_event_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Event_1D'] == 1
assert result['Target_Multiple_Events_1D'] == 1

print('Many events: VALID')


# =========================================================
# TEST 5: SPECIAL EVENT
# =========================================================

print()
print('========== TEST 5: SPECIAL EVENT ==========')
print()

future_rows = [
    {
        'Event_Count': 1,
        'Special_Event': 'Birthday',
    }
]

result = create_event_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Event_1D'] == 1
assert result['Target_Multiple_Events_1D'] == 0
assert result['Target_Has_Special_Event_1D'] == 1

print('Special event: VALID')


# =========================================================
# TEST 6: SPECIAL EVENT WITHOUT NORMAL EVENT COUNT
# =========================================================

print()
print('========== TEST 6: SPECIAL EVENT WITHOUT EVENT COUNT ==========')
print()

future_rows = [
    {
        'Event_Count': 0,
        'Special_Event': 'Holiday',
    }
]

result = create_event_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Event_1D'] == 0
assert result['Target_Multiple_Events_1D'] == 0
assert result['Target_Has_Special_Event_1D'] == 1

print('Special event independent of event count: VALID')


# =========================================================
# TEST 7: EMPTY SPECIAL EVENT
# =========================================================

print()
print('========== TEST 7: EMPTY SPECIAL EVENT ==========')
print()

future_rows = [
    {
        'Event_Count': 1,
        'Special_Event': '   ',
    }
]

result = create_event_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Event_1D'] == 1
assert result['Target_Multiple_Events_1D'] == 0
assert result['Target_Has_Special_Event_1D'] == 0

print('Empty special event: VALID')


# =========================================================
# TEST 8: PERIOD EVENT DETECTION
# =========================================================

print()
print('========== TEST 8: PERIOD EVENT DETECTION ==========')
print()

future_rows = [
    {
        'Event_Count': 0,
        'Special_Event': '',
    },
    {
        'Event_Count': 1,
        'Special_Event': '',
    },
    {
        'Event_Count': 0,
        'Special_Event': '',
    },
]

result = create_event_targets(
    future_rows,
    '8_15D',
)

print(result)

assert result['Target_Has_Event_8_15D'] == 1
assert result['Target_Multiple_Events_8_15D'] == 0
assert result['Target_Has_Special_Event_8_15D'] == 0

print('Period event detection: VALID')


# =========================================================
# TEST 9: PERIOD MULTIPLE EVENTS
# =========================================================

print()
print('========== TEST 9: PERIOD MULTIPLE EVENTS ==========')
print()

future_rows = [
    {
        'Event_Count': 0,
        'Special_Event': '',
    },
    {
        'Event_Count': 2,
        'Special_Event': '',
    },
    {
        'Event_Count': 0,
        'Special_Event': '',
    },
]

result = create_event_targets(
    future_rows,
    '16_30D',
)

print(result)

assert result['Target_Has_Event_16_30D'] == 1
assert result['Target_Multiple_Events_16_30D'] == 1
assert result['Target_Has_Special_Event_16_30D'] == 0

print('Period multiple-event detection: VALID')


# =========================================================
# TEST 10: PERIOD SPECIAL EVENT
# =========================================================

print()
print('========== TEST 10: PERIOD SPECIAL EVENT ==========')
print()

future_rows = [
    {
        'Event_Count': 0,
        'Special_Event': '',
    },
    {
        'Event_Count': 1,
        'Special_Event': 'Holiday',
    },
    {
        'Event_Count': 0,
        'Special_Event': '',
    },
]

result = create_event_targets(
    future_rows,
    '30D',
)

print(result)

assert result['Target_Has_Event_30D'] == 1
assert result['Target_Multiple_Events_30D'] == 0
assert result['Target_Has_Special_Event_30D'] == 1

print('Period special-event detection: VALID')


# =========================================================
# TEST 11: EMPTY FUTURE PERIOD
# =========================================================

print()
print('========== TEST 11: EMPTY FUTURE PERIOD ==========')
print()

result = create_event_targets(
    [],
    '30D',
)

print(result)

assert isnan(
    result['Target_Has_Event_30D']
)

assert isnan(
    result['Target_Multiple_Events_30D']
)

assert isnan(
    result['Target_Has_Special_Event_30D']
)

print('Empty future period handling: VALID')


# =========================================================
# TEST 12: EVENT COUNT BOUNDARY 1
# =========================================================

print()
print('========== TEST 12: EVENT COUNT BOUNDARY 1 ==========')
print()

future_rows = [
    {
        'Event_Count': 1,
        'Special_Event': '',
    }
]

result = create_event_targets(
    future_rows,
    '1D',
)

assert result['Target_Has_Event_1D'] == 1
assert result['Target_Multiple_Events_1D'] == 0

print('Event count 1 boundary: VALID')


# =========================================================
# TEST 13: EVENT COUNT BOUNDARY 2
# =========================================================

print()
print('========== TEST 13: EVENT COUNT BOUNDARY 2 ==========')
print()

future_rows = [
    {
        'Event_Count': 2,
        'Special_Event': '',
    }
]

result = create_event_targets(
    future_rows,
    '1D',
)

assert result['Target_Has_Event_1D'] == 1
assert result['Target_Multiple_Events_1D'] == 1

print('Event count 2 boundary: VALID')


# =========================================================
# PASSED
# =========================================================

print()
print('========== SYNTHETIC EVENT TARGET TEST PASSED ==========')