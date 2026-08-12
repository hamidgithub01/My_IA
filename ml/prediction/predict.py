from ml.features.build import build_feature_dataset
from ml.training.train import train_model


# ==========================================================
# PREDICTION
# ==========================================================

def predict_expense_for_date(target_date):
    """
    Predict the total expense for a specific date.

    The prediction is based on the engineered features
    already produced by the feature engineering pipeline.

    Args:
        target_date:
            Date to predict.

    Returns:
        Dictionary containing:
            - Date
            - Predicted_Expense
            - Features
    """

    data = build_feature_dataset()

    if not data:
        raise ValueError(
            'No feature data available for prediction.'
        )

    # ------------------------------------------------------
    # Find requested date
    # ------------------------------------------------------

    target_row = None

    for row in data:

        if row['Date'] == target_date:
            target_row = row
            break

    if target_row is None:
        raise ValueError(
            f'No feature data found for date: {target_date}'
        )

    # ------------------------------------------------------
    # Train / load model
    # ------------------------------------------------------

    training_result = train_model()

    model = training_result['model']
    feature_names = training_result['feature_names']

    # ------------------------------------------------------
    # Build feature vector
    # ------------------------------------------------------

    feature_vector = [
        float(target_row[feature])
        for feature in feature_names
    ]

    # ------------------------------------------------------
    # Prediction
    # ------------------------------------------------------

    predicted_expense = model.predict(
        [feature_vector]
    )[0]

    # ------------------------------------------------------
    # Expenses cannot be negative
    # ------------------------------------------------------

    predicted_expense = max(
        0.0,
        float(predicted_expense)
    )

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    return {
        'Date': target_date,
        'Predicted_Expense': predicted_expense,
        'Features': {
            feature: target_row[feature]
            for feature in feature_names
        },
    }