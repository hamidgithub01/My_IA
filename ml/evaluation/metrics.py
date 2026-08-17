import math

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
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

        mae
        rmse
        r_squared

    Notes:

        - Zero is a valid target value.
        - R² requires at least two observations.
        - R² is not meaningful when all true values are equal.
        - All values must be finite numeric values.
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
    # Convert to float
    # ------------------------------------------------------

    try:
        true_values = [
            float(value)
            for value in y_true
        ]

        predicted_values = [
            float(value)
            for value in y_pred
        ]

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            'Regression metric values must be numeric.'
        ) from exc

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

    rmse = math.sqrt(
        float(mse)
    )

    # ------------------------------------------------------
    # R²
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
    # Result
    # ------------------------------------------------------

    return {
        'mae': float(mae),
        'rmse': float(rmse),
        'r_squared': r_squared,
    }


# ==========================================================
# CLASSIFICATION METRICS
# ==========================================================

def calculate_classification_metrics(
    y_true,
    y_pred,
    average='weighted',
):
    """
    Calculate safe classification metrics.

    Supports:

        - Binary classification
        - Multiclass classification

    Metrics:

        - accuracy
        - precision
        - recall
        - f1

    Averaging:

        binary
        macro
        weighted
        micro
        samples
        None

    Important:

        This function does NOT guess whether the problem is
        binary or multiclass.

        The evaluation layer determines the appropriate
        averaging strategy.

        zero_division=0 is used to prevent metric failures
        when a class has no predicted samples.
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
    # Validate averaging strategy
    # ------------------------------------------------------

    allowed_averages = {
        'binary',
        'macro',
        'weighted',
        'micro',
        'samples',
        None,
    }

    if average not in allowed_averages:

        raise ValueError(
            'Unsupported classification averaging strategy: '
            f'{average!r}.'
        )

    # ------------------------------------------------------
    # Validate classes
    # ------------------------------------------------------

    true_classes = set(
        y_true
    )

    if len(true_classes) < 2:

        raise ValueError(
            'Classification metrics require at least '
            'two distinct classes in y_true.'
        )

    # ------------------------------------------------------
    # Binary averaging safety
    # ------------------------------------------------------

    if average == 'binary':

        if len(true_classes) != 2:

            raise ValueError(
                'average="binary" requires exactly two '
                'classes in y_true.'
            )

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    precision = precision_score(
        y_true,
        y_pred,
        average=average,
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        average=average,
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        average=average,
        zero_division=0,
    )

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    return {
        'accuracy': float(
            accuracy
        ),

        'precision': float(
            precision
        ),

        'recall': float(
            recall
        ),

        'f1': float(
            f1
        ),
    }