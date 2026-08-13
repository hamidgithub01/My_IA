from ml.features.build import build_feature_dataset
from ml.training.load import load_latest_model


# ==========================================================
# PREDICTION
# ==========================================================

def predict_expense_for_date(target_date):
    """
    Predict the total expense for a specific date
    using the latest saved model.

    The prediction does not retrain the model.

    Args:
        target_date:
            Date to predict.

    Returns:
        Dictionary containing:
            - Date
            - Predicted_Expense
            - Model_History_ID
            - Features
    """

    # ------------------------------------------------------
    # Load feature data
    # ------------------------------------------------------

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
    # Load latest saved model
    # ------------------------------------------------------

    model_result = load_latest_model()

    if model_result is None:
        raise ValueError(
            'No trained model is available.'
        )

    model = model_result['model']

    feature_names = (
        model_result['feature_names']
    )

    model_history_id = (
        model_result['model_history_id']
    )

    # ------------------------------------------------------
    # Validate feature structure
    # ------------------------------------------------------

    missing_features = [
        feature
        for feature in feature_names
        if feature not in target_row
    ]

    if missing_features:

        raise ValueError(
            'Missing features for prediction: '
            + ', '.join(missing_features)
        )

    # ------------------------------------------------------
    # Build feature vector
    # ------------------------------------------------------

    feature_vector = [
        float(
            target_row[feature]
            or 0.0
        )
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
        float(predicted_expense),
    )

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    return {
        'Date':
            target_date,

        'Predicted_Expense':
            predicted_expense,

        'Model_History_ID':
            model_history_id,

        'Features': {
            feature:
                target_row[feature]
            for feature in feature_names
        },
    }