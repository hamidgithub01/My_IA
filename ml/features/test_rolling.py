from datetime import date

from ml.features.rolling import (
    create_rolling_features,
)


# ==========================================================
# TEST DATA
# ==========================================================

def build_historical_rows():
    """
    Build deterministic historical rows covering more than
    30 calendar days.

    The values are deliberately easy to verify.
    """

    return [
        {
            'Date': date(2026, 7, 1),
            'Expense_Total': 100.0,
            'Income_Total': 200.0,
            'Max_Health_Severity': 1.0,
            'Avg_Energy_Level': 10.0,
            'Activity_Duration_Minutes': 10.0,
            'Sleep_Duration_Minutes': 300.0,
            'Avg_Sleep_Quality': 5.0,
        },

        {
            'Date': date(2026, 7, 15),
            'Expense_Total': 200.0,
            'Income_Total': 400.0,
            'Max_Health_Severity': 2.0,
            'Avg_Energy_Level': 20.0,
            'Activity_Duration_Minutes': 20.0,
            'Sleep_Duration_Minutes': 400.0,
            'Avg_Sleep_Quality': 6.0,
        },

        {
            'Date': date(2026, 7, 25),
            'Expense_Total': 300.0,
            'Income_Total': 600.0,
            'Max_Health_Severity': 3.0,
            'Avg_Energy_Level': 30.0,
            'Activity_Duration_Minutes': 30.0,
            'Sleep_Duration_Minutes': 500.0,
            'Avg_Sleep_Quality': 7.0,
        },

        {
            'Date': date(2026, 8, 1),
            'Expense_Total': 400.0,
            'Income_Total': 800.0,
            'Max_Health_Severity': 4.0,
            'Avg_Energy_Level': 40.0,
            'Activity_Duration_Minutes': 40.0,
            'Sleep_Duration_Minutes': 600.0,
            'Avg_Sleep_Quality': 8.0,
        },

        {
            'Date': date(2026, 8, 3),
            'Expense_Total': 500.0,
            'Income_Total': 1000.0,
            'Max_Health_Severity': 5.0,
            'Avg_Energy_Level': 50.0,
            'Activity_Duration_Minutes': 50.0,
            'Sleep_Duration_Minutes': 700.0,
            'Avg_Sleep_Quality': 9.0,
        },

        {
            'Date': date(2026, 8, 5),
            'Expense_Total': 600.0,
            'Income_Total': 1200.0,
            'Max_Health_Severity': 6.0,
            'Avg_Energy_Level': 60.0,
            'Activity_Duration_Minutes': 60.0,
            'Sleep_Duration_Minutes': 800.0,
            'Avg_Sleep_Quality': 10.0,
        },

        {
            'Date': date(2026, 8, 7),
            'Expense_Total': 700.0,
            'Income_Total': 1400.0,
            'Max_Health_Severity': 7.0,
            'Avg_Energy_Level': 70.0,
            'Activity_Duration_Minutes': 70.0,
            'Sleep_Duration_Minutes': 900.0,
            'Avg_Sleep_Quality': 11.0,
        },

        {
            'Date': date(2026, 8, 10),
            'Expense_Total': 800.0,
            'Income_Total': 1600.0,
            'Max_Health_Severity': 8.0,
            'Avg_Energy_Level': 80.0,
            'Activity_Duration_Minutes': 80.0,
            'Sleep_Duration_Minutes': 1000.0,
            'Avg_Sleep_Quality': 12.0,
        },
    ]


def build_target_row():
    """
    Target day.

    Actual target-day values must never affect rolling
    historical features.
    """

    return {
        'Date': date(2026, 8, 11),

        'Expense_Total': 999999.0,
        'Income_Total': 888888.0,

        'Max_Health_Severity': 999.0,
        'Avg_Energy_Level': 999.0,

        'Activity_Duration_Minutes': 99999.0,

        'Sleep_Duration_Minutes': 99999.0,
        'Avg_Sleep_Quality': 999.0,
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
            if before.get(key)
            != after.get(key)
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
    Changing target-day values must not affect any rolling
    historical feature.
    """

    historical_rows = build_historical_rows()
    target_row = build_target_row()

    before = create_rolling_features(
        target_row,
        historical_rows,
    )

    modified_target = dict(
        target_row
    )

    modified_target.update({

        'Expense_Total': 1234567.0,
        'Income_Total': 7654321.0,

        'Max_Health_Severity': 500.0,
        'Avg_Energy_Level': 500.0,

        'Activity_Duration_Minutes': 50000.0,

        'Sleep_Duration_Minutes': 50000.0,
        'Avg_Sleep_Quality': 500.0,
    })

    after = create_rolling_features(
        modified_target,
        historical_rows,
    )

    assert_not_changed(
        before,
        after,
        'Target-day data affected rolling historical features.',
    )

    print(
        'Target-day outcome independence: PASSED'
    )


# ==========================================================
# TEST 2
# FUTURE ROW EXCLUSION
# ==========================================================

def test_future_row_exclusion():
    """
    Adding a future row must not change rolling features.
    """

    historical_rows = build_historical_rows()
    target_row = build_target_row()

    before = create_rolling_features(
        target_row,
        historical_rows,
    )

    future_row = {
        'Date': date(2026, 8, 12),

        'Expense_Total': 9999999.0,
        'Income_Total': 9999999.0,

        'Max_Health_Severity': 9999.0,
        'Avg_Energy_Level': 9999.0,

        'Activity_Duration_Minutes': 999999.0,

        'Sleep_Duration_Minutes': 999999.0,
        'Avg_Sleep_Quality': 9999.0,
    }

    after = create_rolling_features(
        target_row,
        historical_rows + [future_row],
    )

    assert_not_changed(
        before,
        after,
        'Future row affected rolling features.',
    )

    print(
        'Future row exclusion: PASSED'
    )


# ==========================================================
# TEST 3
# TARGET DATE EXCLUSION
# ==========================================================

def test_target_date_exclusion():
    """
    If target row itself is accidentally included inside
    previous_rows, it must still be excluded.
    """

    historical_rows = build_historical_rows()
    target_row = build_target_row()

    before = create_rolling_features(
        target_row,
        historical_rows,
    )

    after = create_rolling_features(
        target_row,
        historical_rows + [target_row],
    )

    assert_not_changed(
        before,
        after,
        'Target date was included in rolling history.',
    )

    print(
        'Target-date exclusion: PASSED'
    )


# ==========================================================
# TEST 4
# 3-DAY WINDOW
# ==========================================================

def test_3_day_window():
    """
    Target: 2026-08-11

    3-day window:
        2026-08-08 <= date < 2026-08-11

    There are no records on Aug 8 or Aug 9.

    Aug 10 is included.
    """

    historical_rows = build_historical_rows()
    target_row = build_target_row()

    features = create_rolling_features(
        target_row,
        historical_rows,
    )

    assert_close(
        features[
            'Rolling_3D_Avg_Expense'
        ],
        800.0,
        '3-day expense window is incorrect.',
    )

    assert_close(
        features[
            'Rolling_3D_Avg_Income'
        ],
        1600.0,
        '3-day income window is incorrect.',
    )

    assert_close(
        features[
            'Rolling_3D_Avg_Balance'
        ],
        800.0,
        '3-day balance window is incorrect.',
    )

    print(
        '3-day window boundary: PASSED'
    )


# ==========================================================
# TEST 5
# 7-DAY WINDOW
# ==========================================================

def test_7_day_window():
    """
    7-day window:

        2026-08-04 <= date < 2026-08-11

    Included:
        Aug 5
        Aug 7
        Aug 10

    Excluded:
        Aug 3
        Aug 11
        future dates
    """

    historical_rows = build_historical_rows()
    target_row = build_target_row()

    features = create_rolling_features(
        target_row,
        historical_rows,
    )

    expected_expense = (
        600.0
        + 700.0
        + 800.0
    ) / 3

    expected_income = (
        1200.0
        + 1400.0
        + 1600.0
    ) / 3

    assert_close(
        features[
            'Rolling_7D_Avg_Expense'
        ],
        expected_expense,
        '7-day expense window is incorrect.',
    )

    assert_close(
        features[
            'Rolling_7D_Avg_Income'
        ],
        expected_income,
        '7-day income window is incorrect.',
    )

    assert_close(
        features[
            'Rolling_7D_Avg_Balance'
        ],
        expected_income - expected_expense,
        '7-day balance window is incorrect.',
    )

    print(
        '7-day window boundary: PASSED'
    )


# ==========================================================
# TEST 6
# 14-DAY WINDOW
# ==========================================================

def test_14_day_window():
    """
    14-day window:

        2026-07-28 <= date < 2026-08-11

    Included:
        Aug 1
        Aug 3
        Aug 5
        Aug 7
        Aug 10
    """

    historical_rows = build_historical_rows()
    target_row = build_target_row()

    features = create_rolling_features(
        target_row,
        historical_rows,
    )

    expenses = [
        400.0,
        500.0,
        600.0,
        700.0,
        800.0,
    ]

    incomes = [
        800.0,
        1000.0,
        1200.0,
        1400.0,
        1600.0,
    ]

    expected_expense = sum(
        expenses
    ) / len(expenses)

    expected_income = sum(
        incomes
    ) / len(incomes)

    assert_close(
        features[
            'Rolling_14D_Avg_Expense'
        ],
        expected_expense,
        '14-day expense window is incorrect.',
    )

    assert_close(
        features[
            'Rolling_14D_Avg_Income'
        ],
        expected_income,
        '14-day income window is incorrect.',
    )

    print(
        '14-day window boundary: PASSED'
    )


# ==========================================================
# TEST 7
# 30-DAY WINDOW
# ==========================================================

def test_30_day_window():
    """
    30-day window:

        2026-07-12 <= date < 2026-08-11

    Included:
        Jul 15
        Jul 25
        Aug 1
        Aug 3
        Aug 5
        Aug 7
        Aug 10

    Jul 1 is excluded.
    """

    historical_rows = build_historical_rows()
    target_row = build_target_row()

    features = create_rolling_features(
        target_row,
        historical_rows,
    )

    expenses = [
        200.0,
        300.0,
        400.0,
        500.0,
        600.0,
        700.0,
        800.0,
    ]

    expected_expense = sum(
        expenses
    ) / len(expenses)

    assert_close(
        features[
            'Rolling_30D_Avg_Expense'
        ],
        expected_expense,
        '30-day expense window is incorrect.',
    )

    print(
        '30-day window boundary: PASSED'
    )


# ==========================================================
# TEST 8
# BALANCE CALCULATION
# ==========================================================

def test_balance_calculation():
    """
    Verify:

        Balance = Income - Expense
    """

    historical_rows = build_historical_rows()
    target_row = build_target_row()

    features = create_rolling_features(
        target_row,
        historical_rows,
    )

    # 3-day:
    #
    # Income:
    #   1600
    #
    # Expense:
    #   800
    #
    # Balance:
    #   800

    assert_close(
        features[
            'Rolling_3D_Avg_Balance'
        ],
        800.0,
        'Rolling balance calculation is incorrect.',
    )

    print(
        'Rolling balance calculation: PASSED'
    )


# ==========================================================
# TEST 9
# EMPTY HISTORY
# ==========================================================

def test_empty_history():
    """
    Empty historical data must produce safe zero values.
    """

    target_row = build_target_row()

    features = create_rolling_features(
        target_row,
        [],
    )

    if not features:
        raise AssertionError(
            'Rolling feature builder returned no features.'
        )

    for name, value in features.items():

        if value != 0.0:
            raise AssertionError(
                f'Expected zero for empty history: '
                f'{name} = {value}'
            )

    print(
        'Empty history handling: PASSED'
    )


# ==========================================================
# TEST 10
# INVALID TARGET DATE
# ==========================================================

def test_invalid_target_date():
    """
    Invalid target dates must safely return an empty
    feature dictionary.
    """

    target_row = {
        'Date': 'not-a-date',
    }

    features = create_rolling_features(
        target_row,
        build_historical_rows(),
    )

    assert_equal(
        features,
        {},
        'Invalid target date should return an empty dictionary.',
    )

    print(
        'Invalid target date handling: PASSED'
    )


# ==========================================================
# MAIN
# ==========================================================

def test_rolling_features():

    print(
        '========== ROLLING FEATURES TEST =========='
    )

    test_target_day_outcome_independence()

    test_future_row_exclusion()

    test_target_date_exclusion()

    test_3_day_window()

    test_7_day_window()

    test_14_day_window()

    test_30_day_window()

    test_balance_calculation()

    test_empty_history()

    test_invalid_target_date()

    print(
        '========== ROLLING FEATURES TEST PASSED =========='
    )


if __name__ == '__main__':
    test_rolling_features()