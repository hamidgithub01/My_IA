from datetime import date, timedelta

from ml.features.lags import (
    create_lag_features,
)


# ==========================================================
# TEST HELPERS
# ==========================================================

def make_row(
    row_date,
    expense=0.0,
    income=0.0,
    events=0,
    health=0.0,
    activity=0.0,
    sleep=0.0,
):
    return {
        'Date': row_date,
        'Expense_Total': expense,
        'Income_Total': income,
        'Event_Count': events,
        'Max_Health_Severity': health,
        'Activity_Duration_Minutes': activity,
        'Sleep_Duration_Minutes': sleep,
    }


def assert_equal(
    actual,
    expected,
    message,
):
    if actual != expected:
        raise AssertionError(
            f'{message}\n'
            f'Expected: {expected}\n'
            f'Actual: {actual}'
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
            f'Actual: {actual}'
        )


# ==========================================================
# TEST 1
# TARGET-DAY OUTCOME INDEPENDENCE
# ==========================================================

def test_target_day_outcome_independence():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [
        make_row(
            target_date - timedelta(days=1),
            expense=100.0,
            income=200.0,
            events=2,
            health=3.0,
            activity=60.0,
            sleep=420.0,
        )
    ]

    target_row_a = make_row(
        target_date,
        expense=500.0,
        income=900.0,
        events=20,
        health=10.0,
        activity=500.0,
        sleep=1000.0,
    )

    target_row_b = make_row(
        target_date,
        expense=99999.0,
        income=88888.0,
        events=999,
        health=999.0,
        activity=9999.0,
        sleep=9999.0,
    )

    features_a = create_lag_features(
        target_row_a,
        previous_rows,
    )

    features_b = create_lag_features(
        target_row_b,
        previous_rows,
    )

    assert_equal(
        features_a,
        features_b,
        'Lag features depend on target-day outcomes.',
    )

    print(
        'Target-day outcome independence: PASSED'
    )


# ==========================================================
# TEST 2
# FUTURE ROW EXCLUSION
# ==========================================================

def test_future_row_exclusion():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [

        make_row(
            target_date - timedelta(days=1),
            expense=100.0,
        ),

        make_row(
            target_date + timedelta(days=1),
            expense=9999.0,
        ),

        make_row(
            target_date + timedelta(days=7),
            expense=8888.0,
        ),

        make_row(
            target_date + timedelta(days=28),
            expense=7777.0,
        ),
    ]

    features = create_lag_features(
        make_row(target_date),
        previous_rows,
    )

    assert_close(
        features['Lag_1_Expense'],
        100.0,
        'Future rows affected Lag_1.',
    )

    assert_close(
        features['Lag_7_Expense'],
        0.0,
        'Future rows affected Lag_7.',
    )

    assert_close(
        features['Lag_28_Expense'],
        0.0,
        'Future rows affected Lag_28.',
    )

    print(
        'Future row exclusion: PASSED'
    )


# ==========================================================
# TEST 3
# EXACT CALENDAR LAG
# ==========================================================

def test_exact_calendar_lag():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = []

    for days_ago in [
        1,
        2,
        3,
        7,
        14,
        28,
    ]:

        previous_rows.append(
            make_row(
                target_date
                - timedelta(days=days_ago),
                expense=float(days_ago * 100),
            )
        )

    features = create_lag_features(
        make_row(target_date),
        previous_rows,
    )

    expected = {
        'Lag_1_Expense': 100.0,
        'Lag_2_Expense': 200.0,
        'Lag_3_Expense': 300.0,
        'Lag_7_Expense': 700.0,
        'Lag_14_Expense': 1400.0,
        'Lag_28_Expense': 2800.0,
    }

    for feature_name, expected_value in expected.items():

        assert_close(
            features[feature_name],
            expected_value,
            f'Incorrect exact calendar lag: {feature_name}.',
        )

    print(
        'Exact calendar lag: PASSED'
    )


# ==========================================================
# TEST 4
# MISSING CALENDAR DAY
# ==========================================================

def test_missing_calendar_day():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [

        # One day ago exists.
        make_row(
            target_date - timedelta(days=1),
            expense=100.0,
        ),

        # Six days ago exists.
        make_row(
            target_date - timedelta(days=6),
            expense=600.0,
        ),
    ]

    features = create_lag_features(
        make_row(target_date),
        previous_rows,
    )

    assert_close(
        features['Lag_1_Expense'],
        100.0,
        'Lag_1 failed when available.',
    )

    # Seven calendar days ago does not exist.
    # The six-days-ago row must NOT be used.
    assert_close(
        features['Lag_7_Expense'],
        0.0,
        'Lag_7 incorrectly used a nearby row.',
    )

    print(
        'Missing calendar day handling: PASSED'
    )


# ==========================================================
# TEST 5
# LAG 1 BOUNDARY
# ==========================================================

def test_lag_1_boundary():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [

        make_row(
            target_date - timedelta(days=1),
            expense=123.0,
        ),

        make_row(
            target_date,
            expense=9999.0,
        ),

        make_row(
            target_date + timedelta(days=1),
            expense=8888.0,
        ),
    ]

    features = create_lag_features(
        make_row(
            target_date,
            expense=5000.0,
        ),
        previous_rows,
    )

    assert_close(
        features['Lag_1_Expense'],
        123.0,
        'Lag_1 boundary is incorrect.',
    )

    print(
        'Lag 1 boundary: PASSED'
    )


# ==========================================================
# TEST 6
# LAG 2 BOUNDARY
# ==========================================================

def test_lag_2_boundary():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [

        make_row(
            target_date - timedelta(days=2),
            expense=222.0,
        ),

        make_row(
            target_date - timedelta(days=1),
            expense=111.0,
        ),

        make_row(
            target_date,
            expense=9999.0,
        ),
    ]

    features = create_lag_features(
        make_row(target_date),
        previous_rows,
    )

    assert_close(
        features['Lag_2_Expense'],
        222.0,
        'Lag_2 boundary is incorrect.',
    )

    print(
        'Lag 2 boundary: PASSED'
    )


# ==========================================================
# TEST 7
# LAG 3 BOUNDARY
# ==========================================================

def test_lag_3_boundary():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [

        make_row(
            target_date - timedelta(days=3),
            expense=333.0,
        ),

        make_row(
            target_date - timedelta(days=2),
            expense=222.0,
        ),

        make_row(
            target_date - timedelta(days=1),
            expense=111.0,
        ),
    ]

    features = create_lag_features(
        make_row(target_date),
        previous_rows,
    )

    assert_close(
        features['Lag_3_Expense'],
        333.0,
        'Lag_3 boundary is incorrect.',
    )

    print(
        'Lag 3 boundary: PASSED'
    )


# ==========================================================
# TEST 8
# LAG 7 BOUNDARY
# ==========================================================

def test_lag_7_boundary():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [

        make_row(
            target_date - timedelta(days=7),
            expense=700.0,
        ),

        make_row(
            target_date - timedelta(days=8),
            expense=800.0,
        ),
    ]

    features = create_lag_features(
        make_row(target_date),
        previous_rows,
    )

    assert_close(
        features['Lag_7_Expense'],
        700.0,
        'Lag_7 boundary is incorrect.',
    )

    print(
        'Lag 7 boundary: PASSED'
    )


# ==========================================================
# TEST 9
# LAG 14 BOUNDARY
# ==========================================================

def test_lag_14_boundary():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [

        make_row(
            target_date - timedelta(days=14),
            expense=1400.0,
        ),

        make_row(
            target_date - timedelta(days=15),
            expense=1500.0,
        ),
    ]

    features = create_lag_features(
        make_row(target_date),
        previous_rows,
    )

    assert_close(
        features['Lag_14_Expense'],
        1400.0,
        'Lag_14 boundary is incorrect.',
    )

    print(
        'Lag 14 boundary: PASSED'
    )


# ==========================================================
# TEST 10
# LAG 28 BOUNDARY
# ==========================================================

def test_lag_28_boundary():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [

        make_row(
            target_date - timedelta(days=28),
            expense=2800.0,
        ),

        make_row(
            target_date - timedelta(days=29),
            expense=2900.0,
        ),
    ]

    features = create_lag_features(
        make_row(target_date),
        previous_rows,
    )

    assert_close(
        features['Lag_28_Expense'],
        2800.0,
        'Lag_28 boundary is incorrect.',
    )

    print(
        'Lag 28 boundary: PASSED'
    )


# ==========================================================
# TEST 11
# MULTIPLE FIELDS CONSISTENCY
# ==========================================================

def test_multiple_fields():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [

        make_row(
            target_date - timedelta(days=1),
            expense=100.0,
            income=500.0,
            events=3,
            health=4.0,
            activity=60.0,
            sleep=420.0,
        )
    ]

    features = create_lag_features(
        make_row(target_date),
        previous_rows,
    )

    assert_close(
        features['Lag_1_Expense'],
        100.0,
        'Lag_1_Expense is incorrect.',
    )

    assert_close(
        features['Lag_1_Income'],
        500.0,
        'Lag_1_Income is incorrect.',
    )

    assert_equal(
        features['Lag_1_Events'],
        3.0,
        'Lag_1_Events is incorrect.',
    )

    assert_close(
        features['Lag_1_Health_Severity'],
        4.0,
        'Lag_1_Health_Severity is incorrect.',
    )

    assert_close(
        features['Lag_1_Activity_Duration'],
        60.0,
        'Lag_1_Activity_Duration is incorrect.',
    )

    assert_close(
        features['Lag_1_Sleep_Duration'],
        420.0,
        'Lag_1_Sleep_Duration is incorrect.',
    )

    print(
        'Multiple fields consistency: PASSED'
    )


# ==========================================================
# TEST 12
# DUPLICATE DATE HANDLING
# ==========================================================

def test_duplicate_date_handling():

    target_date = date(
        2026,
        8,
        15,
    )

    previous_rows = [

        make_row(
            target_date - timedelta(days=1),
            expense=100.0,
        ),

        make_row(
            target_date - timedelta(days=1),
            expense=200.0,
        ),
    ]

    features = create_lag_features(
        make_row(target_date),
        previous_rows,
    )

    # The implementation uses the last row assigned
    # to the duplicated date.
    assert_close(
        features['Lag_1_Expense'],
        200.0,
        'Duplicate date handling is incorrect.',
    )

    print(
        'Duplicate date handling: PASSED'
    )


# ==========================================================
# TEST 13
# EMPTY HISTORY
# ==========================================================

def test_empty_history():

    target_date = date(
        2026,
        8,
        15,
    )

    features = create_lag_features(
        make_row(target_date),
        [],
    )

    for feature_name, value in features.items():

        if value != 0.0:
            raise AssertionError(
                f'Expected zero for empty history: '
                f'{feature_name} = {value}'
            )

    print(
        'Empty history handling: PASSED'
    )


# ==========================================================
# TEST 14
# INVALID TARGET DATE
# ==========================================================

def test_invalid_target_date():

    features = create_lag_features(
        {
            'Date': 'not-a-date',
            'Expense_Total': 9999.0,
        },
        [
            make_row(
                date(2026, 8, 14),
                expense=100.0,
            )
        ],
    )

    if not features:
        raise AssertionError(
            'Invalid target date should return '
            'the defined zero-filled lag structure.'
        )

    for feature_name, value in features.items():

        if value != 0.0:
            raise AssertionError(
                f'Expected zero for invalid target date: '
                f'{feature_name} = {value}'
            )

    print(
        'Invalid target date handling: PASSED'
    )


# ==========================================================
# RUN ALL TESTS
# ==========================================================

def test_lag_features():

    print(
        '========== LAG FEATURES TEST =========='
    )

    test_target_day_outcome_independence()

    test_future_row_exclusion()

    test_exact_calendar_lag()

    test_missing_calendar_day()

    test_lag_1_boundary()

    test_lag_2_boundary()

    test_lag_3_boundary()

    test_lag_7_boundary()

    test_lag_14_boundary()

    test_lag_28_boundary()

    test_multiple_fields()

    test_duplicate_date_handling()

    test_empty_history()

    test_invalid_target_date()

    print(
        '========== LAG FEATURES TEST PASSED =========='
    )


if __name__ == '__main__':
    test_lag_features()