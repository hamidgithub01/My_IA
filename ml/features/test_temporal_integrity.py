from copy import deepcopy
from datetime import date, datetime

from ml.preparation.preparation import (
    get_prepared_dataset,
)

from ml.features.build import (
    build_feature_row,
)


# ==========================================================
# DATE
# ==========================================================

def to_date(value):
    """
    Convert supported date values into Python date.
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
# TARGET-DAY OBSERVED OUTCOMES
# ==========================================================

FORBIDDEN_TARGET_DAY_FIELDS = {

    # Financial
    'Expense_Total',
    'Expense_Count',
    'Income_Total',
    'Income_Count',

    # Events
    'Event_Count',

    # Health
    'Health_Record_Count',
    'Max_Health_Severity',
    'Avg_Energy_Level',

    # Activities
    'Activity_Count',
    'Activity_Duration_Minutes',
    'Activity_Cost',

    # Sleep
    'Sleep_Record_Count',
    'Sleep_Duration_Minutes',
    'Avg_Sleep_Quality',
    'Total_Awakenings',

    # Target-day observations
    'Stress_Level',
    'Sleep_Hours',
    'Social_Activity',
    'Work_Status',
    'Travel',
    'Special_Event',
    'Location',
    'Health_Impact',
    'Day_Type',
}


# ==========================================================
# TEMPORAL ORDER TEST
# ==========================================================

def test_previous_rows_are_strictly_historical(
    prepared_data,
):
    """
    Every previous row must be strictly before
    the target date.
    """

    errors = []

    for index in range(
        1,
        len(prepared_data),
    ):

        target_row = prepared_data[index]

        target_date = to_date(
            target_row.get('Date')
        )

        if target_date is None:

            errors.append(
                'Target row has invalid date.'
            )

            continue

        previous_rows = prepared_data[:index]

        for historical_row in previous_rows:

            historical_date = to_date(
                historical_row.get('Date')
            )

            if historical_date is None:

                errors.append(
                    f'Target {target_date}: '
                    'historical row has invalid date.'
                )

                continue

            if historical_date >= target_date:

                errors.append(
                    f'Target {target_date}: '
                    f'previous_rows contains '
                    f'{historical_date}, which is not '
                    'strictly before target date.'
                )

    assert not errors, (
        'Temporal boundary violations:\n'
        + '\n'.join(errors)
    )


# ==========================================================
# TARGET-DAY IMMUTABILITY TEST
# ==========================================================

def test_target_day_outcomes_do_not_affect_features(
    prepared_data,
):
    """
    Changing target-day observed outcomes must not change
    the generated feature vector.
    """

    errors = []

    for index in range(
        1,
        len(prepared_data),
    ):

        target_row = prepared_data[index]

        target_date = to_date(
            target_row.get('Date')
        )

        previous_rows = prepared_data[:index]

        normal_features = build_feature_row(
            target_row,
            previous_rows,
        )

        poisoned_target = deepcopy(
            target_row
        )

        for field in FORBIDDEN_TARGET_DAY_FIELDS:

            if field not in poisoned_target:
                continue

            value = poisoned_target[field]

            if isinstance(value, str):

                poisoned_target[field] = (
                    '__TEMPORAL_INTEGRITY_POISON__'
                )

            elif isinstance(value, (int, float)):

                poisoned_target[field] = (
                    987654321.123
                )

            elif value is None:

                continue

            else:

                poisoned_target[field] = (
                    '__TEMPORAL_INTEGRITY_POISON__'
                )

        poisoned_features = build_feature_row(
            poisoned_target,
            previous_rows,
        )

        if normal_features != poisoned_features:

            changed_features = []

            all_keys = (
                set(normal_features)
                |
                set(poisoned_features)
            )

            for key in sorted(all_keys):

                normal_value = (
                    normal_features.get(key)
                )

                poisoned_value = (
                    poisoned_features.get(key)
                )

                if normal_value != poisoned_value:

                    changed_features.append(
                        key
                    )

            errors.append(
                f'Target {target_date}: '
                'target-day observed data changed '
                f'the feature vector: '
                f'{changed_features}'
            )

    assert not errors, (
        'Target-day dependency violations:\n'
        + '\n'.join(errors)
    )


# ==========================================================
# DIRECT TARGET COLUMN TEST
# ==========================================================

def test_forbidden_columns_are_absent(
    prepared_data,
):
    """
    Forbidden target-day observed columns must not appear
    directly inside the feature vector.
    """

    errors = []

    for index in range(
        1,
        len(prepared_data),
    ):

        target_row = prepared_data[index]

        target_date = to_date(
            target_row.get('Date')
        )

        previous_rows = prepared_data[:index]

        features = build_feature_row(
            target_row,
            previous_rows,
        )

        leaked_columns = [
            column
            for column in features
            if column in FORBIDDEN_TARGET_DAY_FIELDS
        ]

        if leaked_columns:

            errors.append(
                f'Target {target_date}: '
                'forbidden target-day columns found '
                f'in features: {leaked_columns}'
            )

    assert not errors, (
        'Direct target-column leakage:\n'
        + '\n'.join(errors)
    )


# ==========================================================
# TARGET COLUMN TEST
# ==========================================================

def test_target_columns_are_absent(
    prepared_data,
):
    """
    Target_* columns must never be inserted into the
    feature vector during feature construction.
    """

    errors = []

    for index in range(
        1,
        len(prepared_data),
    ):

        target_row = prepared_data[index]

        target_date = to_date(
            target_row.get('Date')
        )

        previous_rows = prepared_data[:index]

        features = build_feature_row(
            target_row,
            previous_rows,
        )

        target_columns = [
            column
            for column in features
            if column.startswith('Target_')
        ]

        if target_columns:

            errors.append(
                f'Target {target_date}: '
                'Target_* columns found inside '
                f'feature vector: {target_columns}'
            )

    assert not errors, (
        'Target column leakage:\n'
        + '\n'.join(errors)
    )


# ==========================================================
# FEATURE DETERMINISM TEST
# ==========================================================

def test_feature_generation_is_deterministic(
    prepared_data,
):
    """
    Generating the same feature row twice from identical
    information must produce identical results.
    """

    errors = []

    for index in range(
        1,
        len(prepared_data),
    ):

        target_row = prepared_data[index]

        target_date = to_date(
            target_row.get('Date')
        )

        previous_rows = prepared_data[:index]

        first = build_feature_row(
            target_row,
            previous_rows,
        )

        second = build_feature_row(
            target_row,
            previous_rows,
        )

        if first != second:

            errors.append(
                f'Target {target_date}: '
                'feature generation is not deterministic.'
            )

    assert not errors, (
        'Feature determinism violations:\n'
        + '\n'.join(errors)
    )


# ==========================================================
# MAIN TEST
# ==========================================================

def run_temporal_integrity_test():

    print(
        '========== TEMPORAL INTEGRITY TEST =========='
    )

    prepared_data = get_prepared_dataset()

    if len(prepared_data) < 2:

        print(
            'Not enough data for temporal integrity test.'
        )

        return False

    prepared_data = sorted(
        prepared_data,
        key=lambda row: to_date(
            row.get('Date')
        ),
    )

    total_rows = len(
        prepared_data
    )

    print(
        'Prepared rows:',
        total_rows,
    )

    all_errors = []

    # ======================================================
    # TEST 1
    # ======================================================

    for index in range(
        1,
        len(prepared_data),
    ):

        target_date = to_date(
            prepared_data[index].get('Date')
        )

        for historical_row in prepared_data[:index]:

            historical_date = to_date(
                historical_row.get('Date')
            )

            if (
                historical_date is None
                or target_date is None
                or historical_date >= target_date
            ):

                all_errors.append(
                    (
                        target_date,
                        'Invalid historical boundary.'
                    )
                )

    print(
        'Historical boundary errors:',
        len(all_errors),
    )

    # ======================================================
    # TEST 2
    # ======================================================

    try:

        test_target_day_outcomes_do_not_affect_features(
            prepared_data
        )

        target_day_errors = 0

    except AssertionError as exc:

        target_day_errors = 1
        all_errors.append(
            (
                None,
                str(exc)
            )
        )

    print(
        'Target-day dependency errors:',
        target_day_errors,
    )

    # ======================================================
    # TEST 3
    # ======================================================

    try:

        test_forbidden_columns_are_absent(
            prepared_data
        )

        direct_errors = 0

    except AssertionError as exc:

        direct_errors = 1
        all_errors.append(
            (
                None,
                str(exc)
            )
        )

    print(
        'Direct target-column errors:',
        direct_errors,
    )

    # ======================================================
    # TEST 4
    # ======================================================

    try:

        test_target_columns_are_absent(
            prepared_data
        )

        target_column_errors = 0

    except AssertionError as exc:

        target_column_errors = 1
        all_errors.append(
            (
                None,
                str(exc)
            )
        )

    print(
        'Target_* leakage errors:',
        target_column_errors,
    )

    # ======================================================
    # TEST 5
    # ======================================================

    try:

        test_feature_generation_is_deterministic(
            prepared_data
        )

        determinism_errors = 0

    except AssertionError as exc:

        determinism_errors = 1
        all_errors.append(
            (
                None,
                str(exc)
            )
        )

    print(
        'Determinism errors:',
        determinism_errors,
    )

    # ======================================================
    # RESULT
    # ======================================================

    print(
        'Total temporal integrity errors:',
        len(all_errors),
    )

    if all_errors:

        print()
        print(
            '========== TEMPORAL INTEGRITY FAILED =========='
        )

        for target_date, problem in all_errors:

            print(
                f'Date: {target_date}'
            )

            print(
                f'Problem: {problem}'
            )

        return False

    print()
    print(
        '========== TEMPORAL INTEGRITY PASSED =========='
    )

    return True


# ==========================================================
# SCRIPT ENTRY POINT
# ==========================================================

if __name__ == '__main__':

    success = run_temporal_integrity_test()

    if not success:

        raise SystemExit(1)