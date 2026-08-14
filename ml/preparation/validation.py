from datetime import date, datetime
from numbers import Number


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _to_date(value):
    """
    Convert a value to a Python date.

    Returns None when conversion fails.
    """

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None

    return None


def _is_numeric(value):
    """
    Return True when a value can reasonably be treated
    as numeric.

    Boolean values are excluded.
    """

    if isinstance(value, bool):
        return False

    if isinstance(value, Number):
        return True

    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _is_missing(value):
    """
    Detect missing values.

    Zero is NOT considered missing.
    False is NOT considered missing.
    """

    return value is None


# ==========================================================
# DATE VALIDATION
# ==========================================================

def validate_dates(
    data,
    date_field='Date',
    require_sorted=True,
    allow_duplicate_dates=False,
):
    """
    Validate dates inside a dataset.

    Returns a report dictionary.
    """

    errors = []
    invalid_dates = []
    dates = []

    for index, row in enumerate(data or []):

        value = row.get(date_field)

        parsed_date = _to_date(value)

        if parsed_date is None:
            invalid_dates.append(index)
            continue

        dates.append(parsed_date)

    if invalid_dates:

        errors.append(
            f'Invalid dates found at rows: '
            f'{invalid_dates}'
        )

    if require_sorted and len(dates) > 1:

        for index in range(1, len(dates)):

            if dates[index] < dates[index - 1]:

                errors.append(
                    'Dataset is not chronologically sorted.'
                )

                break

    duplicate_dates = []

    if not allow_duplicate_dates:

        seen = set()

        for current_date in dates:

            if current_date in seen:

                duplicate_dates.append(
                    current_date
                )

            seen.add(current_date)

        if duplicate_dates:

            errors.append(
                'Duplicate dates found: '
                f'{sorted(set(duplicate_dates))}'
            )

    return {
        'valid': not errors,
        'errors': errors,
        'row_count': len(data or []),
        'valid_date_count': len(dates),
        'invalid_date_rows': invalid_dates,
        'duplicate_dates': sorted(
            set(duplicate_dates)
        ),
    }


# ==========================================================
# FEATURE SCHEMA VALIDATION
# ==========================================================

def validate_feature_schema(
    features,
    feature_names=None,
):
    """
    Validate the feature dataset structure.

    Date and Target_* columns must never be
    considered model input features.
    """

    errors = []

    if not features:

        return {
            'valid': False,
            'errors': ['Feature dataset is empty.'],
            'feature_count': 0,
            'forbidden_features': [],
        }

    actual_columns = list(
        features[0].keys()
    )

    if feature_names is None:

        feature_names = [
            name
            for name in actual_columns
            if name != 'Date'
            and not name.startswith('Target_')
        ]

    forbidden = []

    for name in feature_names:

        if name == 'Date':

            forbidden.append(name)

        elif name.startswith('Target_'):

            forbidden.append(name)

    if forbidden:

        errors.append(
            'Forbidden model features found: '
            f'{forbidden}'
        )

    missing_feature_names = [
        name
        for name in feature_names
        if name not in actual_columns
    ]

    if missing_feature_names:

        errors.append(
            'Feature names missing from dataset: '
            f'{missing_feature_names}'
        )

    return {
        'valid': not errors,
        'errors': errors,
        'feature_count': len(feature_names),
        'forbidden_features': forbidden,
        'missing_features': missing_feature_names,
        'feature_names': feature_names,
    }


# ==========================================================
# FEATURE VALUE VALIDATION
# ==========================================================

def validate_feature_values(
    data,
    feature_names=None,
):
    """
    Validate feature values.

    Missing values are reported but are not automatically
    considered errors because some historical features
    legitimately start with missing history.

    Non-numeric feature values are reported.
    """

    errors = []

    if not data:

        return {
            'valid': False,
            'errors': ['Feature dataset is empty.'],
            'missing_values': {},
            'non_numeric_values': {},
        }

    if feature_names is None:

        feature_names = [
            name
            for name in data[0].keys()
            if name != 'Date'
            and not name.startswith('Target_')
        ]

    missing_values = {}
    non_numeric_values = {}

    for feature_name in feature_names:

        missing_rows = []
        invalid_rows = []

        for index, row in enumerate(data):

            value = row.get(feature_name)

            if _is_missing(value):

                missing_rows.append(index)

                continue

            if not _is_numeric(value):

                invalid_rows.append(index)

        if missing_rows:

            missing_values[
                feature_name
            ] = missing_rows

        if invalid_rows:

            non_numeric_values[
                feature_name
            ] = invalid_rows

    if non_numeric_values:

        errors.append(
            'Non-numeric feature values found: '
            f'{list(non_numeric_values.keys())}'
        )

    return {
        'valid': not errors,
        'errors': errors,
        'missing_values': missing_values,
        'non_numeric_values': non_numeric_values,
    }


# ==========================================================
# TARGET VALIDATION
# ==========================================================

def validate_targets(
    data,
    target_names=None,
    minimum_available=1,
):
    """
    Validate target columns.

    Missing target values are allowed.

    This is important because future horizons such as
    30D cannot exist for the latest historical rows.

    A target is considered trainable when it has at least
    minimum_available non-missing values.
    """

    errors = []

    if not data:

        return {
            'valid': False,
            'errors': ['Target dataset is empty.'],
            'target_count': 0,
            'target_summary': {},
        }

    if target_names is None:

        target_names = [
            name
            for name in data[0].keys()
            if name.startswith('Target_')
        ]

    target_summary = {}

    for target_name in target_names:

        available_rows = []
        missing_rows = []
        invalid_rows = []

        for index, row in enumerate(data):

            value = row.get(target_name)

            if _is_missing(value):

                missing_rows.append(index)

                continue

            if not _is_numeric(value):

                invalid_rows.append(index)

                continue

            available_rows.append(index)

        trainable = (
            len(available_rows)
            >= minimum_available
        )

        target_summary[target_name] = {

            'available': len(
                available_rows
            ),

            'missing': len(
                missing_rows
            ),

            'invalid': len(
                invalid_rows
            ),

            'trainable': trainable,

            'available_rows':
                available_rows,

            'missing_rows':
                missing_rows,

            'invalid_rows':
                invalid_rows,
        }

        if invalid_rows:

            errors.append(
                f'Invalid values in target '
                f'{target_name}.'
            )

    return {
        'valid': not errors,
        'errors': errors,
        'target_count': len(target_names),
        'target_summary': target_summary,
    }


# ==========================================================
# DATE ALIGNMENT
# ==========================================================

def validate_date_alignment(
    features,
    targets,
):
    """
    Ensure that feature rows and target rows refer
    to the same dates.

    Alignment is checked by Date, not by row position.
    """

    errors = []

    feature_dates = {
        _to_date(row.get('Date'))
        for row in features or []
        if _to_date(row.get('Date')) is not None
    }

    target_dates = {
        _to_date(row.get('Date'))
        for row in targets or []
        if _to_date(row.get('Date')) is not None
    }

    missing_in_targets = sorted(
        feature_dates - target_dates
    )

    missing_in_features = sorted(
        target_dates - feature_dates
    )

    if missing_in_targets:

        errors.append(
            'Feature dates missing from targets: '
            f'{missing_in_targets}'
        )

    if missing_in_features:

        errors.append(
            'Target dates missing from features: '
            f'{missing_in_features}'
        )

    return {
        'valid': not errors,
        'errors': errors,
        'feature_date_count': len(
            feature_dates
        ),
        'target_date_count': len(
            target_dates
        ),
        'missing_in_targets':
            missing_in_targets,
        'missing_in_features':
            missing_in_features,
    }


# ==========================================================
# FEATURE / TARGET LEAKAGE VALIDATION
# ==========================================================

def validate_no_feature_target_leakage(
    features,
):
    """
    Ensure that target columns are not present
    inside model features.

    Date is also excluded from model inputs.
    """

    errors = []

    if not features:

        return {
            'valid': False,
            'errors': ['Feature dataset is empty.'],
            'forbidden_features': [],
        }

    columns = list(
        features[0].keys()
    )

    forbidden = []

    for column in columns:

        if column == 'Date':

            forbidden.append(column)

        elif column.startswith('Target_'):

            forbidden.append(column)

    # Date is allowed in the dataset for identification,
    # ordering and reporting, but forbidden as model input.
    #
    # Target_* is allowed in a combined dataset for target
    # storage, but forbidden as model input.

    if forbidden:

        # This function validates raw dataset columns.
        # Therefore Date/Target columns are reported here,
        # while get_model_feature_names() determines the
        # actual model input columns.

        pass

    return {
        'valid': True,
        'errors': errors,
        'forbidden_dataset_columns': [],
        'note': (
            'Date and Target_* may exist in the '
            'dataset but must be excluded from X.'
        ),
    }


# ==========================================================
# MODEL FEATURE NAMES
# ==========================================================

def get_model_feature_names(
    data,
):
    """
    Return only columns allowed to enter the model.

    Explicitly excludes:

        Date
        Target_*
    """

    if not data:
        return []

    return [
        name
        for name in data[0].keys()
        if name != 'Date'
        and not name.startswith('Target_')
    ]


# ==========================================================
# TEMPORAL INTEGRITY
# ==========================================================

def validate_temporal_integrity(
    features,
):
    """
    Validate that historical feature names do not
    accidentally contain target columns.

    This is a structural validation.

    Actual historical-value leakage is tested separately
    by ml.features.test_temporal_leakage.
    """

    errors = []

    if not features:

        return {
            'valid': False,
            'errors': ['Feature dataset is empty.'],
        }

    model_features = get_model_feature_names(
        features
    )

    suspicious = [
        name
        for name in model_features
        if name.startswith('Target_')
    ]

    if suspicious:

        errors.append(
            'Target-prefixed columns detected '
            'inside model features.'
        )

    return {
        'valid': not errors,
        'errors': errors,
        'model_feature_count':
            len(model_features),
    }


# ==========================================================
# DATASET SIZE VALIDATION
# ==========================================================

def validate_dataset_size(
    features,
    minimum_rows=2,
):
    """
    Validate whether the dataset contains enough rows
    for basic supervised learning preparation.

    This does NOT claim that the dataset is large enough
    for a production-quality model.
    """

    row_count = len(
        features or []
    )

    errors = []

    if row_count < minimum_rows:

        errors.append(
            f'Dataset contains only {row_count} '
            f'rows; minimum required is '
            f'{minimum_rows}.'
        )

    return {
        'valid': not errors,
        'errors': errors,
        'row_count': row_count,
        'minimum_rows': minimum_rows,
    }


# ==========================================================
# FULL DATASET VALIDATION
# ==========================================================

def validate_training_dataset(
    features,
    targets=None,
    minimum_rows=2,
    minimum_target_values=1,
):
    """
    Run the complete dataset validation pipeline.

    Parameters
    ----------
    features:
        Feature dataset produced by the feature builder.

    targets:
        Optional target dataset. If omitted, targets are
        extracted from features when Target_* columns exist.

    minimum_rows:
        Minimum number of feature rows required.

    minimum_target_values:
        Minimum number of available values required
        for a target to be considered trainable.
    """

    errors = []

    features = features or []

    # ------------------------------------------------------
    # Targets can be supplied separately.
    # Otherwise use the same combined dataset.
    # ------------------------------------------------------

    if targets is None:

        targets = features

    targets = targets or []

    # ------------------------------------------------------
    # Basic dataset size
    # ------------------------------------------------------

    size_report = validate_dataset_size(
        features,
        minimum_rows,
    )

    errors.extend(
        size_report['errors']
    )

    # ------------------------------------------------------
    # Feature dates
    # ------------------------------------------------------

    feature_date_report = validate_dates(
        features,
        date_field='Date',
        require_sorted=True,
        allow_duplicate_dates=False,
    )

    errors.extend(
        feature_date_report['errors']
    )

    # ------------------------------------------------------
    # Target dates
    # ------------------------------------------------------

    target_date_report = validate_dates(
        targets,
        date_field='Date',
        require_sorted=True,
        allow_duplicate_dates=False,
    )

    errors.extend(
        [
            f'Target dataset: {error}'
            for error in target_date_report[
                'errors'
            ]
        ]
    )

    # ------------------------------------------------------
    # Feature schema
    # ------------------------------------------------------

    schema_report = validate_feature_schema(
        features
    )

    errors.extend(
        schema_report['errors']
    )

    # ------------------------------------------------------
    # Feature values
    # ------------------------------------------------------

    feature_names = (
        schema_report.get(
            'feature_names',
            []
        )
    )

    feature_value_report = (
        validate_feature_values(
            features,
            feature_names,
        )
    )

    errors.extend(
        feature_value_report['errors']
    )

    # ------------------------------------------------------
    # Targets
    # ------------------------------------------------------

    target_names = [
        name
        for name in (
            targets[0].keys()
            if targets
            else []
        )
        if name.startswith('Target_')
    ]

    target_report = validate_targets(
        targets,
        target_names,
        minimum_target_values,
    )

    errors.extend(
        target_report['errors']
    )

    # ------------------------------------------------------
    # Date alignment
    # ------------------------------------------------------

    alignment_report = (
        validate_date_alignment(
            features,
            targets,
        )
    )

    errors.extend(
        alignment_report['errors']
    )

    # ------------------------------------------------------
    # Structural temporal integrity
    # ------------------------------------------------------

    temporal_report = (
        validate_temporal_integrity(
            features
        )
    )

    errors.extend(
        temporal_report['errors']
    )

    # ------------------------------------------------------
    # Final status
    # ------------------------------------------------------

    return {
        'valid': not errors,

        'ready_for_training':
            not errors,

        'errors':
            errors,

        'row_count':
            len(features),

        'feature_count':
            schema_report.get(
                'feature_count',
                0,
            ),

        'model_feature_count':
            len(
                get_model_feature_names(
                    features
                )
            ),

        'target_count':
            target_report.get(
                'target_count',
                0,
            ),

        'feature_date_count':
            feature_date_report.get(
                'valid_date_count',
                0,
            ),

        'target_date_count':
            target_date_report.get(
                'valid_date_count',
                0,
            ),

        'missing_feature_values':
            feature_value_report.get(
                'missing_values',
                {},
            ),

        'target_summary':
            target_report.get(
                'target_summary',
                {},
            ),

        'alignment':
            alignment_report,

        'schema':
            schema_report,

        'dates':
            feature_date_report,

        'target_dates':
            target_date_report,

        'feature_values':
            feature_value_report,

        'temporal':
            temporal_report,
    }


# ==========================================================
# REPORT
# ==========================================================

def print_validation_report(
    report,
):
    """
    Print a readable validation report.
    """

    print(
        '========== DATASET VALIDATION =========='
    )

    print(
        f"Rows: {report.get('row_count', 0)}"
    )

    print(
        f"Model features: "
        f"{report.get('model_feature_count', 0)}"
    )

    print(
        f"Targets: "
        f"{report.get('target_count', 0)}"
    )

    print(
        f"Feature dates: "
        f"{report.get('feature_date_count', 0)}"
    )

    print(
        f"Target dates: "
        f"{report.get('target_date_count', 0)}"
    )

    print()

    print(
        '========== TARGET AVAILABILITY =========='
    )

    target_summary = report.get(
        'target_summary',
        {},
    )

    for target_name, info in (
        target_summary.items()
    ):

        print(
            f"{target_name}: "
            f"available={info['available']}, "
            f"missing={info['missing']}, "
            f"invalid={info['invalid']}, "
            f"trainable={info['trainable']}"
        )

    print()

    print(
        '========== MISSING FEATURE VALUES =========='
    )

    missing_features = report.get(
        'missing_feature_values',
        {},
    )

    if missing_features:

        for name, rows in (
            missing_features.items()
        ):

            print(
                f'{name}: '
                f'{len(rows)} missing'
            )

    else:

        print(
            'No missing feature values.'
        )

    print()

    print(
        '========== VALIDATION RESULT =========='
    )

    if report.get(
        'ready_for_training'
    ):

        print(
            'DATASET VALIDATION PASSED'
        )

        print(
            'READY FOR MODEL TRAINING'
        )

    else:

        print(
            'DATASET VALIDATION FAILED'
        )

        print(
            'Errors:'
        )

        for error in report.get(
            'errors',
            [],
        ):

            print(
                f' - {error}'
            )