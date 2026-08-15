import math

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# ==========================================================
# REGRESSION METRICS
# ==========================================================

def calculate_metrics(
    y_true,
    y_pred,
):
    """
    Calculate regression evaluation metrics.

    Returns:
        dict containing:

        - mae
        - rmse
        - r_squared

    Important:

        A target value of 0.0 is a valid observation.

        R² requires at least two observations and a
        non-constant true target.

        When R² cannot be calculated meaningfully,
        r_squared is returned as None.
    """

    if y_true is None or y_pred is None:
        raise ValueError(
            'y_true and y_pred are required.'
        )

    if len(y_true) == 0:
        raise ValueError(
            'At least one observation is required '
            'for metric calculation.'
        )

    if len(y_true) != len(y_pred):
        raise ValueError(
            'y_true and y_pred must have the same length.'
        )

    # ------------------------------------------------------
    # Convert values to float
    # ------------------------------------------------------

    true_values = [
        float(value)
        for value in y_true
    ]

    predicted_values = [
        float(value)
        for value in y_pred
    ]

    # ------------------------------------------------------
    # Validate finite values
    # ------------------------------------------------------

    if not all(
        math.isfinite(value)
        for value in true_values
    ):
        raise ValueError(
            'y_true contains a non-finite value.'
        )

    if not all(
        math.isfinite(value)
        for value in predicted_values
    ):
        raise ValueError(
            'y_pred contains a non-finite value.'
        )

    # ------------------------------------------------------
    # MAE
    # ------------------------------------------------------

    mae = mean_absolute_error(
        true_values,
        predicted_values,
    )

    # ------------------------------------------------------
    # RMSE
    # ------------------------------------------------------

    mse = mean_squared_error(
        true_values,
        predicted_values,
    )

    rmse = mse ** 0.5

    # ------------------------------------------------------
    # R²
    #
    # R² is not meaningful when:
    #
    #   - fewer than two observations exist
    #   - all true target values are identical
    #
    # A real target value of 0.0 does NOT make R² invalid
    # by itself.
    # ------------------------------------------------------

    r_squared = None

    if len(true_values) >= 2:

        unique_true_values = set(
            true_values
        )

        if len(unique_true_values) > 1:

            calculated_r_squared = r2_score(
                true_values,
                predicted_values,
            )

            if math.isfinite(
                float(calculated_r_squared)
            ):
                r_squared = float(
                    calculated_r_squared
                )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    return {
        'mae': float(mae),
        'rmse': float(rmse),
        'r_squared': r_squared,
    }