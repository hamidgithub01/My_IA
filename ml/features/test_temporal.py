from datetime import date, datetime

from ml.features.temporal import (
    create_temporal_features,
)


# ==========================================================
# TEST HELPERS
# ==========================================================

def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(
            f'{message}\n'
            f'Expected: {expected}\n'
            f'Actual:   {actual}'
        )


def assert_empty(result, message):
    if result != {}:
        raise AssertionError(
            f'{message}\n'
            f'Expected: {{}}\n'
            f'Actual:   {result}'
        )


# ==========================================================
# EXPECTED FEATURE STRUCTURE
# ==========================================================

EXPECTED_FEATURES = {
    'Day_of_Week',
    'Day_of_Month',
    'Month',
    'Quarter',
    'Is_Weekend',
    'Is_Month_Start',
    'Is_Month_End',
    'Week_of_Month',
    'Days_From_Month_Start',
    'Days_To_Month_End',
}


# ==========================================================
# BASIC STRUCTURE
# ==========================================================

def test_feature_structure():
    row = {
        'Date': date(2026, 8, 15),
    }

    features = create_temporal_features(row)

    actual = set(features.keys())

    assert_equal(
        actual,
        EXPECTED_FEATURES,
        'Temporal feature structure mismatch.',
    )


# ==========================================================
# BASIC DATE FEATURES
# ==========================================================

def test_basic_date_features():
    row = {
        'Date': date(2026, 8, 15),
    }

    features = create_temporal_features(row)

    # 2026-08-15 is Saturday.
    assert_equal(
        features['Day_of_Week'],
        5,
        'Day_of_Week calculation failed.',
    )

    assert_equal(
        features['Day_of_Month'],
        15,
        'Day_of_Month calculation failed.',
    )

    assert_equal(
        features['Month'],
        8,
        'Month calculation failed.',
    )

    assert_equal(
        features['Quarter'],
        3,
        'Quarter calculation failed.',
    )


# ==========================================================
# WEEKEND
# ==========================================================

def test_weekend_detection():
    saturday = create_temporal_features({
        'Date': date(2026, 8, 15),
    })

    monday = create_temporal_features({
        'Date': date(2026, 8, 17),
    })

    assert_equal(
        saturday['Is_Weekend'],
        1,
        'Saturday should be detected as weekend.',
    )

    assert_equal(
        monday['Is_Weekend'],
        0,
        'Monday should not be detected as weekend.',
    )


# ==========================================================
# MONTH BOUNDARIES
# ==========================================================

def test_month_start():
    features = create_temporal_features({
        'Date': date(2026, 8, 1),
    })

    assert_equal(
        features['Is_Month_Start'],
        1,
        'First day of month should be detected.',
    )

    assert_equal(
        features['Days_From_Month_Start'],
        0,
        'Days_From_Month_Start is incorrect.',
    )


def test_month_end():
    features = create_temporal_features({
        'Date': date(2026, 8, 31),
    })

    assert_equal(
        features['Is_Month_End'],
        1,
        'Last day of month should be detected.',
    )

    assert_equal(
        features['Days_To_Month_End'],
        0,
        'Days_To_Month_End is incorrect.',
    )


# ==========================================================
# MONTH LENGTH
# ==========================================================

def test_month_length_boundaries():
    test_cases = [
        # date, expected days in month
        (date(2026, 1, 31), 31),
        (date(2026, 4, 30), 30),
        (date(2026, 2, 28), 28),
        (date(2028, 2, 29), 29),
    ]

    for test_date, expected_days in test_cases:

        features = create_temporal_features({
            'Date': test_date,
        })

        assert_equal(
            features['Days_To_Month_End'],
            0,
            (
                f'Month length calculation failed '
                f'for {test_date}. '
                f'Expected {expected_days} days.'
            ),
        )


# ==========================================================
# WEEK OF MONTH
# ==========================================================

def test_week_of_month():
    test_cases = [
        (1, 1),
        (7, 1),
        (8, 2),
        (14, 2),
        (15, 3),
        (21, 3),
        (22, 4),
        (28, 4),
        (29, 5),
        (31, 5),
    ]

    for day, expected_week in test_cases:

        features = create_temporal_features({
            'Date': date(2026, 8, day),
        })

        assert_equal(
            features['Week_of_Month'],
            expected_week,
            (
                f'Week_of_Month calculation failed '
                f'for day {day}.'
            ),
        )


# ==========================================================
# DATE / DATETIME / STRING SUPPORT
# ==========================================================

def test_supported_date_types():

    expected = create_temporal_features({
        'Date': date(2026, 8, 15),
    })

    datetime_result = create_temporal_features({
        'Date': datetime(
            2026,
            8,
            15,
            18,
            30,
        ),
    })

    string_result = create_temporal_features({
        'Date': '2026-08-15',
    })

    assert_equal(
        datetime_result,
        expected,
        'datetime input produced different features.',
    )

    assert_equal(
        string_result,
        expected,
        'string input produced different features.',
    )


# ==========================================================
# INVALID DATE HANDLING
# ==========================================================

def test_invalid_date_handling():

    invalid_values = [
        None,
        '',
        'invalid-date',
        '2026-99-99',
        12345,
        object(),
    ]

    for value in invalid_values:

        result = create_temporal_features({
            'Date': value,
        })

        assert_empty(
            result,
            f'Invalid Date should return empty features: {value}',
        )


# ==========================================================
# TARGET-DAY OUTCOME INDEPENDENCE
# ==========================================================

def test_target_day_outcome_independence():

    base_row = {
        'Date': date(2026, 8, 15),

        'Expense_Total': 100.0,
        'Income_Total': 500.0,
        'Activity_Cost': 75.0,
        'Health_Record_Count': 3,
        'Event_Count': 5,
        'Sleep_Duration_Minutes': 420,
    }

    modified_row = {
        'Date': date(2026, 8, 15),

        # Completely different target-day outcomes.
        'Expense_Total': 999999.0,
        'Income_Total': 999999.0,
        'Activity_Cost': 999999.0,
        'Health_Record_Count': 999,
        'Event_Count': 999,
        'Sleep_Duration_Minutes': 9999,
    }

    base_features = create_temporal_features(
        base_row
    )

    modified_features = create_temporal_features(
        modified_row
    )

    assert_equal(
        base_features,
        modified_features,
        (
            'Temporal features depend on target-day '
            'outcomes.'
        ),
    )


# ==========================================================
# DATE IS THE ONLY INFORMATION SOURCE
# ==========================================================

def test_extra_fields_do_not_change_features():

    row_a = {
        'Date': date(2026, 8, 15),
    }

    row_b = {
        'Date': date(2026, 8, 15),

        'Expense_Total': 12345,
        'Income_Total': 54321,
        'Health_Record_Count': 100,
        'Activity_Count': 200,
        'Stress_Level': 10,
        'Sleep_Hours': 2,
        'Travel_Flag': 1,
        'Special_Event_Flag': 1,
    }

    features_a = create_temporal_features(row_a)
    features_b = create_temporal_features(row_b)

    assert_equal(
        features_a,
        features_b,
        (
            'Temporal features changed because of '
            'non-date fields.'
        ),
    )


# ==========================================================
# MAIN TEST
# ==========================================================

def test_temporal_features():

    print(
        '========== TEMPORAL FEATURES TEST =========='
    )

    test_feature_structure()
    print(
        'Feature structure: PASSED'
    )

    test_basic_date_features()
    print(
        'Basic date features: PASSED'
    )

    test_weekend_detection()
    print(
        'Weekend detection: PASSED'
    )

    test_month_start()
    print(
        'Month-start boundary: PASSED'
    )

    test_month_end()
    print(
        'Month-end boundary: PASSED'
    )

    test_month_length_boundaries()
    print(
        'Month length boundaries: PASSED'
    )

    test_week_of_month()
    print(
        'Week-of-month calculation: PASSED'
    )

    test_supported_date_types()
    print(
        'Date type handling: PASSED'
    )

    test_invalid_date_handling()
    print(
        'Invalid date handling: PASSED'
    )

    test_target_day_outcome_independence()
    print(
        'Target-day outcome independence: PASSED'
    )

    test_extra_fields_do_not_change_features()
    print(
        'Extra-field independence: PASSED'
    )

    print(
        '========== TEMPORAL FEATURES TEST PASSED =========='
    )


if __name__ == '__main__':
    test_temporal_features()