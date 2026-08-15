import pandas as pd

from ml.targets.target_engineering import (
HORIZONS,
TARGET_DEFINITIONS,
REQUIRED_SOURCE_COLUMNS,
calculate_next_value,
calculate_future_sum,
calculate_future_mean,
calculate_future_max,
calculate_future_count,
calculate_target_value,
create_date_map,
get_future_rows,
make_target_name,
get_target_columns,
create_targets_for_horizon,
validate_input_dataset,
validate_target_columns,
build_target_dataset,
)

# =========================================================

# TEST DATA

# =========================================================

def create_test_dataframe():
    """
    Create a deterministic Feature Dataset used only
    for Target Engineering tests.

    ```
    Dates are consecutive so that calendar-day boundaries
    can be tested precisely.
    """

    dates = pd.date_range(
        '2026-01-01',
        periods=10,
        freq='D',
    )

    dataframe = pd.DataFrame(
        {
            'Date': dates,

            'Stress_Level': [
                1, 2, 3, 4, 5,
                6, 7, 8, 9, 10,
            ],

            'Sleep_Hours': [
                8, 7, 6, 5, 4,
                3, 2, 1, 8, 7,
            ],

            'Social_Activity': [
                'no',
                'yes',
                'no',
                'yes',
                'no',
                'yes',
                'no',
                'yes',
                'no',
                'yes',
            ],

            'Work_Status': [
                'work',
                'off',
                'work',
                'off',
                'work',
                'off',
                'work',
                'off',
                'work',
                'off',
            ],

            'Activity_Count': [
                1, 2, 3, 4, 5,
                6, 7, 8, 9, 10,
            ],

            'Activity_Duration_Minutes': [
                10, 20, 30, 40, 50,
                60, 70, 80, 90, 100,
            ],

            'Event_Count': [
                0, 1, 0, 2, 0,
                3, 0, 4, 0, 5,
            ],

            'Expense_Total': [
                100, 200, 300, 400, 500,
                600, 700, 800, 900, 1000,
            ],

            'Income_Total': [
                1000, 1100, 1200, 1300, 1400,
                1500, 1600, 1700, 1800, 1900,
            ],

            'Max_Health_Severity': [
                0, 1, 2, 3, 4,
                5, 6, 7, 8, 9,
            ],

            'Avg_Energy_Level': [
                10, 9, 8, 7, 6,
                5, 4, 3, 2, 1,
            ],

            'Health_Record_Count': [
                0, 1, 0, 1, 0,
                1, 0, 1, 0, 1,
            ],

            'Location': [
                'home',
                'work',
                'home',
                'work',
                'home',
                'work',
                'home',
                'work',
                'home',
                'work',
            ],

            'Travel': [
                'no',
                'yes',
                'no',
                'yes',
                'no',
                'yes',
                'no',
                'yes',
                'no',
                'yes',
            ],
        }
    )

    return dataframe


# =========================================================

# BASIC TARGET DEFINITIONS

# =========================================================

def test_target_definitions():


    assert TARGET_DEFINITIONS

    for target_name, definition in (
        TARGET_DEFINITIONS.items()
    ):

        assert 'source' in definition
        assert 'aggregation' in definition
        assert 'type' in definition

        assert definition['source']
        assert definition['aggregation']
        assert definition['type']

    assert (
        REQUIRED_SOURCE_COLUMNS
        == {
            definition['source']
            for definition in TARGET_DEFINITIONS.values()
        }
    )


# =========================================================

# DATE MAP

# =========================================================

def test_create_date_map():


    dataframe = create_test_dataframe()

    date_map = create_date_map(
        dataframe
    )

    assert len(date_map) == len(
        dataframe
    )

    first_date = dataframe.iloc[0]['Date']

    assert first_date in date_map

    assert (
        date_map[first_date]['Expense_Total']
        == 100
    )


# =========================================================

# FUTURE ROW BOUNDARIES

# =========================================================

def test_future_rows_exclude_current_day():


    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-03'
    )

    future_rows = get_future_rows(
        dataframe,
        current_date,
        3,
    )

    expected_dates = [
        pd.Timestamp('2026-01-04'),
        pd.Timestamp('2026-01-05'),
        pd.Timestamp('2026-01-06'),
    ]

    assert list(
        future_rows['Date']
    ) == expected_dates

    assert (
        current_date
        not in set(future_rows['Date'])
    )


def test_future_rows_use_calendar_days():


    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-03'
    )

    future_rows = get_future_rows(
        dataframe,
        current_date,
        1,
    )

    assert len(
        future_rows
    ) == 1

    assert (
        future_rows.iloc[0]['Date']
        == pd.Timestamp('2026-01-04')
    )


def test_future_rows_respect_horizon_boundary():


    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-03'
    )

    future_rows = get_future_rows(
        dataframe,
        current_date,
        7,
    )

    assert (
        future_rows['Date'].min()
        == pd.Timestamp('2026-01-04')
    )

    assert (
        future_rows['Date'].max()
        == pd.Timestamp('2026-01-10')
    )
    

# =========================================================

# NEXT VALUE

# =========================================================

def test_next_value():

    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-03'
    )

    value = calculate_next_value(
        dataframe,
        current_date,
        'Expense_Total',
    )

    assert value == 400


def test_next_value_missing_future_day():


    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-10'
    )

    value = calculate_next_value(
        dataframe,
        current_date,
        'Expense_Total',
    )

    assert value is None


# =========================================================

# FUTURE AGGREGATIONS

# =========================================================

def test_future_sum():


    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-03'
    )

    future_rows = get_future_rows(
        dataframe,
        current_date,
        3,
    )

    result = calculate_future_sum(
        future_rows,
        'Expense_Total',
    )

    # 400 + 500 + 600
    assert result == 1500.0


def test_future_mean():


    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-03'
    )

    future_rows = get_future_rows(
        dataframe,
        current_date,
        3,
    )

    result = calculate_future_mean(
        future_rows,
        'Expense_Total',
    )

    assert result == 500.0


def test_future_max():


    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-03'
    )

    future_rows = get_future_rows(
        dataframe,
        current_date,
        3,
    )

    result = calculate_future_max(
        future_rows,
        'Expense_Total',
    )

    assert result == 600.0


def test_future_count():


    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-03'
    )

    future_rows = get_future_rows(
        dataframe,
        current_date,
        3,
    )

    result = calculate_future_count(
        future_rows,
        'Event_Count',
    )

    # Future Event_Count:
    # 2, 0, 3
    # Values > 0 = 2
    assert result == 2


# =========================================================

# TARGET VALUE

# =========================================================

def test_calculate_numeric_next_target():


    dataframe = create_test_dataframe()

    definition = {
        'source': 'Expense_Total',
        'aggregation': 'next_value',
        'type': 'numeric',
    }

    result = calculate_target_value(
        dataframe,
        pd.Timestamp('2026-01-03'),
        definition,
        1,
    )

    assert result == 400.0


def test_calculate_categorical_next_target():


    dataframe = create_test_dataframe()

    definition = {
        'source': 'Work_Status',
        'aggregation': 'next_value',
        'type': 'categorical',
    }

    result = calculate_target_value(
        dataframe,
        pd.Timestamp('2026-01-01'),
        definition,
        1,
    )

    assert result == 'off'


# =========================================================

# TARGET NAMING

# =========================================================

def test_target_name():


    assert (
        make_target_name(
            'Expense_Total',
            '1D',
        )
        == 'Target_Expense_Total_1D'
    )

    assert (
        make_target_name(
            'Stress_Level',
            '7D',
        )
        == 'Target_Stress_Level_7D'
    )


def test_target_columns():


    columns = get_target_columns()

    expected_count = (
        len(HORIZONS)
        * len(TARGET_DEFINITIONS)
    )

    assert len(columns) == expected_count

    assert (
        'Target_Expense_Total_1D'
        in columns
    )

    assert (
        'Target_Expense_Total_7D'
        in columns
    )

    assert (
        'Target_Expense_Total_30D'
        in columns
    )


# =========================================================

# HORIZON CREATION

# =========================================================

def test_create_targets_for_1d():


    dataframe = create_test_dataframe()

    result = create_targets_for_horizon(
        dataframe,
        horizon_name='1D',
        horizon_days=1,
    )

    column = (
        'Target_Expense_Total_1D'
    )

    assert column in result.columns

    # Jan 1 -> Jan 2 = 200
    assert (
        result.iloc[0][column]
        == 200.0
    )

    # Jan 3 -> Jan 4 = 400
    assert (
        result.iloc[2][column]
        == 400.0
    )


def test_create_targets_for_7d():


    dataframe = create_test_dataframe()

    result = create_targets_for_horizon(
        dataframe,
        horizon_name='7D',
        horizon_days=7,
    )

    column = (
        'Target_Expense_Total_7D'
    )

    assert column in result.columns

    # Jan 1 future rows:
    # Jan 2 ... Jan 8
    #
    # 200 + 300 + 400 + 500
    # + 600 + 700 + 800
    #
    # But Expense_Total uses next_value,
    # therefore only T+1 is used.
    assert (
        result.iloc[0][column]
        == 200.0
    )


def test_create_targets_for_30d():


    dataframe = create_test_dataframe()

    result = create_targets_for_horizon(
        dataframe,
        horizon_name='30D',
        horizon_days=30,
    )

    column = (
        'Target_Expense_Total_30D'
    )

    assert column in result.columns

    # next_value aggregation still means T+1.
    assert (
        result.iloc[0][column]
        == 200.0
    )


# =========================================================

# TARGET-DAY INDEPENDENCE

# =========================================================

def test_target_does_not_use_current_day():


    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-03'
    )

    definition = {
        'source': 'Expense_Total',
        'aggregation': 'next_value',
        'type': 'numeric',
    }

    original = calculate_target_value(
        dataframe,
        current_date,
        definition,
        1,
    )

    modified = dataframe.copy()

    mask = (
        modified['Date']
        == current_date
    )

    modified.loc[
        mask,
        'Expense_Total'
    ] = 999999999.0

    changed = calculate_target_value(
        modified,
        current_date,
        definition,
        1,
    )

    assert original == changed
    

# =========================================================

# FUTURE-DAY DEPENDENCE

# =========================================================

def test_target_changes_when_future_value_changes():


    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-03'
    )

    definition = {
        'source': 'Expense_Total',
        'aggregation': 'next_value',
        'type': 'numeric',
    }

    original = calculate_target_value(
        dataframe,
        current_date,
        definition,
        1,
    )

    modified = dataframe.copy()

    mask = (
        modified['Date']
        == pd.Timestamp('2026-01-04')
    )

    modified.loc[
        mask,
        'Expense_Total'
    ] = 9999

    changed = calculate_target_value(
        modified,
        current_date,
        definition,
        1,
    )

    assert original != changed
    assert changed == 9999.0


# =========================================================

# INPUT VALIDATION

# =========================================================

def test_validate_input_dataset():


    dataframe = create_test_dataframe()

    result = validate_input_dataset(
        dataframe
    )

    assert (
        result['Date']
        .is_monotonic_increasing
    )

    assert not (
        result['Date']
        .duplicated()
        .any()
    )


def test_validate_input_rejects_duplicate_dates():


    dataframe = create_test_dataframe()

    duplicate = dataframe.iloc[
        [0]
    ].copy()

    dataframe = pd.concat(
        [
            dataframe,
            duplicate,
        ],
        ignore_index=True,
    )

    try:

        validate_input_dataset(
            dataframe
        )

    except ValueError as error:

        assert (
            'duplicate dates'
            in str(error).lower()
        )

    else:

        raise AssertionError(
            'Duplicate dates were not rejected.'
        )


def test_validate_input_rejects_missing_columns():


    dataframe = create_test_dataframe()

    dataframe = dataframe.drop(
        columns=[
            'Expense_Total'
        ]
    )

    try:

        validate_input_dataset(
            dataframe
        )

    except ValueError as error:

        assert (
            'missing required columns'
            in str(error).lower()
        )

    else:

        raise AssertionError(
            'Missing source column was not rejected.'
        )


# =========================================================

# TARGET COLUMN VALIDATION

# =========================================================

def test_validate_target_columns():


    dataframe = create_test_dataframe()

    dataframe = create_targets_for_horizon(
        dataframe,
        '1D',
        1,
    )

    dataframe = create_targets_for_horizon(
        dataframe,
        '7D',
        7,
    )

    dataframe = create_targets_for_horizon(
        dataframe,
        '30D',
        30,
    )

    result = validate_target_columns(
        dataframe
    )

    assert result is not None


def test_validate_target_columns_rejects_missing():


    dataframe = create_test_dataframe()

    try:

        validate_target_columns(
            dataframe
        )

    except ValueError as error:

        assert (
            'missing target columns'
            in str(error).lower()
        )

    else:

        raise AssertionError(
            'Missing target columns were not rejected.'
        )


# =========================================================

# FULL TARGET DATASET

# =========================================================

def test_full_target_dataset_structure():


    dataframe = create_test_dataframe()

    dataframe = create_targets_for_horizon(
        dataframe,
        '1D',
        1,
    )

    dataframe = create_targets_for_horizon(
        dataframe,
        '7D',
        7,
    )

    dataframe = create_targets_for_horizon(
        dataframe,
        '30D',
        30,
    )

    validate_target_columns(
        dataframe
    )

    expected_target_count = (
        len(HORIZONS)
        * len(TARGET_DEFINITIONS)
    )

    generated_target_columns = [
        column
        for column in dataframe.columns
        if column.startswith('Target_')
    ]

    assert (
        len(generated_target_columns)
        == expected_target_count
    )


# =========================================================

# TARGET FUTURE BOUNDARY

# =========================================================

def test_last_row_has_no_next_day_target():


    dataframe = create_test_dataframe()

    result = create_targets_for_horizon(
        dataframe,
        '1D',
        1,
    )

    column = (
        'Target_Expense_Total_1D'
    )

    assert pd.isna(
        result.iloc[-1][column]
    )


def test_target_does_not_use_rows_beyond_available_data():

    dataframe = create_test_dataframe()

    current_date = pd.Timestamp(
        '2026-01-08'
    )

    definition = {
        'source': 'Expense_Total',
        'aggregation': 'next_value',
        'type': 'numeric',
    }

    result = calculate_target_value(
        dataframe,
        current_date,
        definition,
        1,
    )

    assert result == 900.0


# =========================================================

# FULL PIPELINE TEST

# =========================================================

def test_build_target_dataset():

    dataframe = create_test_dataframe()

    # The real build_target_dataset() loads the production
    # Feature Dataset, so this test validates the complete
    # target-generation sequence independently using the
    # deterministic test dataset.

    dataframe = validate_input_dataset(
        dataframe
    )

    for horizon_name, horizon_days in (
        HORIZONS.items()
    ):

        dataframe = create_targets_for_horizon(
            dataframe,
            horizon_name,
            horizon_days,
        )

    dataframe = validate_target_columns(
        dataframe
    )

    assert not dataframe.empty

    assert (
        len(
            get_target_columns()
        )
        == len(
            [
                column
                for column in dataframe.columns
                if column.startswith('Target_')
            ]
        )
    )


# =========================================================

# RUN ALL TESTS

# =========================================================

def run_tests():


    tests = [
        test_target_definitions,
        test_create_date_map,

        test_future_rows_exclude_current_day,
        test_future_rows_use_calendar_days,
        test_future_rows_respect_horizon_boundary,

        test_next_value,
        test_next_value_missing_future_day,

        test_future_sum,
        test_future_mean,
        test_future_max,
        test_future_count,

        test_calculate_numeric_next_target,
        test_calculate_categorical_next_target,

        test_target_name,
        test_target_columns,

        test_create_targets_for_1d,
        test_create_targets_for_7d,
        test_create_targets_for_30d,

        test_target_does_not_use_current_day,
        test_target_changes_when_future_value_changes,

        test_validate_input_dataset,
        test_validate_input_rejects_duplicate_dates,
        test_validate_input_rejects_missing_columns,

        test_validate_target_columns,
        test_validate_target_columns_rejects_missing,

        test_full_target_dataset_structure,

        test_last_row_has_no_next_day_target,
        test_target_does_not_use_rows_beyond_available_data,

        test_build_target_dataset,
    ]

    print(
        '========== TARGET ENGINEERING TEST =========='
    )

    for test in tests:

        test()

        print(
            f'{test.__name__}: PASSED'
        )

    print(
        '========== TARGET ENGINEERING TEST PASSED =========='
    )


if __name__ == '__main__':


    run_tests()
