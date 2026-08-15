from copy import deepcopy
from datetime import date, timedelta

from ml.features.history import (
    create_history_features,
)


# ==========================================================
# TEST DATA
# ==========================================================

def build_test_rows():
    """
    Build deterministic historical rows for testing.

    The target date is deliberately separated from the
    historical rows so that temporal boundaries are obvious.
    """

    return [
        {
            'Date': date(2026, 8, 7),

            'Expense_Total': 100.0,
            'Income_Total': 200.0,
            'Event_Count': 2,

            'Health_Record_Count': 1,
            'Max_Health_Severity': 2.0,
            'Avg_Energy_Level': 7.0,

            'Activity_Count': 2,
            'Activity_Duration_Minutes': 60.0,
            'Activity_Cost': 20.0,

            'Sleep_Duration_Minutes': 420.0,
            'Avg_Sleep_Quality': 8.0,
            'Total_Awakenings': 1.0,

            'Day_Type': 'workday',
            'Work_Status': 'working',
            'Health_Impact': 'none',
            'Travel': 'no',
            'Stress_Level': 3.0,
            'Sleep_Hours': 7.0,
            'Social_Activity': 'low',
            'Special_Event': '',
            'Location': 'home',
        },

        {
            'Date': date(2026, 8, 8),

            'Expense_Total': 300.0,
            'Income_Total': 0.0,
            'Event_Count': 5,

            'Health_Record_Count': 2,
            'Max_Health_Severity': 4.0,
            'Avg_Energy_Level': 5.0,

            'Activity_Count': 3,
            'Activity_Duration_Minutes': 90.0,
            'Activity_Cost': 50.0,

            'Sleep_Duration_Minutes': 480.0,
            'Avg_Sleep_Quality': 6.0,
            'Total_Awakenings': 3.0,

            'Day_Type': 'weekend',
            'Work_Status': 'off',
            'Health_Impact': 'low',
            'Travel': 'yes',
            'Stress_Level': 6.0,
            'Sleep_Hours': 8.0,
            'Social_Activity': 'high',
            'Special_Event': 'party',
            'Location': 'city',
        },

        {
            'Date': date(2026, 8, 10),

            'Expense_Total': 150.0,
            'Income_Total': 500.0,
            'Event_Count': 1,

            'Health_Record_Count': 1,
            'Max_Health_Severity': 1.0,
            'Avg_Energy_Level': 8.0,

            'Activity_Count': 1,
            'Activity_Duration_Minutes': 30.0,
            'Activity_Cost': 10.0,

            'Sleep_Duration_Minutes': 450.0,
            'Avg_Sleep_Quality': 9.0,
            'Total_Awakenings': 0.0,

            'Day_Type': 'workday',
            'Work_Status': 'working',
            'Health_Impact': 'none',
            'Travel': 'no',
            'Stress_Level': 2.0,
            'Sleep_Hours': 7.5,
            'Social_Activity': 'medium',
            'Special_Event': '',
            'Location': 'work',
        },
    ]


def build_target_row():
    """
    Target day.

    Its actual outcomes must NEVER affect historical features.
    """

    return {
        'Date': date(2026, 8, 11),

        'Expense_Total': 9999.0,
        'Income_Total': 8888.0,
        'Event_Count': 99,

        'Health_Record_Count': 99,
        'Max_Health_Severity': 99.0,
        'Avg_Energy_Level': 99.0,

        'Activity_Count': 99,
        'Activity_Duration_Minutes': 9999.0,
        'Activity_Cost': 9999.0,

        'Sleep_Duration_Minutes': 9999.0,
        'Avg_Sleep_Quality': 99.0,
        'Total_Awakenings': 99.0,

        'Day_Type': 'holiday',
        'Work_Status': 'leave',
        'Health_Impact': 'high',
        'Travel': 'yes',
        'Stress_Level': 99.0,
        'Sleep_Hours': 99.0,
        'Social_Activity': 'high',
        'Special_Event': 'TARGET_EVENT',
        'Location': 'TARGET_LOCATION',
    }


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


def assert_not_changed(
    before,
    after,
    message,
):
    if before != after:
        changed = {
            key: (
                before.get(key),
                after.get(key),
            )
            for key in before
            if before.get(key) != after.get(key)
        }

        raise AssertionError(
            f'{message}\n'
            f'Changed features: {changed}'
        )


# ==========================================================
# TEST 1
# TARGET-DAY OUTCOME INDEPENDENCE
# ==========================================================

def test_target_day_outcome_independence():
    """
    Changing actual target-day outcomes must not change
    historical features.
    """

    historical_rows = build_test_rows()
    target_row = build_target_row()

    features_before = create_history_features(
        target_row,
        historical_rows,
    )

    modified_target = deepcopy(
        target_row
    )

    # Change every target-day outcome/context field.
    modified_target.update({

        'Expense_Total': 123456.0,
        'Income_Total': 654321.0,
        'Event_Count': 777,

        'Health_Record_Count': 777,
        'Max_Health_Severity': 777.0,
        'Avg_Energy_Level': 777.0,

        'Activity_Count': 777,
        'Activity_Duration_Minutes': 77777.0,
        'Activity_Cost': 77777.0,

        'Sleep_Duration_Minutes': 77777.0,
        'Avg_Sleep_Quality': 777.0,
        'Total_Awakenings': 777.0,

        'Day_Type': 'workday',
        'Work_Status': 'working',
        'Health_Impact': 'none',
        'Travel': 'no',
        'Stress_Level': 1.0,
        'Sleep_Hours': 1.0,
        'Social_Activity': 'low',
        'Special_Event': '',
        'Location': 'home',
    })

    features_after = create_history_features(
        modified_target,
        historical_rows,
    )

    assert_not_changed(
        features_before,
        features_after,
        'Target-day data affected historical features.',
    )

    print(
        'Target-day outcome independence: PASSED'
    )


# ==========================================================
# TEST 2
# FUTURE ROW MUST NOT BE USED
# ==========================================================

def test_future_row_exclusion():
    """
    Adding a row after the target date must not change
    historical features.
    """

    historical_rows = build_test_rows()
    target_row = build_target_row()

    features_before = create_history_features(
        target_row,
        historical_rows,
    )

    future_row = {
        'Date': date(2026, 8, 12),

        'Expense_Total': 999999.0,
        'Income_Total': 999999.0,
        'Event_Count': 999,

        'Health_Record_Count': 999,
        'Max_Health_Severity': 999.0,
        'Avg_Energy_Level': 999.0,

        'Activity_Count': 999,
        'Activity_Duration_Minutes': 99999.0,
        'Activity_Cost': 99999.0,

        'Sleep_Duration_Minutes': 99999.0,
        'Avg_Sleep_Quality': 999.0,
        'Total_Awakenings': 999.0,

        'Day_Type': 'holiday',
        'Work_Status': 'leave',
        'Health_Impact': 'high',
        'Travel': 'yes',
        'Stress_Level': 999.0,
        'Sleep_Hours': 999.0,
        'Social_Activity': 'high',
        'Special_Event': 'future_event',
        'Location': 'future_location',
    }

    rows_with_future = (
        historical_rows
        + [future_row]
    )

    features_after = create_history_features(
        target_row,
        rows_with_future,
    )

    assert_not_changed(
        features_before,
        features_after,
        'Future row affected historical features.',
    )

    print(
        'Future row exclusion: PASSED'
    )


# ==========================================================
# TEST 3
# SAME WEEKDAY FUTURE LEAKAGE
# ==========================================================

def test_same_weekday_future_exclusion():
    """
    A future row with the same weekday as the target must
    still be ignored.
    """

    historical_rows = build_test_rows()
    target_row = build_target_row()

    features_before = create_history_features(
        target_row,
        historical_rows,
    )

    # 2026-08-18 is also Tuesday, same weekday as target.
    future_same_weekday = {
        'Date': date(2026, 8, 18),

        'Expense_Total': 500000.0,
        'Income_Total': 500000.0,
        'Event_Count': 500,

        'Health_Record_Count': 500,
        'Max_Health_Severity': 500.0,
        'Avg_Energy_Level': 500.0,

        'Activity_Count': 500,
        'Activity_Duration_Minutes': 50000.0,
        'Activity_Cost': 50000.0,

        'Sleep_Duration_Minutes': 50000.0,
        'Avg_Sleep_Quality': 500.0,
        'Total_Awakenings': 500.0,

        'Day_Type': 'holiday',
        'Work_Status': 'leave',
        'Health_Impact': 'high',
        'Travel': 'yes',
        'Stress_Level': 500.0,
        'Sleep_Hours': 500.0,
        'Social_Activity': 'high',
        'Special_Event': 'future',
        'Location': 'future',
    }

    rows_with_future = (
        historical_rows
        + [future_same_weekday]
    )

    features_after = create_history_features(
        target_row,
        rows_with_future,
    )

    assert_not_changed(
        features_before,
        features_after,
        'Future same-weekday row affected same-weekday history.',
    )

    print(
        'Same-weekday future exclusion: PASSED'
    )


# ==========================================================
# TEST 4
# PREVIOUS DAY MUST BE STRICTLY BEFORE TARGET
# ==========================================================

def test_previous_day_boundary():
    """
    The previous-day features must come from a date strictly
    before the target date.
    """

    historical_rows = build_test_rows()
    target_row = build_target_row()

    features = create_history_features(
        target_row,
        historical_rows,
    )

    # The latest historical row is 2026-08-10.
    expected_expense = 150.0
    expected_income = 500.0

    assert_equal(
        features[
            'Previous_Day_Expense'
        ],
        expected_expense,
        'Previous day expense is incorrect.',
    )

    assert_equal(
        features[
            'Previous_Day_Income'
        ],
        expected_income,
        'Previous day income is incorrect.',
    )

    assert_equal(
        features[
            'Previous_Day_Balance'
        ],
        expected_income - expected_expense,
        'Previous day balance is incorrect.',
    )

    print(
        'Previous-day temporal boundary: PASSED'
    )


# ==========================================================
# TEST 5
# SAME WEEKDAY MUST ONLY CONTAIN PAST ROWS
# ==========================================================

def test_same_weekday_temporal_boundary():
    """
    Same weekday history must contain only rows strictly
    before the target date.
    """

    historical_rows = build_test_rows()
    target_row = build_target_row()

    features = create_history_features(
        target_row,
        historical_rows,
    )

    # Target is Tuesday.
    # Historical Tuesday in this dataset:
    # 2026-08-04 would be before the available rows,
    # so there are no same-weekday records in the test data.
    #
    # Therefore Same_Weekday_Count must be zero.
    assert_equal(
        features[
            'Same_Weekday_Count'
        ],
        0,
        'Same weekday count incorrectly includes non-past data.',
    )

    print(
        'Same-weekday temporal boundary: PASSED'
    )


# ==========================================================
# TEST 6
# TARGET DATE ITSELF MUST NOT BE HISTORICAL
# ==========================================================

def test_target_date_exclusion():
    """
    If the target row itself is accidentally inserted into
    previous_rows, create_history_features must still reject
    it because the comparison is strictly < target_date.
    """

    historical_rows = build_test_rows()
    target_row = build_target_row()

    features_before = create_history_features(
        target_row,
        historical_rows,
    )

    rows_with_target = (
        historical_rows
        + [deepcopy(target_row)]
    )

    features_after = create_history_features(
        target_row,
        rows_with_target,
    )

    assert_not_changed(
        features_before,
        features_after,
        'Target date was incorrectly accepted as historical data.',
    )

    print(
        'Target-date exclusion: PASSED'
    )


# ==========================================================
# TEST 7
# EMPTY HISTORY
# ==========================================================

def test_empty_history():
    """
    No historical rows must produce safe default features.
    """

    target_row = build_target_row()

    features = create_history_features(
        target_row,
        [],
    )

    if not features:
        raise AssertionError(
            'History feature builder returned no feature dictionary.'
        )

    if features[
        'Previous_Day_Expense'
    ] != 0.0:

        raise AssertionError(
            'Previous day expense default is incorrect.'
        )

    if features[
        'Same_Weekday_Count'
    ] != 0:

        raise AssertionError(
            'Same weekday count default is incorrect.'
        )

    print(
        'Empty history handling: PASSED'
    )


# ==========================================================
# MAIN TEST
# ==========================================================

def test_history_features():

    print(
        '========== HISTORY FEATURES TEST =========='
    )

    test_target_day_outcome_independence()

    test_future_row_exclusion()

    test_same_weekday_future_exclusion()

    test_previous_day_boundary()

    test_same_weekday_temporal_boundary()

    test_target_date_exclusion()

    test_empty_history()

    print(
        '========== HISTORY FEATURES TEST PASSED =========='
    )


if __name__ == '__main__':
    test_history_features()