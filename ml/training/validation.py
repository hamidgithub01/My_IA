import math
from datetime import date, datetime


# ==========================================================
# DATE HELPERS
# ==========================================================

def _to_date(value):
    """
    Convert supported date values into a date object.
    """

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):

        try:
            return date.fromisoformat(
                value[:10]
            )

        except ValueError:
            return None

    return None


# ==========================================================
# VALUE VALIDATION
# ==========================================================

def _is_finite_number(value):
    """
    Return True when value is a finite numeric value.
    """

    if isinstance(value, bool):
        return False

    if not isinstance(
        value,
        (
            int,
            float,
        ),
    ):
        return False

    return math.isfinite(
        float(value)
    )


# ==========================================================
# DATE VALIDATION
# ==========================================================

def validate_dataset_dates(
    dataset,
):
    """
    Validate chronological ordering and duplicate dates.
    """

    if not dataset:
        return

    dates = []

    for index, row in enumerate(dataset):

        if 'Date' not in row:

            raise ValueError(
                f'Dataset row {index} has no Date.'
            )

        row_date = _to_date(
            row.get('Date')
        )

        if row_date is None:

            raise ValueError(
                f'Dataset row {index} contains '
                f'an invalid Date: {row.get("Date")!r}'
            )

        dates.append(
            row_date
        )

    # ------------------------------------------------------
    # Chronological ordering
    # ------------------------------------------------------

    if dates != sorted(dates):

        raise ValueError(
            'Dataset is not chronologically ordered.'
        )

    # ------------------------------------------------------
    # Duplicate dates
    # ------------------------------------------------------

    if len(dates) != len(set(dates)):

        raise ValueError(
            'Dataset contains duplicate dates.'
        )


# ==========================================================
# FEATURE SCHEMA VALIDATION
# ==========================================================

def validate_feature_schema(
    dataset,
    feature_names,
):
    """
    Validate feature names and every feature row.
    """

    if not feature_names:

        raise ValueError(
            'Feature names are empty.'
        )

    # ------------------------------------------------------
    # Forbidden columns
    # ------------------------------------------------------

    forbidden = [
        name
        for name in feature_names
        if name == 'Date'
        or name.startswith('Target_')
    ]

    if forbidden:

        raise ValueError(
            'Forbidden model features detected: '
            f'{forbidden}'
        )

    # ------------------------------------------------------
    # Every row must contain every feature
    # ------------------------------------------------------

    for row_index, row in enumerate(
        dataset
    ):

        for feature_name in feature_names:

            if feature_name not in row:

                raise ValueError(
                    'Feature schema mismatch.\n'
                    f'Row: {row_index}\n'
                    f'Missing feature: {feature_name}'
                )

            value = row.get(
                feature_name
            )

            if not _is_finite_number(
                value
            ):

                raise ValueError(
                    'Invalid feature value.\n'
                    f'Row: {row_index}\n'
                    f'Feature: {feature_name}\n'
                    f'Value: {value!r}'
                )


# ==========================================================
# X MATRIX VALIDATION
# ==========================================================

def validate_feature_matrix(
    X,
    feature_names,
    dataset_name='dataset',
):
    """
    Validate X dimensions and numeric values.
    """

    if len(feature_names) == 0:

        raise ValueError(
            'Feature matrix has no feature names.'
        )

    for row_index, row in enumerate(X):

        if len(row) != len(
            feature_names
        ):

            raise ValueError(
                f'{dataset_name} row {row_index} '
                'has an invalid feature count.\n'
                f'Expected: {len(feature_names)}\n'
                f'Actual: {len(row)}'
            )

        for feature_index, value in enumerate(
            row
        ):

            if not _is_finite_number(
                value
            ):

                raise ValueError(
                    f'{dataset_name} contains '
                    'an invalid feature value.\n'
                    f'Row: {row_index}\n'
                    f'Feature: '
                    f'{feature_names[feature_index]}\n'
                    f'Value: {value!r}'
                )


# ==========================================================
# TARGET VALIDATION
# ==========================================================

def validate_target_values(
    values,
    target_name,
    dataset_name='target',
):
    """
    Validate that target values are known and finite.
    """

    for index, value in enumerate(values):

        if not _is_finite_number(
            value
        ):

            raise ValueError(
                f'Invalid target value in '
                f'{dataset_name}.\n'
                f'Row: {index}\n'
                f'Target: {target_name}\n'
                f'Value: {value!r}'
            )


# ==========================================================
# X / Y ALIGNMENT
# ==========================================================

def validate_xy_alignment(
    X,
    y,
    dataset_name='dataset',
):
    """
    Validate X/y row alignment.
    """

    if len(X) != len(y):

        raise ValueError(
            f'{dataset_name} X/y length mismatch.\n'
            f'X rows: {len(X)}\n'
            f'y rows: {len(y)}'
        )


# ==========================================================
# TRAIN / TEST TEMPORAL VALIDATION
# ==========================================================

def validate_train_test_temporal_separation(
    training_data,
    test_data,
):
    """
    Validate chronological separation between training
    and testing observations.
    """

    if not training_data or not test_data:
        return

    training_dates = [
        _to_date(
            row.get('Date')
        )
        for row in training_data
    ]

    test_dates = [
        _to_date(
            row.get('Date')
        )
        for row in test_data
    ]

    if any(
        value is None
        for value in training_dates
    ):

        raise ValueError(
            'Training data contains an invalid Date.'
        )

    if any(
        value is None
        for value in test_dates
    ):

        raise ValueError(
            'Test data contains an invalid Date.'
        )

    # ------------------------------------------------------
    # Training must come before testing
    # ------------------------------------------------------

    if max(training_dates) >= min(
        test_dates
    ):

        raise ValueError(
            'Training and test periods overlap '
            'or are not chronologically separated.'
        )

    # ------------------------------------------------------
    # No exact date overlap
    # ------------------------------------------------------

    overlap = (
        set(training_dates)
        & set(test_dates)
    )

    if overlap:

        raise ValueError(
            'Training and test datasets contain '
            f'overlapping dates: {sorted(overlap)}'
        )


# ==========================================================
# TARGET LEAKAGE VALIDATION
# ==========================================================

def validate_no_target_leakage(
    feature_names,
    target_name,
):
    """
    Ensure the selected target cannot enter model inputs.
    """

    if target_name in feature_names:

        raise ValueError(
            'Target leakage detected: '
            f'{target_name} exists inside feature_names.'
        )

    forbidden_targets = [
        name
        for name in feature_names
        if name.startswith('Target_')
    ]

    if forbidden_targets:

        raise ValueError(
            'Target leakage detected. '
            'Target columns found inside features: '
            f'{forbidden_targets}'
        )


# ==========================================================
# COMPLETE MODEL DATASET VALIDATION
# ==========================================================

def validate_model_dataset(
    result,
):
    """
    Perform complete Training Dataset Validation.

    Expected structure:

        dataset
        feature_names
        target_name
        training_data
        test_data
        X_train
        y_train
        X_test
        y_test
    """

    if result is None:

        raise ValueError(
            'Model dataset result is None.'
        )

    dataset = result.get(
        'dataset',
        []
    )

    feature_names = result.get(
        'feature_names',
        []
    )

    target_name = result.get(
        'target_name'
    )

    training_data = result.get(
        'training_data',
        []
    )

    test_data = result.get(
        'test_data',
        []
    )

    X_train = result.get(
        'X_train',
        []
    )

    y_train = result.get(
        'y_train',
        []
    )

    X_test = result.get(
        'X_test',
        []
    )

    y_test = result.get(
        'y_test',
        []
    )

    if not target_name:

        raise ValueError(
            'Model dataset contains no target name.'
        )

    # ------------------------------------------------------
    # Dataset dates
    # ------------------------------------------------------

    validate_dataset_dates(
        dataset
    )

    validate_dataset_dates(
        training_data
    )

    validate_dataset_dates(
        test_data
    )

    # ------------------------------------------------------
    # Feature schema
    # ------------------------------------------------------

    validate_feature_schema(
        dataset,
        feature_names,
    )

    # ------------------------------------------------------
    # Target leakage
    # ------------------------------------------------------

    validate_no_target_leakage(
        feature_names,
        target_name,
    )

    # ------------------------------------------------------
    # X / y alignment
    # ------------------------------------------------------

    validate_xy_alignment(
        X_train,
        y_train,
        'training dataset',
    )

    validate_xy_alignment(
        X_test,
        y_test,
        'test dataset',
    )

    # ------------------------------------------------------
    # Feature matrices
    # ------------------------------------------------------

    validate_feature_matrix(
        X_train,
        feature_names,
        'X_train',
    )

    validate_feature_matrix(
        X_test,
        feature_names,
        'X_test',
    )

    # ------------------------------------------------------
    # Targets
    # ------------------------------------------------------

    validate_target_values(
        y_train,
        target_name,
        'y_train',
    )

    validate_target_values(
        y_test,
        target_name,
        'y_test',
    )

    # ------------------------------------------------------
    # Temporal separation
    # ------------------------------------------------------

    validate_train_test_temporal_separation(
        training_data,
        test_data,
    )

    return True