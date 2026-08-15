from ml.training.dataset import (
    split_features_and_target,
)

def test_different_targets_use_the_same_features():
    rows = [
    {
    'Date': '2026-08-01',

    
            'Expense_Total': 500.0,
            'Income_Total': 1000.0,
            'Previous_Day_Expense': 100.0,

            'Target_Expense_Total': 500.0,
            'Target_Income_Total': 1000.0,
            'Target_High_Stress_1D': 0,
            'Target_Working_Day_1D': 1,
        }
    ]

    expense_X, expense_y = split_features_and_target(
        rows,
        target_name='Target_Expense_Total',
    )

    income_X, income_y = split_features_and_target(
        rows,
        target_name='Target_Income_Total',
    )

    assert expense_X == income_X

    assert expense_y == [500.0]

    assert income_y == [1000.0]

    assert expense_y != income_y
