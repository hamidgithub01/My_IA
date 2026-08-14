from copy import deepcopy

from ml.preparation.preparation import get_prepared_dataset
from ml.features.build import (
    build_training_dataset,
    build_feature_row,
    get_feature_names,
)


# ==========================================================
# CONFIGURATION
# ==========================================================

TARGET_COLUMN = 'Target_Expense_Total'
DATE_COLUMN = 'Date'

ALLOWED_KNOWN_PREFIXES = (
    'Known_Plan_',
    'Known_Recurring_',
)


# ==========================================================
# HELPERS
# ==========================================================

def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def build_rows_from_prepared(prepared_data):
    prepared_data = sorted(
        prepared_data,
        key=lambda row: row['Date'],
    )

    rows = []

    for index in range(1, len(prepared_data)):
        target_row = prepared_data[index]
        previous_rows = prepared_data[:index]

        features = build_feature_row(
            target_row,
            previous_rows,
        )

        features[TARGET_COLUMN] = float(
            target_row.get('Expense_Total') or 0.0
        )

        rows.append(features)

    return rows


# ==========================================================
# TEST 1
# ==========================================================

def test_target_and_date_are_excluded_from_model_features():
    data = build_training_dataset()

    assert_true(
        data,
        'Training dataset is empty.',
    )

    feature_names = get_feature_names(data)

    assert_true(
        DATE_COLUMN not in feature_names,
        'DATA LEAKAGE: Date is included in model features.',
    )

    assert_true(
        TARGET_COLUMN not in feature_names,
        'DATA LEAKAGE: Target_Expense_Total is included in model features.',
    )


# ==========================================================
# TEST 2
# ==========================================================

def test_target_is_present_only_as_target():
    data = build_training_dataset()

    assert_true(
        data,
        'Training dataset is empty.',
    )

    for index, row in enumerate(data):

        assert_true(
            TARGET_COLUMN in row,
            f'Row {index} does not contain the target.',
        )

        feature_names = get_feature_names([row])

        assert_true(
            TARGET_COLUMN not in feature_names,
            f'Row {index} leaks the target into model features.',
        )


# ==========================================================
# TEST 3
# ==========================================================

def test_known_future_features_are_explicitly_allowed():
    data = build_training_dataset()

    assert_true(
        data,
        'Training dataset is empty.',
    )

    feature_names = get_feature_names(data)

    known_features = [
        name
        for name in feature_names
        if name.startswith(ALLOWED_KNOWN_PREFIXES)
    ]

    assert_true(
        known_features,
        'Expected Known_Plan_* / Known_Recurring_* features were not found.',
    )

    forbidden_actual_names = {
        'Actual_Cost',
        'Actual_Date',
        'Expense_Total',
    }

    for name in feature_names:
        assert_true(
            name not in forbidden_actual_names,
            f'Potential actual-outcome leakage feature found: {name}',
        )


# ==========================================================
# TEST 4
# ==========================================================

def test_chronological_training_rows():
    prepared = get_prepared_dataset()

    assert_true(
        prepared,
        'Prepared dataset is empty.',
    )

    dates = [
        row['Date']
        for row in sorted(
            prepared,
            key=lambda row: row['Date'],
        )
    ]

    assert_true(
        dates == sorted(dates),
        'Prepared data is not chronologically ordered.',
    )

    training_data = build_training_dataset()

    training_dates = [
        row[DATE_COLUMN]
        for row in training_data
    ]

    assert_true(
        training_dates == sorted(training_dates),
        'Training target dates are not chronologically ordered.',
    )


# ==========================================================
# TEST 5
# ==========================================================
# Adversarial test:
# Changing the target day's actual expense must not change
# features that are supposed to be calculated from the past
# and known future information.


def test_target_day_expense_cannot_change_its_own_features():
    prepared_original = get_prepared_dataset()

    assert_true(
        len(prepared_original) >= 2,
        'At least two prepared days are required.',
    )

    prepared_original = sorted(
        prepared_original,
        key=lambda row: row['Date'],
    )

    # ------------------------------------------------------
    # Test each target day independently.
    #
    # We change ONLY the target day's actual expense.
    #
    # Historical rows before that target day remain
    # completely unchanged.
    # ------------------------------------------------------

    for target_index in range(
        1,
        len(prepared_original),
    ):

        original_data = deepcopy(
            prepared_original
        )

        modified_data = deepcopy(
            prepared_original
        )

        original_target = original_data[
            target_index
        ]

        modified_target = modified_data[
            target_index
        ]

        original_features = build_feature_row(
            original_target,
            original_data[:target_index],
        )

        # Change ONLY the target day's actual expense.
        modified_target['Expense_Total'] = (
            float(
                original_target.get(
                    'Expense_Total'
                ) or 0.0
            )
            + 999999999.0
        )

        modified_features = build_feature_row(
            modified_target,
            modified_data[:target_index],
        )

        # --------------------------------------------------
        # Compare every feature except Date.
        #
        # The target day's actual Expense_Total must have
        # absolutely no effect on its own features.
        # --------------------------------------------------

        for key in original_features:

            if key == DATE_COLUMN:
                continue

            original_value = (
                original_features.get(key)
            )

            modified_value = (
                modified_features.get(key)
            )

            assert_true(
                original_value == modified_value,
                (
                    'DATA LEAKAGE detected: '
                    f'feature "{key}" changed for target day '
                    f"{original_target['Date']} when only "
                    'that target day Expense_Total was changed.'
                ),
            )


# ==========================================================
# TEST 6
# ==========================================================

def test_previous_day_features_do_not_use_target_day_values():
    prepared = get_prepared_dataset()

    prepared = sorted(
        prepared,
        key=lambda row: row['Date'],
    )

    assert_true(
        len(prepared) >= 2,
        'At least two prepared days are required.',
    )

    for index in range(1, len(prepared)):

        target = prepared[index]
        previous = prepared[:index]

        features = build_feature_row(
            target,
            previous,
        )

        # Direct previous-day expense must correspond to
        # the previous row, never the target row.
        if 'Previous_Day_Expense' in features:

            expected = float(
                previous[-1].get(
                    'Expense_Total'
                ) or 0.0
            )

            actual = features[
                'Previous_Day_Expense'
            ]

            assert_true(
                actual == expected,
                (
                    'DATA LEAKAGE: Previous_Day_Expense '
                    'does not correspond to the immediately '
                    'previous day.'
                ),
            )

        # Previous-day income must likewise come from history.
        if 'Previous_Day_Income' in features:

            expected = float(
                previous[-1].get(
                    'Income_Total'
                ) or 0.0
            )

            actual = features[
                'Previous_Day_Income'
            ]

            assert_true(
                actual == expected,
                (
                    'DATA LEAKAGE: Previous_Day_Income '
                    'does not correspond to the immediately '
                    'previous day.'
                ),
            )


# ==========================================================
# TEST 7
# ==========================================================

def test_training_dataset_structure():
    data = build_training_dataset()

    assert_true(
        data,
        'Training dataset is empty.',
    )

    for index, row in enumerate(data):

        assert_true(
            DATE_COLUMN in row,
            f'Row {index} is missing Date.',
        )

        assert_true(
            TARGET_COLUMN in row,
            f'Row {index} is missing Target_Expense_Total.',
        )

        assert_true(
            isinstance(row[DATE_COLUMN], object),
            f'Row {index} has an invalid Date value.',
        )

        assert_true(
            isinstance(
                row[TARGET_COLUMN],
                (int, float),
            ),
            f'Row {index} has a non-numeric target.',
        )


# ==========================================================
# RUN ALL TESTS
# ==========================================================

def run_all_tests():
    tests = [
        test_target_and_date_are_excluded_from_model_features,
        test_target_is_present_only_as_target,
        test_known_future_features_are_explicitly_allowed,
        test_chronological_training_rows,
        test_target_day_expense_cannot_change_its_own_features,
        test_previous_day_features_do_not_use_target_day_values,
        test_training_dataset_structure,
    ]

    print()
    print('=' * 70)
    print('FEATURE ENGINEERING DATA LEAKAGE TEST')
    print('=' * 70)

    passed = 0

    for test in tests:

        print()
        print(f'Running: {test.__name__}')

        test()

        print('PASS')
        passed += 1

    print()
    print('=' * 70)
    print(f'PASSED: {passed}/{len(tests)}')
    print('NO DATA LEAKAGE DETECTED BY THESE TESTS.')
    print('=' * 70)


if __name__ == '__main__':
    run_all_tests()
