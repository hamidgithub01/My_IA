from ml.training.dataset import (
    prepare_model_dataset,
)


def test_different_targets_use_the_same_features():
    """
    Different targets should use the same model feature structure.

    The target itself must change, while the feature set remains
    independent from the selected target.
    """

    expense_result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D',
    )

    income_result = prepare_model_dataset(
        target_name='Target_Income_Total_1D',
    )

    expense_features = expense_result[
        'feature_names'
    ]

    income_features = income_result[
        'feature_names'
    ]

    assert expense_features == income_features

    assert (
        expense_result['target_name']
        == 'Target_Expense_Total_1D'
    )

    assert (
        income_result['target_name']
        == 'Target_Income_Total_1D'
    )