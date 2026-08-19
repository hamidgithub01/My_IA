from ml.prediction.patterns import (
    PATTERN_DETECTED,
    PATTERN_NONE,
    PATTERN_INSUFFICIENT_DATA,
    PATTERN_PERSISTENT_LOW_RELIABILITY,
    PATTERN_PERSISTENT_HIGH_ERROR,
    PATTERN_RELIABILITY_DECLINE,
    PATTERN_INCREASING_ERROR,
    PATTERN_INSUFFICIENT_DATA,
    PATTERN_SEVERITY_INFO,
    PATTERN_SEVERITY_WARNING,
    PATTERN_SEVERITY_HIGH,
    detect_patterns,
    has_patterns,
)


# ==========================================================
# HELPERS
# ==========================================================

def make_record(
    reliability_level='good',
    relative_error=0.05,
    target_name='Target_Test',
):
    return {
        'status':
            'ready_for_evaluation',

        'target_name':
            target_name,

        'target_task':
            'regression',

        'prediction':
            100.0,

        'actual_value':
            100.0,

        'actual_value_available':
            True,

        'absolute_error':
            abs(relative_error * 100.0),

        'signed_error':
            0.0,

        'squared_error':
            (relative_error * 100.0) ** 2,

        'relative_error':
            relative_error,

        'reliability_available':
            True,

        'reliability_level':
            reliability_level,

        'reliability_status':
            'evaluated',
    }


# ==========================================================
# NO PATTERN
# ==========================================================

def test_no_pattern():

    records = [
        make_record(
            reliability_level='excellent',
            relative_error=0.02,
        ),
        make_record(
            reliability_level='excellent',
            relative_error=0.03,
        ),
        make_record(
            reliability_level='good',
            relative_error=0.06,
        ),
    ]

    result = detect_patterns(
        records
    )

    assert (
        result['status']
        == PATTERN_NONE
    )

    assert (
        result['pattern_count']
        == 0
    )

    assert (
        result['patterns']
        == []
    )

    assert (
        has_patterns(result)
        is False
    )


# ==========================================================
# PERSISTENT LOW RELIABILITY
# ==========================================================

def test_persistent_low_reliability():

    records = [
        make_record(
            reliability_level='low',
            relative_error=0.30,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.35,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.40,
        ),
    ]

    result = detect_patterns(
        records
    )

    assert (
        result['status']
        == PATTERN_DETECTED
    )

    assert (
        result['pattern_count']
        == 1
    )

    pattern = result['patterns'][0]

    assert (
        pattern['pattern_type']
        == PATTERN_PERSISTENT_LOW_RELIABILITY
    )

    assert (
        pattern['severity']
        == PATTERN_SEVERITY_HIGH
    )

    assert (
        pattern['occurrences']
        == 3
    )


# ==========================================================
# LOW RELIABILITY BELOW OCCURRENCE THRESHOLD
# ==========================================================

def test_low_reliability_below_threshold():

    records = [
        make_record(
            reliability_level='low',
            relative_error=0.30,
        ),
        make_record(
            reliability_level='good',
            relative_error=0.08,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.40,
        ),
    ]

    result = detect_patterns(
        records,
        minimum_occurrences=3,
    )

    assert (
        all(
            pattern['pattern_type']
            != PATTERN_PERSISTENT_LOW_RELIABILITY
            for pattern in result['patterns']
        )
    )


# ==========================================================
# PERSISTENT HIGH ERROR
# ==========================================================

def test_persistent_high_error():

    records = [
        make_record(
            reliability_level='moderate',
            relative_error=0.25,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.30,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.40,
        ),
    ]

    result = detect_patterns(
        records,
        maximum_relative_error=0.20,
    )

    assert (
        result['status']
        == PATTERN_DETECTED
    )

    patterns = result['patterns']

    assert any(
        pattern['pattern_type']
        == PATTERN_PERSISTENT_HIGH_ERROR
        for pattern in patterns
    )


# ==========================================================
# HIGH ERROR BELOW THRESHOLD
# ==========================================================

def test_high_error_below_threshold():

    records = [
        make_record(
            reliability_level='good',
            relative_error=0.15,
        ),
        make_record(
            reliability_level='good',
            relative_error=0.18,
        ),
        make_record(
            reliability_level='moderate',
            relative_error=0.19,
        ),
    ]

    result = detect_patterns(
        records,
        maximum_relative_error=0.20,
    )

    assert not any(
        pattern['pattern_type']
        == PATTERN_PERSISTENT_HIGH_ERROR
        for pattern in result['patterns']
    )


# ==========================================================
# RELIABILITY DECLINE
# ==========================================================

def test_reliability_decline():

    records = [
        make_record(
            reliability_level='excellent',
            relative_error=0.02,
        ),
        make_record(
            reliability_level='good',
            relative_error=0.07,
        ),
        make_record(
            reliability_level='moderate',
            relative_error=0.15,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.30,
        ),
    ]

    result = detect_patterns(
        records,
        minimum_reliability_decline=2,
    )

    assert any(
        pattern['pattern_type']
        == PATTERN_RELIABILITY_DECLINE
        for pattern in result['patterns']
    )


# ==========================================================
# SMALL RELIABILITY DECLINE
# ==========================================================

def test_small_reliability_decline():

    records = [
        make_record(
            reliability_level='good',
            relative_error=0.08,
        ),
        make_record(
            reliability_level='moderate',
            relative_error=0.15,
        ),
        make_record(
            reliability_level='good',
            relative_error=0.08,
        ),
    ]

    result = detect_patterns(
        records,
        minimum_reliability_decline=2,
    )

    assert not any(
        pattern['pattern_type']
        == PATTERN_RELIABILITY_DECLINE
        for pattern in result['patterns']
    )


# ==========================================================
# INCREASING ERROR
# ==========================================================

def test_increasing_error():

    records = [
        make_record(
            reliability_level='excellent',
            relative_error=0.05,
        ),
        make_record(
            reliability_level='good',
            relative_error=0.10,
        ),
        make_record(
            reliability_level='moderate',
            relative_error=0.17,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.25,
        ),
    ]

    result = detect_patterns(
        records,
        minimum_error_increase=0.15,
    )

    assert any(
        pattern['pattern_type']
        == PATTERN_INCREASING_ERROR
        for pattern in result['patterns']
    )


# ==========================================================
# NO INCREASING ERROR
# ==========================================================

def test_no_increasing_error():

    records = [
        make_record(
            reliability_level='good',
            relative_error=0.10,
        ),
        make_record(
            reliability_level='good',
            relative_error=0.12,
        ),
        make_record(
            reliability_level='good',
            relative_error=0.15,
        ),
    ]

    result = detect_patterns(
        records,
        minimum_error_increase=0.10,
    )

    assert not any(
        pattern['pattern_type']
        == PATTERN_INCREASING_ERROR
        for pattern in result['patterns']
    )


# ==========================================================
# INSUFFICIENT DATA
# ==========================================================

def test_insufficient_data():

    records = [
        {
            'target_name':
                'Target_Test',

            'actual_value_available':
                False,

            'reliability_level':
                'unknown',
        },
    ]

    result = detect_patterns(
        records,
        minimum_occurrences=3,
    )

    assert (
        result['status']
        == PATTERN_INSUFFICIENT_DATA
    )

    assert (
        result['pattern_count']
        == 1
    )

    pattern = result['patterns'][0]

    assert (
        pattern['pattern_type']
        == PATTERN_INSUFFICIENT_DATA
    )

    assert (
        pattern['severity']
        == PATTERN_SEVERITY_INFO
    )


# ==========================================================
# MULTIPLE PATTERNS
# ==========================================================

def test_multiple_patterns():

    records = [
        make_record(
            reliability_level='moderate',
            relative_error=0.25,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.30,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.40,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.50,
        ),
    ]

    result = detect_patterns(
        records,
        minimum_occurrences=3,
        maximum_relative_error=0.20,
        minimum_reliability_decline=1,
        minimum_error_increase=0.20,
    )

    pattern_types = {
        pattern['pattern_type']
        for pattern in result['patterns']
    }

    assert (
        PATTERN_PERSISTENT_LOW_RELIABILITY
        in pattern_types
    )

    assert (
        PATTERN_PERSISTENT_HIGH_ERROR
        in pattern_types
    )

    assert (
        PATTERN_RELIABILITY_DECLINE
        in pattern_types
    )

    assert (
        PATTERN_INCREASING_ERROR
        in pattern_types
    )

    assert (
        result['pattern_count']
        == len(result['patterns'])
    )


# ==========================================================
# TARGET PRESERVATION
# ==========================================================

def test_pattern_target_is_preserved():

    records = [
        make_record(
            reliability_level='low',
            relative_error=0.30,
            target_name='Target_Expense_Total_1D',
        ),
        make_record(
            reliability_level='low',
            relative_error=0.35,
            target_name='Target_Expense_Total_1D',
        ),
        make_record(
            reliability_level='low',
            relative_error=0.40,
            target_name='Target_Expense_Total_1D',
        ),
    ]

    result = detect_patterns(
        records
    )

    assert (
        result['target_name']
        == 'Target_Expense_Total_1D'
    )

    assert (
        result['patterns'][0]['target_name']
        == 'Target_Expense_Total_1D'
    )


# ==========================================================
# PATTERN CONTRACT
# ==========================================================

def test_pattern_result_contract():

    records = [
        make_record(
            reliability_level='low',
            relative_error=0.30,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.35,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.40,
        ),
    ]

    result = detect_patterns(
        records
    )

    assert isinstance(
        result,
        dict,
    )

    assert 'status' in result
    assert 'pattern_count' in result
    assert 'patterns' in result
    assert 'target_name' in result

    assert (
        result['pattern_count']
        == len(result['patterns'])
    )


# ==========================================================
# PATTERN OBJECT CONTRACT
# ==========================================================

def test_pattern_object_contract():

    records = [
        make_record(
            reliability_level='low',
            relative_error=0.30,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.35,
        ),
        make_record(
            reliability_level='low',
            relative_error=0.40,
        ),
    ]

    result = detect_patterns(
        records
    )

    pattern = result['patterns'][0]

    required_fields = {
        'pattern_type',
        'severity',
        'message',
        'reason',
        'target_name',
        'occurrences',
        'metric',
        'current_value',
        'threshold',
    }

    assert required_fields.issubset(
        pattern.keys()
    )


# ==========================================================
# INVALID INPUTS
# ==========================================================

def test_invalid_inputs():

    try:

        detect_patterns(None)

        assert False

    except ValueError:

        pass

    try:

        detect_patterns([])

        assert False

    except ValueError:

        pass

    try:

        detect_patterns(
            [
                make_record(),
            ],
            minimum_occurrences=0,
        )

        assert False

    except ValueError:

        pass

    try:

        detect_patterns(
            [
                make_record(),
            ],
            maximum_relative_error=-0.1,
        )

        assert False

    except ValueError:

        pass

    try:

        detect_patterns(
            [
                make_record(),
            ],
            minimum_error_increase=-0.1,
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# CONVENIENCE FUNCTION
# ==========================================================

def test_has_patterns():

    result = detect_patterns(
        [
            make_record(
                reliability_level='low',
                relative_error=0.30,
            ),
            make_record(
                reliability_level='low',
                relative_error=0.35,
            ),
            make_record(
                reliability_level='low',
                relative_error=0.40,
            ),
        ]
    )

    assert (
        has_patterns(result)
        is True
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    print(
        '========== PATTERN TEST SUITE =========='
    )

    test_no_pattern()
    test_persistent_low_reliability()
    test_low_reliability_below_threshold()
    test_persistent_high_error()
    test_high_error_below_threshold()
    test_reliability_decline()
    test_small_reliability_decline()
    test_increasing_error()
    test_no_increasing_error()
    test_insufficient_data()
    test_multiple_patterns()
    test_pattern_target_is_preserved()
    test_pattern_result_contract()
    test_pattern_object_contract()
    test_invalid_inputs()
    test_has_patterns()

    print(
        'ALL PATTERN TESTS PASSED'
    )