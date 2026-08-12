from sklearn.linear_model import LinearRegression

from ml.features.build import build_feature_dataset


# ==========================================================
# MODEL TRAINING
# ==========================================================

def train_model():
    """
    Train a Linear Regression model using the engineered
    daily financial features.

    Target:
        Expense_Total

    Returns:
        {
            'model': trained model,
            'feature_names': list of feature names,
            'training_rows': number of rows,
        }
    """

    data = build_feature_dataset()

    if not data:
        raise ValueError(
            'No feature data available for training.'
        )

    # ------------------------------------------------------
    # Target
    # ------------------------------------------------------

    target_name = 'Expense_Total'

    # ------------------------------------------------------
    # Features
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Build X and y
    # ------------------------------------------------------

    X = []

    y = []

    for row in data:

        X.append([
            float(row[feature])
            for feature in feature_names
        ])

        y.append(
            float(row[target_name])
        )

    # ------------------------------------------------------
    # Train model
    # ------------------------------------------------------

    model = LinearRegression()

    model.fit(X, y)

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    return {
        'model': model,
        'feature_names': feature_names,
        'training_rows': len(data),
    }