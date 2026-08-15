from ml.features.behavioral import (
    normalize_text,
    encode_binary,
    encode_day_type,
    encode_work_status,
    encode_health_impact,
    encode_travel,
    encode_social_activity,
    encode_special_event,
    encode_location,
    create_historical_behavioral_features,
    create_behavioral_features,
)


# ==========================================================
# ASSERTION HELPERS
# ==========================================================

def assert_equal(
    actual,
    expected,
    message,
):
    if actual != expected:
        raise AssertionError(
            f'{message}\n'
            f'Expected: {expected}\n'
            f'Actual:   {actual}'
        )


def assert_close(
    actual,
    expected,
    message,
    tolerance=1e-9,
):
    if abs(actual - expected) > tolerance:
        raise AssertionError(
            f'{message}\n'
            f'Expected: {expected}\n'
            f'Actual:   {actual}'
        )


# ==========================================================
# TEST DATA
# ==========================================================

def build_historical_row():
    """
    Build a complete deterministic historical row.
    """

    return {
        'Date': '2026-08-14',

        'Day_Type': 'Workday',
        'Work_Status': 'Working',
        'Health_Impact': 'Moderate',
        'Travel': 'Yes',

        'Stress_Level': 7.5,
        'Sleep_Hours': 6.5,

        'Social_Activity': 'High',
        'Special_Event': 'Birthday',
        'Location': 'Work',
    }


# ==========================================================
# TEST 1
# NORMALIZE TEXT
# ==========================================================

def test_normalize_text():

    assert_equal(
        normalize_text('Workday'),
        'workday',
        'normalize_text failed to lowercase text.',
    )

    assert_equal(
        normalize_text('  WORKDAY  '),
        'workday',
        'normalize_text failed to strip whitespace.',
    )

    assert_equal(
        normalize_text(None),
        '',
        'normalize_text should convert None to empty text.',
    )

    assert_equal(
        normalize_text(''),
        '',
        'normalize_text should preserve empty values as empty text.',
    )

    assert_equal(
        normalize_text(123),
        '123',
        'normalize_text failed to convert numeric values to text.',
    )

    print(
        'Text normalization: PASSED'
    )


# ==========================================================
# TEST 2
# BINARY ENCODING
# ==========================================================

def test_binary_encoding():

    positive_values = [
        'yes',
        'true',
        '1',
    ]

    assert_equal(
        encode_binary(
            'yes',
            positive_values,
        ),
        1,
        'Binary encoding failed for positive value.',
    )

    assert_equal(
        encode_binary(
            'YES',
            positive_values,
        ),
        1,
        'Binary encoding should be case-insensitive.',
    )

    assert_equal(
        encode_binary(
            ' true ',
            positive_values,
        ),
        1,
        'Binary encoding should ignore surrounding whitespace.',
    )

    assert_equal(
        encode_binary(
            'no',
            positive_values,
        ),
        0,
        'Binary encoding failed for negative value.',
    )

    assert_equal(
        encode_binary(
            None,
            positive_values,
        ),
        0,
        'Binary encoding failed for None.',
    )

    print(
        'Binary encoding: PASSED'
    )


# ==========================================================
# TEST 3
# DAY TYPE ENCODING
# ==========================================================

def test_day_type_encoding():

    assert_equal(
        encode_day_type('workday'),
        1,
        'Workday encoding is incorrect.',
    )

    assert_equal(
        encode_day_type('working day'),
        1,
        'Working day encoding is incorrect.',
    )

    assert_equal(
        encode_day_type('WORKDAY'),
        1,
        'Workday encoding should be case-insensitive.',
    )

    assert_equal(
        encode_day_type('holiday'),
        2,
        'Holiday encoding is incorrect.',
    )

    assert_equal(
        encode_day_type('weekend'),
        3,
        'Weekend encoding is incorrect.',
    )

    assert_equal(
        encode_day_type('unknown'),
        0,
        'Unknown day type should encode as zero.',
    )

    assert_equal(
        encode_day_type(None),
        0,
        'Empty day type should encode as zero.',
    )

    print(
        'Day type encoding: PASSED'
    )


# ==========================================================
# TEST 4
# WORK STATUS ENCODING
# ==========================================================

def test_work_status_encoding():

    assert_equal(
        encode_work_status('working'),
        1,
        'Working status encoding is incorrect.',
    )

    assert_equal(
        encode_work_status('work'),
        1,
        'Work status encoding is incorrect.',
    )

    assert_equal(
        encode_work_status('off'),
        2,
        'Off status encoding is incorrect.',
    )

    assert_equal(
        encode_work_status('leave'),
        3,
        'Leave status encoding is incorrect.',
    )

    assert_equal(
        encode_work_status('vacation'),
        4,
        'Vacation status encoding is incorrect.',
    )

    assert_equal(
        encode_work_status('unknown'),
        0,
        'Unknown work status should encode as zero.',
    )

    assert_equal(
        encode_work_status(None),
        0,
        'Empty work status should encode as zero.',
    )

    print(
        'Work status encoding: PASSED'
    )


# ==========================================================
# TEST 5
# HEALTH IMPACT ENCODING
# ==========================================================

def test_health_impact_encoding():

    assert_equal(
        encode_health_impact('low'),
        0,
        'Low health impact encoding is incorrect.',
    )

    assert_equal(
        encode_health_impact('normal'),
        0,
        'Normal health impact encoding is incorrect.',
    )

    assert_equal(
        encode_health_impact('moderate'),
        1,
        'Moderate health impact encoding is incorrect.',
    )

    assert_equal(
        encode_health_impact('medium'),
        1,
        'Medium health impact encoding is incorrect.',
    )

    assert_equal(
        encode_health_impact('high'),
        2,
        'High health impact encoding is incorrect.',
    )

    assert_equal(
        encode_health_impact('unknown'),
        0,
        'Unknown health impact should encode as zero.',
    )

    assert_equal(
        encode_health_impact(None),
        0,
        'Empty health impact should encode as zero.',
    )

    print(
        'Health impact encoding: PASSED'
    )


# ==========================================================
# TEST 6
# TRAVEL ENCODING
# ==========================================================

def test_travel_encoding():

    assert_equal(
        encode_travel('yes'),
        1,
        'Travel yes encoding is incorrect.',
    )

    assert_equal(
        encode_travel('true'),
        1,
        'Travel true encoding is incorrect.',
    )

    assert_equal(
        encode_travel('1'),
        1,
        'Travel 1 encoding is incorrect.',
    )

    assert_equal(
        encode_travel('YES'),
        1,
        'Travel encoding should be case-insensitive.',
    )

    assert_equal(
        encode_travel('no'),
        0,
        'Travel no encoding is incorrect.',
    )

    assert_equal(
        encode_travel(None),
        0,
        'Empty travel value should encode as zero.',
    )

    print(
        'Travel encoding: PASSED'
    )


# ==========================================================
# TEST 7
# SOCIAL ACTIVITY ENCODING
# ==========================================================

def test_social_activity_encoding():

    assert_equal(
        encode_social_activity('low'),
        0,
        'Low social activity encoding is incorrect.',
    )

    assert_equal(
        encode_social_activity('moderate'),
        1,
        'Moderate social activity encoding is incorrect.',
    )

    assert_equal(
        encode_social_activity('medium'),
        1,
        'Medium social activity encoding is incorrect.',
    )

    assert_equal(
        encode_social_activity('high'),
        2,
        'High social activity encoding is incorrect.',
    )

    assert_equal(
        encode_social_activity('HIGH'),
        2,
        'Social activity encoding should be case-insensitive.',
    )

    assert_equal(
        encode_social_activity('unknown'),
        0,
        'Unknown social activity should encode as zero.',
    )

    assert_equal(
        encode_social_activity(None),
        0,
        'Empty social activity should encode as zero.',
    )

    print(
        'Social activity encoding: PASSED'
    )


# ==========================================================
# TEST 8
# SPECIAL EVENT ENCODING
# ==========================================================

def test_special_event_encoding():

    assert_equal(
        encode_special_event('Birthday'),
        1,
        'Existing special event should encode as one.',
    )

    assert_equal(
        encode_special_event('Holiday event'),
        1,
        'Existing special event should encode as one.',
    )

    assert_equal(
        encode_special_event('  Event  '),
        1,
        'Whitespace-only normalization failed for special event.',
    )

    assert_equal(
        encode_special_event(''),
        0,
        'Empty special event should encode as zero.',
    )

    assert_equal(
        encode_special_event(None),
        0,
        'None special event should encode as zero.',
    )

    print(
        'Special event encoding: PASSED'
    )


# ==========================================================
# TEST 9
# LOCATION ENCODING
# ==========================================================

def test_location_encoding():

    assert_equal(
        encode_location('Work'),
        1,
        'Existing location should encode as one.',
    )

    assert_equal(
        encode_location('Home'),
        1,
        'Existing location should encode as one.',
    )

    assert_equal(
        encode_location('  Office  '),
        1,
        'Location normalization failed.',
    )

    assert_equal(
        encode_location(''),
        0,
        'Empty location should encode as zero.',
    )

    assert_equal(
        encode_location(None),
        0,
        'None location should encode as zero.',
    )

    print(
        'Location encoding: PASSED'
    )


# ==========================================================
# TEST 10
# HISTORICAL FEATURE STRUCTURE
# ==========================================================

def test_historical_feature_structure():

    row = build_historical_row()

    features = (
        create_historical_behavioral_features(
            row
        )
    )

    expected_features = {
        'Historical_Day_Type_Code',
        'Historical_Work_Status_Code',
        'Historical_Health_Impact_Code',
        'Historical_Travel_Flag',
        'Historical_Stress_Level',
        'Historical_Sleep_Hours',
        'Historical_Social_Activity_Code',
        'Historical_Special_Event_Flag',
        'Historical_Location_Flag',
    }

    actual_features = set(
        features.keys()
    )

    assert_equal(
        actual_features,
        expected_features,
        'Historical behavioral feature structure is incorrect.',
    )

    print(
        'Historical feature structure: PASSED'
    )


# ==========================================================
# TEST 11
# COMPLETE HISTORICAL FEATURE VALUES
# ==========================================================

def test_complete_historical_feature_values():

    row = build_historical_row()

    features = (
        create_historical_behavioral_features(
            row
        )
    )

    assert_equal(
        features[
            'Historical_Day_Type_Code'
        ],
        1,
        'Historical day type feature is incorrect.',
    )

    assert_equal(
        features[
            'Historical_Work_Status_Code'
        ],
        1,
        'Historical work status feature is incorrect.',
    )

    assert_equal(
        features[
            'Historical_Health_Impact_Code'
        ],
        1,
        'Historical health impact feature is incorrect.',
    )

    assert_equal(
        features[
            'Historical_Travel_Flag'
        ],
        1,
        'Historical travel feature is incorrect.',
    )

    assert_close(
        features[
            'Historical_Stress_Level'
        ],
        7.5,
        'Historical stress level is incorrect.',
    )

    assert_close(
        features[
            'Historical_Sleep_Hours'
        ],
        6.5,
        'Historical sleep hours are incorrect.',
    )

    assert_equal(
        features[
            'Historical_Social_Activity_Code'
        ],
        2,
        'Historical social activity feature is incorrect.',
    )

    assert_equal(
        features[
            'Historical_Special_Event_Flag'
        ],
        1,
        'Historical special event feature is incorrect.',
    )

    assert_equal(
        features[
            'Historical_Location_Flag'
        ],
        1,
        'Historical location feature is incorrect.',
    )

    print(
        'Complete historical feature values: PASSED'
    )


# ==========================================================
# TEST 12
# CASE AND WHITESPACE NORMALIZATION
# ==========================================================

def test_historical_case_normalization():

    row = {
        'Day_Type': '  WORKING DAY  ',
        'Work_Status': '  WORK  ',
        'Health_Impact': '  HIGH  ',
        'Travel': ' YES ',
        'Stress_Level': 5,
        'Sleep_Hours': 8,
        'Social_Activity': ' MEDIUM ',
        'Special_Event': ' Event ',
        'Location': ' Home ',
    }

    features = (
        create_historical_behavioral_features(
            row
        )
    )

    assert_equal(
        features[
            'Historical_Day_Type_Code'
        ],
        1,
        'Day type normalization failed.',
    )

    assert_equal(
        features[
            'Historical_Work_Status_Code'
        ],
        1,
        'Work status normalization failed.',
    )

    assert_equal(
        features[
            'Historical_Health_Impact_Code'
        ],
        2,
        'Health impact normalization failed.',
    )

    assert_equal(
        features[
            'Historical_Travel_Flag'
        ],
        1,
        'Travel normalization failed.',
    )

    assert_equal(
        features[
            'Historical_Social_Activity_Code'
        ],
        1,
        'Social activity normalization failed.',
    )

    assert_equal(
        features[
            'Historical_Special_Event_Flag'
        ],
        1,
        'Special event normalization failed.',
    )

    assert_equal(
        features[
            'Historical_Location_Flag'
        ],
        1,
        'Location normalization failed.',
    )

    print(
        'Historical value normalization: PASSED'
    )


# ==========================================================
# TEST 13
# UNKNOWN AND MISSING VALUES
# ==========================================================

def test_unknown_and_missing_values():

    row = {
        'Day_Type': 'Unknown',
        'Work_Status': 'Unknown',
        'Health_Impact': 'Unknown',
        'Travel': 'No',
        'Stress_Level': None,
        'Sleep_Hours': None,
        'Social_Activity': 'Unknown',
        'Special_Event': '',
        'Location': None,
    }

    features = (
        create_historical_behavioral_features(
            row
        )
    )

    assert_equal(
        features[
            'Historical_Day_Type_Code'
        ],
        0,
        'Unknown day type should be zero.',
    )

    assert_equal(
        features[
            'Historical_Work_Status_Code'
        ],
        0,
        'Unknown work status should be zero.',
    )

    assert_equal(
        features[
            'Historical_Health_Impact_Code'
        ],
        0,
        'Unknown health impact should be zero.',
    )

    assert_equal(
        features[
            'Historical_Travel_Flag'
        ],
        0,
        'Negative travel should be zero.',
    )

    assert_close(
        features[
            'Historical_Stress_Level'
        ],
        0.0,
        'Missing stress level should be zero.',
    )

    assert_close(
        features[
            'Historical_Sleep_Hours'
        ],
        0.0,
        'Missing sleep hours should be zero.',
    )

    assert_equal(
        features[
            'Historical_Social_Activity_Code'
        ],
        0,
        'Unknown social activity should be zero.',
    )

    assert_equal(
        features[
            'Historical_Special_Event_Flag'
        ],
        0,
        'Missing special event should be zero.',
    )

    assert_equal(
        features[
            'Historical_Location_Flag'
        ],
        0,
        'Missing location should be zero.',
    )

    print(
        'Unknown and missing values: PASSED'
    )


# ==========================================================
# TEST 14
# EMPTY HISTORICAL ROW
# ==========================================================

def test_empty_historical_row():

    features = (
        create_historical_behavioral_features(
            {}
        )
    )

    if not features:
        raise AssertionError(
            'Empty historical row returned no features.'
        )

    for name, value in features.items():

        if value != 0.0:

            raise AssertionError(
                f'Expected zero for empty historical row: '
                f'{name} = {value}'
            )

    print(
        'Empty historical row handling: PASSED'
    )


# ==========================================================
# TEST 15
# NONE HISTORICAL ROW
# ==========================================================

def test_none_historical_row():

    features = (
        create_historical_behavioral_features(
            None
        )
    )

    if not features:
        raise AssertionError(
            'None historical row returned no features.'
        )

    for name, value in features.items():

        if value != 0.0:

            raise AssertionError(
                f'Expected zero for None historical row: '
                f'{name} = {value}'
            )

    print(
        'None historical row handling: PASSED'
    )


# ==========================================================
# TEST 16
# TARGET-DAY OUTCOME INDEPENDENCE
# ==========================================================

def test_target_day_outcome_independence():

    row = build_historical_row()

    before = (
        create_historical_behavioral_features(
            row
        )
    )

    modified_row = dict(
        row
    )

    # Actual outcome fields.
    modified_row.update({

        'Expense_Total': 999999.0,
        'Income_Total': 888888.0,

        'Expense_Count': 9999,
        'Income_Count': 9999,

        'Event_Count': 9999,

        'Health_Record_Count': 9999,
        'Max_Health_Severity': 9999.0,

        'Activity_Count': 9999,
        'Activity_Duration_Minutes': 999999.0,
        'Activity_Cost': 999999.0,

        'Sleep_Record_Count': 9999,
        'Sleep_Duration_Minutes': 999999.0,
        'Avg_Sleep_Quality': 9999.0,

        'Total_Awakenings': 9999,
    })

    after = (
        create_historical_behavioral_features(
            modified_row
        )
    )

    assert_equal(
        before,
        after,
        'Behavioral features changed because actual '
        'outcome fields were modified.',
    )

    print(
        'Target-day outcome independence: PASSED'
    )


# ==========================================================
# TEST 17
# BACKWARD COMPATIBILITY
# ==========================================================

def test_backward_compatibility():

    row = build_historical_row()

    historical_features = (
        create_historical_behavioral_features(
            row
        )
    )

    compatibility_features = (
        create_behavioral_features(
            row
        )
    )

    assert_equal(
        compatibility_features,
        historical_features,
        'Backward-compatible behavioral wrapper '
        'does not match historical behavioral features.',
    )

    print(
        'Backward compatibility: PASSED'
    )


# ==========================================================
# TEST 18
# NO_INPUT_MUTATION
# ==========================================================

def test_no_input_mutation():

    row = build_historical_row()

    before = dict(
        row
    )

    create_historical_behavioral_features(
        row
    )

    assert_equal(
        row,
        before,
        'Behavioral feature creation modified the input row.',
    )

    print(
        'Input immutability: PASSED'
    )


# ==========================================================
# TEST 19
# OUTPUT VALUES ARE NUMERIC
# ==========================================================

def test_output_values_are_numeric():

    row = build_historical_row()

    features = (
        create_historical_behavioral_features(
            row
        )
    )

    for name, value in features.items():

        if not isinstance(
            value,
            (int, float),
        ):

            raise AssertionError(
                f'Feature {name} is not numeric: '
                f'{type(value).__name__}'
            )

    print(
        'Numeric feature output: PASSED'
    )


# ==========================================================
# MAIN
# ==========================================================

def test_behavioral_features():

    print(
        '========== BEHAVIORAL FEATURES TEST =========='
    )

    test_normalize_text()

    test_binary_encoding()

    test_day_type_encoding()

    test_work_status_encoding()

    test_health_impact_encoding()

    test_travel_encoding()

    test_social_activity_encoding()

    test_special_event_encoding()

    test_location_encoding()

    test_historical_feature_structure()

    test_complete_historical_feature_values()

    test_historical_case_normalization()

    test_unknown_and_missing_values()

    test_empty_historical_row()

    test_none_historical_row()

    test_target_day_outcome_independence()

    test_backward_compatibility()

    test_no_input_mutation()

    test_output_values_are_numeric()

    print(
        '========== BEHAVIORAL FEATURES TEST PASSED =========='
    )


if __name__ == '__main__':
    test_behavioral_features()