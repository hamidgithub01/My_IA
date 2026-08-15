from datetime import date, datetime

from ml.features.build import build_training_dataset


# ==========================================================
# FEATURE GROUPS
# ==========================================================

FORWARD_LOOKING_PREFIXES = (
    'Target_',
)


HISTORICAL_FEATURE_PREFIXES = (
    'Previous_Day_',
    'Lag_',
    'Rolling_',
    'Same_Weekday_',
)


# ==========================================================
# HELPERS
# ==========================================================

def normalize_date(value):
    """
    Convert supported date values into a comparable date.
    """

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):

        return datetime.fromisoformat(
            value
        ).date()

    raise TypeError(
        f'Unsupported date type: {type(value)}'
    )


def feature_columns(dataset):
    """
    Return model feature columns.

    Date and Target columns are excluded.
    """

    if not dataset:
        return []

    return [
        key
        for key in dataset[0].keys()
        if key != 'Date'
        and not key.startswith('Target_')
    ]


# ==========================================================
# TEST 1
# DATASET EXISTS
# ==========================================================

def test_training_dataset_exists():

    dataset = build_training_dataset()

    assert dataset, (
        'Training dataset is empty.'
    )

    print(
        f'PASS: Training dataset contains '
        f'{len(dataset)} rows.'
    )


# ==========================================================
# TEST 2
# NO TARGETS ARE FEATURES
# ==========================================================

def test_targets_are_not_model_features():

    dataset = build_training_dataset()

    columns = feature_columns(
        dataset
    )

    leaked_targets = [
        column
        for column in columns
        if column.startswith('Target_')
    ]

    assert not leaked_targets, (
        'Target columns found among model features:\n'
        + '\n'.join(
            leaked_targets
        )
    )

    print(
        'PASS: No Target_* column is used '
        'as a model feature.'
    )


# ==========================================================
# TEST 3
# DATE IS NOT A RAW FEATURE
# ==========================================================

def test_date_is_not_raw_feature():

    dataset = build_training_dataset()

    columns = feature_columns(
        dataset
    )

    assert 'Date' not in columns, (
        'Raw Date is being used directly '
        'as a model feature.'
    )

    print(
        'PASS: Raw Date is excluded from '
        'model features.'
    )


# ==========================================================
# TEST 4
# EXPECTED HISTORICAL FEATURE GROUPS EXIST
# ==========================================================

def test_historical_feature_groups_exist():

    dataset = build_training_dataset()

    columns = feature_columns(
        dataset
    )

    for prefix in HISTORICAL_FEATURE_PREFIXES:

        matches = [
            column
            for column in columns
            if column.startswith(prefix)
        ]

        assert matches, (
            f'No features found for group '
            f'{prefix}'
        )

        print(
            f'PASS: {prefix} '
            f'features found: {len(matches)}'
        )


# ==========================================================
# TEST 5
# FORWARD-LOOKING TARGET FEATURES DO NOT EXIST
# ==========================================================

def test_forward_target_features_do_not_exist():

    dataset = build_training_dataset()

    columns = feature_columns(
        dataset
    )

    forward_features = [
        column
        for column in columns
        if column.startswith(
            FORWARD_LOOKING_PREFIXES
        )
    ]

    assert not forward_features, (
        'Forward-looking Target_* features '
        'detected:\n'
        + '\n'.join(
            forward_features
        )
    )

    print(
        'PASS: No forward-looking Target_* '
        'feature exists.'
    )


# ==========================================================
# TEST 6
# FEATURE STRUCTURE IS IDENTICAL
# ==========================================================

def test_feature_structure_is_identical():

    dataset = build_training_dataset()

    expected = set(
        feature_columns(dataset)
    )

    errors = []

    for index, row in enumerate(
        dataset
    ):

        actual = {
            key
            for key in row.keys()
            if key != 'Date'
            and not key.startswith(
                'Target_'
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
        'Feature structure differs between rows:\n'
        + '\n'.join(
            str(error)
            for error in errors[:10]
        )
    )

    print(
        'PASS: Feature structure is identical '
        'across all rows.'
    )


# ==========================================================
# TEST 7
# HISTORICAL FEATURE NAMES
# ==========================================================

def test_historical_features_have_expected_names():

    dataset = build_training_dataset()

    columns = feature_columns(
        dataset
    )

    suspicious = []

    for column in columns:

        if column.startswith(
            HISTORICAL_FEATURE_PREFIXES
        ):

            lowered = column.lower()

            suspicious_words = (
                'future',
                'next_day',
                'next_',
                'tomorrow',
                'forward',
            )

            if any(
                word in lowered
                for word in suspicious_words
            ):

                suspicious.append(
                    column
                )

    assert not suspicious, (
        'Suspicious future-looking historical '
        'feature names detected:\n'
        + '\n'.join(
            suspicious
        )
    )

    print(
        'PASS: Historical feature names '
        'contain no obvious future-looking markers.'
    )


# ==========================================================
# TEST 8
# NO DUPLICATE FEATURE NAMES
# ==========================================================

def test_no_duplicate_feature_names():

    dataset = build_training_dataset()

    columns = feature_columns(
        dataset
    )

    assert len(columns) == len(
        set(columns)
    ), (
        'Duplicate model feature names detected.'
    )

    print(
        'PASS: No duplicate model feature names.'
    )


# ==========================================================
# TEST 9
# FEATURE VALUES ARE NUMERIC
# ==========================================================

def test_model_features_are_numeric():

    dataset = build_training_dataset()

    errors = []

    columns = feature_columns(
        dataset
    )

    for row_index, row in enumerate(
        dataset
    ):

        for column in columns:

            value = row.get(
                column
            )

            if value is None:
                continue

            if isinstance(
                value,
                bool,
            ):
                continue

            if not isinstance(
                value,
                (int, float),
            ):

                errors.append(
                    (
                        row_index,
                        column,
                        value,
                    )
                )

    assert not errors, (
        'Non-numeric model feature values detected:\n'
        + '\n'.join(
            str(error)
            for error in errors[:20]
        )
    )

    print(
        'PASS: Model features contain '
        'numeric values or None.'
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
        '          FEATURE LEAKAGE VALIDATION'
    )
    print(
        '================================================='
    )
    print()

    dataset = build_training_dataset()

    print(
        f'Dataset rows: {len(dataset)}'
    )

    print(
        f'Feature count: '
        f'{len(feature_columns(dataset))}'
    )

    print()

    print(
        'Run with:'
    )

    print(
        'python -m pytest -q '
        'test_feature_leakage.py'
    )