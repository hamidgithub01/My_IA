from datetime import date

from ml.prediction.predict import predict_expense_for_date


# ==========================================================
# EXPENSE PREDICTION SERVICE
# ==========================================================

def get_expense_prediction(target_date):
    """
    Return the predicted expense for a specific date.

    Args:
        target_date:
            A datetime.date object.

    Returns:
        Dictionary containing:
            - Date
            - Predicted_Expense
            - Features
    """

    if not isinstance(target_date, date):
        raise TypeError(
            'target_date must be a datetime.date object.'
        )

    return predict_expense_for_date(target_date)


def get_predicted_expense(target_date):
    """
    Return only the predicted expense amount.
    """

    result = get_expense_prediction(target_date)

    return result['Predicted_Expense']


def get_prediction_features(target_date):
    """
    Return the features used by the model
    for the requested date.
    """

    result = get_expense_prediction(target_date)

    return result['Features']