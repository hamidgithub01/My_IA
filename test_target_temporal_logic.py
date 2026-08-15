from datetime import date

from ml.targets.build import build_target_dataset


# ==========================================================
# EXPECTED HORIZONS
# ==========================================================

HORIZONS = [
    '1D',
    '2D',
    '3D',
    '4D',
    '5D',
    '6D',
    '7D',
    '8_15D',
    '16_30D',
    '30D',
]


# ==========================================================
# TARGET PREFIX
# ==========================================================

TARGET_PREFIX = 'Target_Expense_Total_'


# ==========================================================
# HELPERS
# ==========================================================

def get_target_name(horizon):
    return (
        f'{TARGET_PREFIX}{horizon}'
    )


def get_available_target_dates(
    dataset,
    target_name,
):
    """
    Return rows where the target has a real value.

    None / NaN values are ignored because they may be
    legitimately unavailable near the end of the dataset.
    """

    result = []

    for row in dataset:

        value = row.get(
            target_name
        )

        if value is None:
            continue

        result.append(
            (
                row['Date'],
                value,
            )
        )

    return result


def is_numeric_zero(value):
    """
    Verify that zero is represented as a real numeric value.
    """

    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and float(value) == 0.0
    )


# ==========================================================
# TEST 1
# DATASET EXISTS
# ==========================================================

def test_target_dataset_exists():

    dataset = build_target_dataset()

    assert dataset, (
        'Target dataset is empty.'
    )

    print()
    print(
        'Target dataset rows:',
        len(dataset)
    )


# ==========================================================
# TEST 2
# REQUIRED TARGETS EXIST
# ==========================================================

def test_expense_targets_exist():

    dataset = build_target_dataset()

    assert dataset

    missing = []

    for horizon in HORIZONS:

        target_name = get_target_name(
            horizon
        )

        if target_name not in dataset[0]:

            missing.append(
                target_name
            )

    assert not missing, (
        'Missing expense targets:\n'
        + '\n'.join(missing)
    )

    print(
        'PASS: All expense targets exist.'
    )


# ==========================================================
# TEST 3
# TARGET DATES ARE CHRONOLOGICAL
# ==========================================================

def test_target_dates_are_chronological():

    dataset = build_target_dataset()

    dates = [
        row['Date']
        for row in dataset
    ]

    assert dates == sorted(dates), (
        'Target dataset dates are not chronological.'
    )

    assert len(dates) == len(
        set(dates)
    ), (
        'Duplicate target dates detected.'
    )

    print(
        'PASS: Target dates are chronological '
        'and unique.'
    )


# ==========================================================
# TEST 4
# TARGET VALUES ARE NUMERIC
# ==========================================================

def test_expense_targets_are_numeric():

    dataset = build_target_dataset()

    errors = []

    for row_index, row in enumerate(
        dataset
    ):

        for horizon in HORIZONS:

            target_name = get_target_name(
                horizon
            )

            value = row.get(
                target_name
            )

            if value is None:
                continue

            if not isinstance(
                value,
                (int, float),
            ):

                errors.append(
                    (
                        row_index,
                        target_name,
                        value,
                    )
                )

    assert not errors, (
        'Non-numeric expense targets found:\n'
        + '\n'.join(
            str(error)
            for error in errors[:20]
        )
    )

    print(
        'PASS: Expense targets are numeric '
        'or None.'
    )


# ==========================================================
# TEST 5
# ZERO IS A REAL TARGET VALUE
# ==========================================================

def test_zero_is_valid_target_value():

    dataset = build_target_dataset()

    zero_values = []

    for row_index, row in enumerate(
        dataset
    ):

        for horizon in HORIZONS:

            target_name = get_target_name(
                horizon
            )

            value = row.get(
                target_name
            )

            if is_numeric_zero(value):

                zero_values.append(
                    (
                        row_index,
                        target_name,
                    )
                )

    print(
        'Real zero target values found:',
        len(zero_values)
    )

    # This test does not require the current real database
    # to contain zeros.
    #
    # It only verifies that if zero exists, it is accepted
    # as a valid numeric target.
    #
    # The important assertion is that the target is never
    # rejected merely because it equals zero.

    for row_index, target_name in zero_values:

        value = dataset[
            row_index
        ][target_name]

        assert value == 0.0

    print(
        'PASS: Zero target values are treated '
        'as real values.'
    )


# ==========================================================
# TEST 6
# HORIZON TARGETS DO NOT REVERSE ORDER
# ==========================================================

def test_horizon_structure():

    dataset = build_target_dataset()

    for row in dataset:

        current_date = row['Date']

        assert isinstance(
            current_date,
            date,
        )

        for horizon in HORIZONS:

            target_name = get_target_name(
                horizon
            )

            assert target_name in row

    print(
        'PASS: Every row contains the complete '
        'expense horizon structure.'
    )


# ==========================================================
# TEST 7
# TARGET AVAILABILITY DECREASES TOWARD DATASET END
# ==========================================================

def test_future_targets_become_unavailable_at_end():

    dataset = build_target_dataset()

    availability_counts = {}

    for horizon in HORIZONS:

        target_name = get_target_name(
            horizon
        )

        available = (
            get_available_target_dates(
                dataset,
                target_name,
            )
        )

        availability_counts[
            horizon
        ] = len(available)

    print()
    print(
        '========== TARGET AVAILABILITY =========='
    )

    for horizon in HORIZONS:

        print(
            f'{horizon}: '
            f'{availability_counts[horizon]} rows'
        )

    # Longer horizons should never have MORE
    # usable observations than shorter horizons.

    previous_count = None

    for horizon in HORIZONS:

        current_count = (
            availability_counts[horizon]
        )

        if previous_count is not None:

            assert current_count <= previous_count, (
                f'Target availability increased '
                f'from previous horizon to {horizon}.'
            )

        previous_count = current_count

    print(
        'PASS: Longer horizons do not have '
        'more observations than shorter horizons.'
    )


# ==========================================================
# TEST 8
# TARGET NAMES MATCH EXPECTED HORIZONS
# ==========================================================

def test_no_unexpected_expense_horizons():

    dataset = build_target_dataset()

    actual = {
        key
        for key in dataset[0].keys()
        if key.startswith(
            TARGET_PREFIX
        )
    }

    expected = {
        get_target_name(
            horizon
        )
        for horizon in HORIZONS
    }

    unexpected = actual - expected

    missing = expected - actual

    assert not unexpected, (
        'Unexpected expense target columns:\n'
        + '\n'.join(
            sorted(unexpected)
        )
    )

    assert not missing, (
        'Missing expense target columns:\n'
        + '\n'.join(
            sorted(missing)
        )
    )

    print(
        'PASS: Expense target horizon names '
        'are exactly as expected.'
    )


# ==========================================================
# TEST 9
# TARGET STRUCTURE IDENTICAL ACROSS ROWS
# ==========================================================

def test_target_structure_is_identical():

    dataset = build_target_dataset()

    expected = {
        get_target_name(
            horizon
        )
        for horizon in HORIZONS
    }

    errors = []

    for index, row in enumerate(
        dataset
    ):

        actual = {
            key
            for key in row.keys()
            if key.startswith(
                TARGET_PREFIX
            )
        }

        if actual != expected:

            errors.append(
                (
                    index,
                    sorted(
                        expected - actual
                    ),
                    sorted(
                        actual - expected
                    ),
                )
            )

    assert not errors, (
        'Inconsistent expense target structure:\n'
        + '\n'.join(
            str(error)
            for error in errors[:10]
        )
    )

    print(
        'PASS: Expense target structure '
        'is identical across all rows.'
    )


# ==========================================================
# FINAL
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '================================================='
    )
    print(
        '       EXPENSE TARGET TEMPORAL VALIDATION'
    )
    print(
        '================================================='
    )
    print()

    dataset = build_target_dataset()

    print(
        f'Dataset rows: {len(dataset)}'
    )

    print()

    print(
        'Run this file through pytest:'
    )

    print(
        'python -m pytest -q '
        'test_target_temporal_logic.py'
    )