from ml.targets.location import (
    create_location_targets,
)


print()
print('========== SYNTHETIC LOCATION TARGET TEST ==========')
print()


# =========================================================
# TEST 1: NO LOCATION
# =========================================================

print('========== TEST 1: NO LOCATION ==========')
print()

future_rows = [
    {
        'Location': '',
    }
]

result = create_location_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Location_1D'] == 0
assert result['Target_Location_Changed_1D'] == 0
assert result['Target_Same_Location_1D'] == 0
assert result['Target_Location_1D'] is None

print('No location: VALID')


# =========================================================
# TEST 2: LOCATION WITHOUT HISTORICAL BASELINE
# =========================================================

print()
print('========== TEST 2: LOCATION WITHOUT HISTORICAL BASELINE ==========')
print()

future_rows = [
    {
        'Location': 'Casablanca',
    }
]

result = create_location_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Location_1D'] == 1
assert result['Target_Location_Changed_1D'] == 0
assert result['Target_Same_Location_1D'] == 0
assert result['Target_Location_1D'] == 'casablanca'

print('Location without historical baseline: VALID')


# =========================================================
# TEST 3: SAME LOCATION
# =========================================================

print()
print('========== TEST 3: SAME LOCATION ==========')
print()

previous_rows = [
    {
        'Location': 'Casablanca',
    }
]

future_rows = [
    {
        'Location': 'Casablanca',
    }
]

result = create_location_targets(
    future_rows,
    '1D',
    previous_rows,
)

print(result)

assert result['Target_Has_Location_1D'] == 1
assert result['Target_Location_Changed_1D'] == 0
assert result['Target_Same_Location_1D'] == 1
assert result['Target_Location_1D'] == 'casablanca'

print('Same location: VALID')


# =========================================================
# TEST 4: LOCATION CHANGED
# =========================================================

print()
print('========== TEST 4: LOCATION CHANGED ==========')
print()

previous_rows = [
    {
        'Location': 'Casablanca',
    }
]

future_rows = [
    {
        'Location': 'Rabat',
    }
]

result = create_location_targets(
    future_rows,
    '1D',
    previous_rows,
)

print(result)

assert result['Target_Has_Location_1D'] == 1
assert result['Target_Location_Changed_1D'] == 1
assert result['Target_Same_Location_1D'] == 0
assert result['Target_Location_1D'] == 'rabat'

print('Location change: VALID')


# =========================================================
# TEST 5: TEXT NORMALIZATION
# =========================================================

print()
print('========== TEST 5: TEXT NORMALIZATION ==========')
print()

previous_rows = [
    {
        'Location': ' CASABLANCA ',
    }
]

future_rows = [
    {
        'Location': '  Casablanca  ',
    }
]

result = create_location_targets(
    future_rows,
    '1D',
    previous_rows,
)

print(result)

assert result['Target_Has_Location_1D'] == 1
assert result['Target_Location_Changed_1D'] == 0
assert result['Target_Same_Location_1D'] == 1
assert result['Target_Location_1D'] == 'casablanca'

print('Location text normalization: VALID')


# =========================================================
# TEST 6: LATEST HISTORICAL LOCATION
# =========================================================

print()
print('========== TEST 6: LATEST HISTORICAL LOCATION ==========')
print()

previous_rows = [
    {
        'Location': 'Casablanca',
    },
    {
        'Location': 'Rabat',
    },
    {
        'Location': 'Marrakech',
    },
]

future_rows = [
    {
        'Location': 'Marrakech',
    }
]

result = create_location_targets(
    future_rows,
    '1D',
    previous_rows,
)

print(result)

assert result['Target_Has_Location_1D'] == 1
assert result['Target_Location_Changed_1D'] == 0
assert result['Target_Same_Location_1D'] == 1
assert result['Target_Location_1D'] == 'marrakech'

print('Latest historical location: VALID')


# =========================================================
# TEST 7: IGNORE EMPTY HISTORICAL LOCATIONS
# =========================================================

print()
print('========== TEST 7: IGNORE EMPTY HISTORICAL LOCATIONS ==========')
print()

previous_rows = [
    {
        'Location': 'Casablanca',
    },
    {
        'Location': '',
    },
    {
        'Location': None,
    },
]

future_rows = [
    {
        'Location': 'Casablanca',
    }
]

result = create_location_targets(
    future_rows,
    '1D',
    previous_rows,
)

print(result)

assert result['Target_Has_Location_1D'] == 1
assert result['Target_Location_Changed_1D'] == 0
assert result['Target_Same_Location_1D'] == 1
assert result['Target_Location_1D'] == 'casablanca'

print('Empty historical locations ignored: VALID')


# =========================================================
# TEST 8: PERIOD SAME LOCATION
# =========================================================

print()
print('========== TEST 8: PERIOD SAME LOCATION ==========')
print()

previous_rows = [
    {
        'Location': 'Casablanca',
    }
]

future_rows = [
    {
        'Location': 'Casablanca',
    },
    {
        'Location': 'Casablanca',
    },
    {
        'Location': 'Casablanca',
    },
]

result = create_location_targets(
    future_rows,
    '8_15D',
    previous_rows,
)

print(result)

assert result['Target_Has_Location_8_15D'] == 1
assert result['Target_Location_Changed_8_15D'] == 0
assert result['Target_Same_Location_8_15D'] == 1
assert result['Target_Location_8_15D'] == 'casablanca'

print('Period same location: VALID')


# =========================================================
# TEST 9: PERIOD LOCATION CHANGE
# =========================================================

print()
print('========== TEST 9: PERIOD LOCATION CHANGE ==========')
print()

previous_rows = [
    {
        'Location': 'Casablanca',
    }
]

future_rows = [
    {
        'Location': 'Casablanca',
    },
    {
        'Location': 'Rabat',
    },
]

result = create_location_targets(
    future_rows,
    '16_30D',
    previous_rows,
)

print(result)

assert result['Target_Has_Location_16_30D'] == 1
assert result['Target_Location_Changed_16_30D'] == 1
assert result['Target_Same_Location_16_30D'] == 1
assert result['Target_Location_16_30D'] == 'rabat'

print('Period location change: VALID')


# =========================================================
# TEST 10: PERIOD MULTIPLE LOCATIONS
# =========================================================

print()
print('========== TEST 10: PERIOD MULTIPLE LOCATIONS ==========')
print()

previous_rows = [
    {
        'Location': 'Casablanca',
    }
]

future_rows = [
    {
        'Location': 'Rabat',
    },
    {
        'Location': 'Marrakech',
    },
    {
        'Location': 'Agadir',
    },
]

result = create_location_targets(
    future_rows,
    '30D',
    previous_rows,
)

print(result)

assert result['Target_Has_Location_30D'] == 1
assert result['Target_Location_Changed_30D'] == 1
assert result['Target_Same_Location_30D'] == 0
assert result['Target_Location_30D'] == 'agadir'

print('Period multiple locations: VALID')


# =========================================================
# TEST 11: PERIOD WITH EMPTY LOCATIONS
# =========================================================

print()
print('========== TEST 11: PERIOD WITH EMPTY LOCATIONS ==========')
print()

previous_rows = [
    {
        'Location': 'Casablanca',
    }
]

future_rows = [
    {
        'Location': '',
    },
    {
        'Location': None,
    },
    {
        'Location': 'Casablanca',
    },
]

result = create_location_targets(
    future_rows,
    '30D',
    previous_rows,
)

print(result)

assert result['Target_Has_Location_30D'] == 1
assert result['Target_Location_Changed_30D'] == 0
assert result['Target_Same_Location_30D'] == 1
assert result['Target_Location_30D'] == 'casablanca'

print('Period empty locations handling: VALID')


# =========================================================
# TEST 12: EMPTY DAILY FUTURE
# =========================================================

print()
print('========== TEST 12: EMPTY DAILY FUTURE ==========')
print()

future_rows = []

result = create_location_targets(
    future_rows,
    '1D',
)

print(result)

assert result['Target_Has_Location_1D'] != result['Target_Has_Location_1D']
assert result['Target_Location_Changed_1D'] != result['Target_Location_Changed_1D']
assert result['Target_Same_Location_1D'] != result['Target_Same_Location_1D']
assert result['Target_Location_1D'] is None

print('Empty daily future handling: VALID')


# =========================================================
# TEST 13: EMPTY FUTURE PERIOD
# =========================================================

print()
print('========== TEST 13: EMPTY FUTURE PERIOD ==========')
print()

future_rows = []

result = create_location_targets(
    future_rows,
    '30D',
)

print(result)

assert result['Target_Has_Location_30D'] != result['Target_Has_Location_30D']
assert result['Target_Location_Changed_30D'] != result['Target_Location_Changed_30D']
assert result['Target_Same_Location_30D'] != result['Target_Same_Location_30D']
assert result['Target_Location_30D'] is None

print('Empty future period handling: VALID')


# =========================================================
# TEST 14: INVALID HORIZON
# =========================================================

print()
print('========== TEST 14: INVALID HORIZON ==========')
print()

try:

    create_location_targets(
        [
            {
                'Location': 'Casablanca',
            }
        ],
        'INVALID',
    )

    assert False

except ValueError:

    print('Invalid horizon handling: VALID')


# =========================================================
# FINAL
# =========================================================

print()
print('========== SYNTHETIC LOCATION TARGET TEST PASSED ==========')