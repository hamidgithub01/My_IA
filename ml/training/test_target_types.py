from ml.training.dataset import (
    infer_target_type,
    get_target_class_count,
)


def test_target_types():

    print(
        '========== TARGET TYPE TEST =========='
    )

    # ======================================================
    # Real numeric target
    # ======================================================

    numeric_dataset = [
        {
            'Date': '2026-08-01',
            'Target_Expense_Total_1D': 0.0,
        },
        {
            'Date': '2026-08-02',
            'Target_Expense_Total_1D': 150.0,
        },
        {
            'Date': '2026-08-03',
            'Target_Expense_Total_1D': 0.0,
        },
        {
            'Date': '2026-08-04',
            'Target_Expense_Total_1D': 300.0,
        },
    ]

    target_type = infer_target_type(
        numeric_dataset,
        'Target_Expense_Total_1D',
    )

    if target_type != 'numeric':

        raise AssertionError(
            'Numeric target was not detected as numeric.'
        )

    class_count = get_target_class_count(
        numeric_dataset,
        'Target_Expense_Total_1D',
    )

    if class_count != 3:

        raise AssertionError(
            f'Expected 3 unique values, '
            f'got {class_count}.'
        )

    print(
        'Numeric target detection: PASSED'
    )

    print(
        'Numeric target unique-value count: PASSED'
    )

    # ======================================================
    # Real categorical target
    # ======================================================

    categorical_dataset = [
        {
            'Date': '2026-08-01',
            'Target_Location_1D': 'home',
        },
        {
            'Date': '2026-08-02',
            'Target_Location_1D': 'work',
        },
        {
            'Date': '2026-08-03',
            'Target_Location_1D': 'travel',
        },
        {
            'Date': '2026-08-04',
            'Target_Location_1D': 'home',
        },
    ]

    target_type = infer_target_type(
        categorical_dataset,
        'Target_Location_1D',
    )

    if target_type != 'categorical':

        raise AssertionError(
            'Categorical target was not detected '
            'as categorical.'
        )

    class_count = get_target_class_count(
        categorical_dataset,
        'Target_Location_1D',
    )

    if class_count != 3:

        raise AssertionError(
            f'Expected 3 classes, '
            f'got {class_count}.'
        )

    print(
        'Categorical target detection: PASSED'
    )

    print(
        'Multiclass class count: PASSED'
    )

    # ======================================================
    # Missing values
    # ======================================================

    dataset_with_missing = [
        {
            'Date': '2026-08-01',
            'Target_Location_1D': 'home',
        },
        {
            'Date': '2026-08-02',
            'Target_Location_1D': None,
        },
        {
            'Date': '2026-08-03',
            'Target_Location_1D': 'work',
        },
    ]

    class_count = get_target_class_count(
        dataset_with_missing,
        'Target_Location_1D',
    )

    if class_count != 2:

        raise AssertionError(
            'Missing target values were incorrectly '
            'counted as classes.'
        )

    print(
        'Missing target handling: PASSED'
    )

    # ======================================================
    # Final
    # ======================================================

    print()

    print(
        '========== TARGET TYPE TEST PASSED =========='
    )


if __name__ == '__main__':

    test_target_types()