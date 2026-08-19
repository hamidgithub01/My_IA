
from ml.features.build import (
    build_training_dataset,
)

from ml.targets.build import (
    build_target_dataset,
)


# ==========================================================
# FINAL DATASET
# ==========================================================

def build_final_dataset():
    """
    Build the final machine-learning dataset.

    Pipeline:

        Feature Engineering
                +
        Target Engineering
                ↓
        Final Dataset

    Features are calculated using information available
    before the target day.

    Targets describe the actual target-day outcome.
    """

    feature_dataset = build_training_dataset()
    target_dataset = build_target_dataset()

    if not feature_dataset:
        return []

    if not target_dataset:
        return []

    # ------------------------------------------------------
    # Index targets by date
    # ------------------------------------------------------

    targets_by_date = {
        row['Date']: row
        for row in target_dataset
    }

    final_dataset = []

    # ------------------------------------------------------
    # Match each feature row with its target row
    # ------------------------------------------------------

    for feature_row in feature_dataset:

        date_value = feature_row.get(
            'Date'
        )

        target_row = targets_by_date.get(
            date_value
        )

        if target_row is None:
            continue

        combined = dict(
            feature_row
        )

        # --------------------------------------------------
        # Remove the old financial target.
        #
        # The final dataset keeps targets separately.
        # --------------------------------------------------

        combined.pop(
            'Target_Expense_Total',
            None,
        )

        # --------------------------------------------------
        # Add all engineered targets.
        # --------------------------------------------------

        for key, value in target_row.items():

            if key == 'Date':
                continue

            combined[key] = value

        final_dataset.append(
            combined
        )

    # ------------------------------------------------------
    # Ensure chronological order
    # ------------------------------------------------------

    final_dataset.sort(
        key=lambda row: row['Date']
    )

    return final_dataset


# ==========================================================
# FEATURE / TARGET NAMES
# ==========================================================

def get_feature_names(dataset):
    """
    Return feature names from the final dataset.

    Date and all Target_* columns are excluded.
    """

    if not dataset:
        return []

    return [
        key
        for key in dataset[0].keys()
        if key != 'Date'
        and not key.startswith('Target_')
    ]


def get_target_names(dataset):
    """
    Return target names from the final dataset.
    """

    if not dataset:
        return []

    return [
        key
        for key in dataset[0].keys()
        if key.startswith('Target_')
    ]


# ==========================================================
# VALIDATION
# ==========================================================

def validate_final_dataset(dataset):
    """
    Validate the final machine-learning dataset.

    Checks:

        - dataset is not empty
        - dates are available
        - chronological ordering
        - duplicate dates
        - duplicate columns
        - feature/target separation
        - constant features
        - constant targets
        - missing values
    """

    errors = []
    warnings = []

    # ------------------------------------------------------
    # Empty dataset
    # ------------------------------------------------------

    if not dataset:

        return {
            'valid': False,
            'errors': [
                'Dataset is empty.'
            ],
            'warnings': [],
            'rows': 0,
            'features': 0,
            'targets': 0,
        }

    # ------------------------------------------------------
    # Column structure
    # ------------------------------------------------------

    columns = list(
        dataset[0].keys()
    )

    duplicate_columns = [
        column
        for column in set(columns)
        if columns.count(column) > 1
    ]

    if duplicate_columns:

        errors.append(
            f'Duplicate columns: '
            f'{duplicate_columns}'
        )

    feature_names = get_feature_names(
        dataset
    )

    target_names = get_target_names(
        dataset
    )

    # ------------------------------------------------------
    # Feature / target overlap
    # ------------------------------------------------------

    overlap = (
        set(feature_names)
        &
        set(target_names)
    )

    if overlap:

        errors.append(
            'Feature/target overlap: '
            f'{sorted(overlap)}'
        )

    # ------------------------------------------------------
    # Date validation
    # ------------------------------------------------------

    dates = [
        row.get('Date')
        for row in dataset
    ]

    if any(
        value is None
        for value in dates
    ):

        errors.append(
            'One or more rows have no Date.'
        )

    # ------------------------------------------------------
    # Duplicate dates
    # ------------------------------------------------------

    if len(dates) != len(set(dates)):

        errors.append(
            'Duplicate dates detected.'
        )

    # ------------------------------------------------------
    # Chronological order
    # ------------------------------------------------------

    if dates != sorted(dates):

        errors.append(
            'Dataset is not chronologically ordered.'
        )

    # ------------------------------------------------------
    # Missing values
    # ------------------------------------------------------

    for column in columns:

        missing_count = sum(
            row.get(column) is None
            for row in dataset
        )

        if missing_count > 0:

            warnings.append(
                f'{column}: '
                f'{missing_count} missing value(s).'
            )

    # ------------------------------------------------------
    # Constant features
    # ------------------------------------------------------

    for feature in feature_names:

        values = [
            row.get(feature)
            for row in dataset
        ]

        if len(set(values)) <= 1:

            warnings.append(
                f'Constant feature: '
                f'{feature}'
            )

    # ------------------------------------------------------
    # Constant targets
    # ------------------------------------------------------

    for target in target_names:

        values = [
            row.get(target)
            for row in dataset
        ]

        unique_values = set(
            values
        )

        if len(unique_values) <= 1:

            value = (
                next(
                    iter(unique_values)
                )
                if unique_values
                else 'N/A'
            )

            warnings.append(
                f'Constant target: '
                f'{target} = {value}'
            )

    # ------------------------------------------------------
    # Final validation result
    # ------------------------------------------------------

    return {
        'valid':
            len(errors) == 0,

        'errors':
            errors,

        'warnings':
            warnings,

        'rows':
            len(dataset),

        'features':
            len(feature_names),

        'targets':
            len(target_names),
    }


# ==========================================================
# COMPLETE BUILD + VALIDATION
# ==========================================================

def get_validated_dataset():
    """
    Build and validate the final machine-learning dataset.

    The dataset is returned only when structural
    validation succeeds.
    """

    dataset = build_final_dataset()

    validation = validate_final_dataset(
        dataset
    )

    if not validation['valid']:

        raise ValueError(
            'Final dataset validation failed:\n'
            +
            '\n'.join(
                validation['errors']
            )
        )

    return dataset

# ==========================================================
# TRAINING HORIZONS
# ==========================================================

TRAINING_HORIZONS = (
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
)


# ==========================================================
# HORIZON TARGET HELPERS
# ==========================================================

def get_horizon_target_names(
    dataset,
    horizon,
):
    """
    Return all Target_* columns belonging to one horizon.
    """

    if not dataset:
        return []

    if horizon not in TRAINING_HORIZONS:
        raise ValueError(
            f'Unsupported training horizon: {horizon}'
        )

    return [
        column
        for column in dataset[0].keys()
        if (
            column.startswith('Target_')
            and column.endswith(
                f'_{horizon}'
            )
        )
    ]


# ==========================================================
# TARGET VALUE VALIDATION
# ==========================================================

def _is_nan(value):
    """
    Safely determine whether a value is NaN.
    """

    try:
        return value != value
    except Exception:
        return False


def is_target_value_valid(value):
    """
    Determine whether a target value is available.

    IMPORTANT:

        None is NOT automatically considered invalid.

        Some targets, such as Location, may legitimately
        contain None when there is no location value.

        NaN is the marker used by Target Engineering to
        indicate that the requested future horizon could
        not be constructed.
    """

    if _is_nan(value):
        return False

    return True


# ==========================================================
# HORIZON VALIDATION
# ==========================================================

def is_horizon_valid(
    row,
    horizon,
    dataset,
):
    """
    Determine whether one row is valid for a specific
    training horizon.

    A row is invalid when one or more target columns for
    that horizon contain NaN.

    None is allowed because it can represent a legitimate
    target outcome rather than an unavailable horizon.
    """

    target_names = get_horizon_target_names(
        dataset,
        horizon,
    )

    if not target_names:
        return False

    for target in target_names:

        value = row.get(
            target
        )

        if not is_target_value_valid(
            value
        ):
            return False

    return True


# ==========================================================
# HORIZON DATASET
# ==========================================================

def build_horizon_dataset(
    dataset,
    horizon,
):
    """
    Build a training dataset for one specific horizon.

    Only rows with a complete and valid target set for the
    requested horizon are included.

    Example:

        build_horizon_dataset(
            dataset,
            '7D',
        )

    returns only rows where all 7D targets are available.
    """

    if not dataset:
        return []

    if horizon not in TRAINING_HORIZONS:
        raise ValueError(
            f'Unsupported training horizon: {horizon}'
        )

    horizon_dataset = []

    for row in dataset:

        if not is_horizon_valid(
            row,
            horizon,
            dataset,
        ):
            continue

        horizon_dataset.append(
            dict(row)
        )

    return horizon_dataset


# ==========================================================
# X / Y EXTRACTION
# ==========================================================

def get_training_data(
    dataset,
    horizon,
):
    """
    Extract X and y for one training horizon.

    Returns:

        X
        y
        feature_names
        target_names

    X contains only feature columns.

    y contains only targets belonging to the requested
    horizon.

    Date is excluded from X.
    """

    horizon_dataset = build_horizon_dataset(
        dataset,
        horizon,
    )

    if not horizon_dataset:

        return (
            [],
            [],
            [],
            [],
        )

    feature_names = get_feature_names(
        horizon_dataset
    )

    target_names = get_horizon_target_names(
        horizon_dataset,
        horizon,
    )

    X = []

    y = []

    for row in horizon_dataset:

        X.append(
            [
                row.get(feature)
                for feature in feature_names
            ]
        )

        y.append(
            [
                row.get(target)
                for target in target_names
            ]
        )

    return (
        X,
        y,
        feature_names,
        target_names,
    )


# ==========================================================
# TRAINING DATA VALIDATION
# ==========================================================

def validate_training_data(
    dataset,
    horizon,
):
    """
    Validate X/y readiness for one training horizon.

    This validates structure only.

    Model-specific validation such as scaling,
    classification/regression compatibility,
    calibration, and statistical quality belongs to
    later stages.
    """

    errors = []
    warnings = []

    horizon_dataset = build_horizon_dataset(
        dataset,
        horizon,
    )

    if not horizon_dataset:

        return {
            'valid': False,
            'errors': [
                f'No valid rows for horizon {horizon}.'
            ],
            'warnings': [],
            'horizon': horizon,
            'rows': 0,
            'features': 0,
            'targets': 0,
        }

    (
        X,
        y,
        feature_names,
        target_names,
    ) = get_training_data(
        dataset,
        horizon,
    )

    # ------------------------------------------------------
    # Row consistency
    # ------------------------------------------------------

    if len(X) != len(y):

        errors.append(
            'X and y row counts do not match.'
        )

    # ------------------------------------------------------
    # Feature count
    # ------------------------------------------------------

    if not feature_names:

        errors.append(
            'No features available.'
        )

    # ------------------------------------------------------
    # Target count
    # ------------------------------------------------------

    if not target_names:

        errors.append(
            'No targets available.'
        )

    # ------------------------------------------------------
    # Feature values
    # ------------------------------------------------------

    for index, row in enumerate(X):

        for feature_index, value in enumerate(row):

            if value is None:

                warnings.append(
                    f'Feature '
                    f'{feature_names[feature_index]} '
                    f'has None at row {index}.'
                )

    # ------------------------------------------------------
    # Target values
    # ------------------------------------------------------

    for index, row in enumerate(y):

        for target_index, value in enumerate(row):

            if not is_target_value_valid(
                value
            ):

                errors.append(
                    f'Target '
                    f'{target_names[target_index]} '
                    f'is invalid at row {index}.'
                )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    return {
        'valid':
            len(errors) == 0,

        'errors':
            errors,

        'warnings':
            warnings,

        'horizon':
            horizon,

        'rows':
            len(horizon_dataset),

        'features':
            len(feature_names),

        'targets':
            len(target_names),
    }


# ==========================================================
# ALL HORIZONS SUMMARY
# ==========================================================

def summarize_training_horizons(
    dataset,
):
    """
    Return the number of usable training rows for every
    horizon.
    """

    summary = {}

    for horizon in TRAINING_HORIZONS:

        horizon_dataset = build_horizon_dataset(
            dataset,
            horizon,
        )

        summary[horizon] = {
            'rows':
                len(horizon_dataset),

            'targets':
                len(
                    get_horizon_target_names(
                        dataset,
                        horizon,
                    )
                ),
        }

    return summary


# ==========================================================
# TRAINING DATASET TEST
# ==========================================================

def run_training_dataset_test():
    """
    Build and validate the final dataset for every horizon.
    """

    print()
    print(
        '========== TRAINING DATASET TEST =========='
    )

    dataset = get_validated_dataset()

    if not dataset:

        print(
            'Final dataset is empty.'
        )

        return False

    print(
        f'Final dataset rows: '
        f'{len(dataset)}'
    )

    print(
        f'Final dataset features: '
        f'{len(get_feature_names(dataset))}'
    )

    print(
        f'Final dataset targets: '
        f'{len(get_target_names(dataset))}'
    )

    errors = []

    print()

    for horizon in TRAINING_HORIZONS:

        validation = validate_training_data(
            dataset,
            horizon,
        )

        print(
            f'{horizon}: '
            f'rows={validation["rows"]}, '
            f'features={validation["features"]}, '
            f'targets={validation["targets"]}, '
            f'valid={validation["valid"]}'
        )

        if not validation['valid']:

            errors.extend(
                [
                    f'{horizon}: {error}'
                    for error in validation['errors']
                ]
            )

    print()

    print(
        f'Total training dataset errors: '
        f'{len(errors)}'
    )

    if errors:

        print()
        print(
            '========== TRAINING DATASET FAILED =========='
        )

        for error in errors:

            print(
                error
            )

        return False

    print(
        '========== TRAINING DATASET PASSED =========='
    )

    return True


# ==========================================================
# DIRECT EXECUTION
# ==========================================================

if __name__ == '__main__':

    success = run_training_dataset_test()

    if not success:

        raise SystemExit(1)
