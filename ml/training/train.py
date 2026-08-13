from sklearn.linear_model import LinearRegression

from ml.features.build import (
    build_training_dataset,
)


def train_model():
    """
    Train the financial forecasting model.

    The model learns:

        Historical information
                ↓
        Current/target day
                ↓
        Expense_Total

    The target expense is NEVER used as an input feature.
    """

    data = build_training_dataset()

    if not data:
        raise ValueError(
            'Not enough historical data for training.'
        )

    target_name = 'Target_Expense_Total'

    excluded_features = {
        'Date',
        target_name,
    }

    feature_names = [
        key
        for key in data[0].keys()
        if key not in excluded_features
    ]

    if not feature_names:
        raise ValueError(
            'No features available for training.'
        )

    X = []
    y = []

    for row in data:

        X.append([
            float(
                row.get(feature, 0.0)
                or 0.0
            )
            for feature in feature_names
        ])

        y.append(
            float(
                row[target_name]
            )
        )

    if len(X) < 2:
        raise ValueError(
            'At least two historical records are required '
            'for training.'
        )

    model = LinearRegression()

    model.fit(
        X,
        y,
    )

    return {
        'model': model,
        'feature_names': feature_names,
        'training_rows': len(data),
        'target_name': target_name,
    }