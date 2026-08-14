
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
