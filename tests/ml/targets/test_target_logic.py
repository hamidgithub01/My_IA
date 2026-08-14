# =========================================================
# TARGET LOGIC TESTS
# =========================================================

from ml.targets.build import (
    build_target_dataset,
)


# =========================================================
# TEST DATA
# =========================================================

def create_test_dataset():
    """
    Create a small deterministic dataset.

    Each day has unique financial values so that
    incorrect future-day alignment is immediately visible.
    """

    return [

        {
            'Date': '2026-01-01',
            'Expense_Total': 100,
            'Income_Total': 1000,
            'Travel': 'No',
        },

        {
            'Date': '2026-01-02',
            'Expense_Total': 200,
            'Income_Total': 1100,
            'Travel': 'No',
        },

        {
            'Date': '2026-01-03',
            'Expense_Total': 300,
            'Income_Total': 1200,
            'Travel': 'No',
        },

        {
            'Date': '2026-01-04',
            'Expense_Total': 400,
            'Income_Total': 1300,
            'Travel': 'No',
        },

        {
            'Date': '2026-01-05',
            'Expense_Total': 500,
            'Income_Total': 1400,
            'Travel': 'No',
        },

        {
            'Date': '2026-01-06',
            'Expense_Total': 600,
            'Income_Total': 1500,
            'Travel': 'No',
        },

        {
            'Date': '2026-01-07',
            'Expense_Total': 700,
            'Income_Total': 1600,
            'Travel': 'No',
        },

        {
            'Date': '2026-01-08',
            'Expense_Total': 800,
            'Income_Total': 1700,
            'Travel': 'No',
        },
    ]


# =========================================================
# TEST 1
# =========================================================

def test_daily_financial_alignment():
    """
    Verify that:

        1D -> T+1
        2D -> T+2
        ...
        7D -> T+7
    """

    data = create_test_dataset()

    dataset = build_target_dataset(
        prepared_data=data
    )

    first_row = dataset[0]

    expected_expenses = {
        '1D': 200,
        '2D': 300,
        '3D': 400,
        '4D': 500,
        '5D': 600,
        '6D': 700,
        '7D': 800,
    }

    for horizon, expected_value in (
        expected_expenses.items()
    ):

        column = (
            f'Target_Expense_Total_{horizon}'
        )

        actual_value = first_row[column]

        assert actual_value == expected_value, (
            f'{column}: '
            f'expected {expected_value}, '
            f'got {actual_value}'
        )


# =========================================================
# TEST 2
# =========================================================

def test_daily_income_alignment():
    """
    Verify that income targets point to the
    correct future day.
    """

    data = create_test_dataset()

    dataset = build_target_dataset(
        prepared_data=data
    )

    first_row = dataset[0]

    expected_income = {
        '1D': 1100,
        '2D': 1200,
        '3D': 1300,
        '4D': 1400,
        '5D': 1500,
        '6D': 1600,
        '7D': 1700,
    }

    for horizon, expected_value in (
        expected_income.items()
    ):

        column = (
            f'Target_Income_Total_{horizon}'
        )

        actual_value = first_row[column]

        assert actual_value == expected_value, (
            f'{column}: '
            f'expected {expected_value}, '
            f'got {actual_value}'
        )


# =========================================================
# TEST 3
# =========================================================

def test_daily_balance_alignment():
    """
    Verify that the balance belongs to the
    exact future day.

    Balance = Income - Expense
    """

    data = create_test_dataset()

    dataset = build_target_dataset(
        prepared_data=data
    )

    first_row = dataset[0]

    expected_balance = {
        '1D': 900,
        '2D': 900,
        '3D': 900,
        '4D': 900,
        '5D': 900,
        '6D': 900,
        '7D': 900,
    }

    for horizon, expected_value in (
        expected_balance.items()
    ):

        column = (
            f'Target_Balance_{horizon}'
        )

        actual_value = first_row[column]

        assert actual_value == expected_value, (
            f'{column}: '
            f'expected {expected_value}, '
            f'got {actual_value}'
        )


# =========================================================
# TEST 4
# =========================================================

def test_daily_target_does_not_aggregate_future_days():
    """
    Verify that daily targets represent exactly
    one future day and do not sum multiple days.

    Example:

        T+1 = 200
        T+2 = 300
        T+3 = 400

    Therefore:

        Target_Expense_Total_3D = 400

    NOT:

        200 + 300 + 400 = 900
    """

    data = create_test_dataset()

    dataset = build_target_dataset(
        prepared_data=data
    )

    first_row = dataset[0]

    assert (
        first_row[
            'Target_Expense_Total_3D'
        ]
        == 400
    )

    assert (
        first_row[
            'Target_Expense_Total_3D'
        ]
        != 900
    )


# =========================================================
# TEST 5
# =========================================================

def test_daily_target_alignment_for_middle_row():
    """
    Verify alignment from a row in the middle
    of the dataset, not only the first row.
    """

    data = create_test_dataset()

    dataset = build_target_dataset(
        prepared_data=data
    )

    # T = 2026-01-03
    row = dataset[2]

    expected = {
        '1D': 400,
        '2D': 500,
        '3D': 600,
        '4D': 700,
        '5D': 800,
    }

    for horizon, expected_value in (
        expected.items()
    ):

        column = (
            f'Target_Expense_Total_{horizon}'
        )

        actual_value = row[column]

        assert actual_value == expected_value, (
            f'Date={row["Date"]}, '
            f'{column}: '
            f'expected {expected_value}, '
            f'got {actual_value}'
        )


# =========================================================
# TEST 6
# =========================================================

def test_future_targets_are_nan_when_future_day_does_not_exist():
    """
    Verify that targets become NaN when the required
    future day does not exist.
    """

    data = create_test_dataset()

    dataset = build_target_dataset(
        prepared_data=data
    )

    last_row = dataset[-1]

    for horizon in (
        '1D',
        '2D',
        '3D',
        '4D',
        '5D',
        '6D',
        '7D',
    ):

        column = (
            f'Target_Expense_Total_{horizon}'
        )

        value = last_row[column]

        assert value != value, (
            f'{column} should be NaN, '
            f'but got {value}'
        )


# =========================================================
# TEST 7
# =========================================================

def test_daily_targets_do_not_use_current_day():
    """
    Verify that daily targets never point to T itself.

    The current day has Expense_Total = 100.
    Therefore 1D must be 200, not 100.
    """

    data = create_test_dataset()

    dataset = build_target_dataset(
        prepared_data=data
    )

    first_row = dataset[0]

    assert (
        first_row[
            'Target_Expense_Total_1D'
        ]
        != 100
    )

    assert (
        first_row[
            'Target_Expense_Total_1D'
        ]
        == 200
    )


# =========================================================
# TEST RUNNER
# =========================================================

if __name__ == '__main__':

    print()
    print(
        '========== TARGET LOGIC TESTS =========='
    )

    test_daily_financial_alignment()
    print(
        'PASS: Daily financial alignment'
    )

    test_daily_income_alignment()
    print(
        'PASS: Daily income alignment'
    )

    test_daily_balance_alignment()
    print(
        'PASS: Daily balance alignment'
    )

    test_daily_target_does_not_aggregate_future_days()
    print(
        'PASS: Daily targets do not aggregate'
    )

    test_daily_target_alignment_for_middle_row()
    print(
        'PASS: Middle-row alignment'
    )

    test_future_targets_are_nan_when_future_day_does_not_exist()
    print(
        'PASS: Missing future days -> NaN'
    )

    test_daily_targets_do_not_use_current_day()
    print(
        'PASS: Current day is not used as future target'
    )

    print()
    print(
        '========== ALL TARGET LOGIC TESTS PASSED =========='
    )