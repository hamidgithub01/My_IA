from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


def calculate_metrics(y_true, y_pred):
    """
    Calculate regression evaluation metrics.

    Returns:
        dict containing:
        - mae
        - rmse
        - r_squared
    """

    mae = mean_absolute_error(
        y_true,
        y_pred,
    )

    rmse = mean_squared_error(
        y_true,
        y_pred,
    ) ** 0.5

    r_squared = r2_score(
        y_true,
        y_pred,
    )

    return {
        'mae': float(mae),
        'rmse': float(rmse),
        'r_squared': float(r_squared),
    }