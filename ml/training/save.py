import json
import math
from datetime import datetime

from database.connection import get_connection


# ==========================================================
# MODEL HISTORY
# ==========================================================

def save_model_history(
    training_result,
    evaluation_result=None,
    reused_previous_state=False,
):
    """
    Save a trained model and its evaluation metrics into
    the model_history table.

    Every training operation creates a new history record.

    Previous model history is never deleted.

    Evaluation metrics are stored only when they are valid.

    A target value of 0.0 is a valid training/evaluation
    observation and does not require any special handling.
    """

    # ------------------------------------------------------
    # Validate training result
    # ------------------------------------------------------

    if training_result is None:
        raise ValueError(
            'training_result is required.'
        )

    model = training_result.get(
        'model'
    )

    feature_names = training_result.get(
        'feature_names'
    )

    training_rows = training_result.get(
    'training_rows'
    )

    target_name = training_result.get(
        'target_name'
    )

    if model is None:
        raise ValueError(
            'Training result contains no model.'
        )

    if not feature_names:
        raise ValueError(
            'Training result contains no feature names.'
        )

    if training_rows is None:
        raise ValueError(
            'Training result contains no training row count.'
        )

    if not target_name:
         raise ValueError(
            'Training result contains no target name.'
    )

    # ------------------------------------------------------
    # Model parameters
    # ------------------------------------------------------

    coefficients = [
        float(value)
        for value in model.coef_
    ]

    intercept = float(
        model.intercept_
    )

    # ------------------------------------------------------
    # Validate feature / coefficient structure
    # ------------------------------------------------------

    if len(feature_names) != len(
        coefficients
    ):
        raise ValueError(
            'Feature count does not match coefficient count.'
        )

    # ------------------------------------------------------
    # Validate model parameters
    # ------------------------------------------------------

    if not all(
        math.isfinite(value)
        for value in coefficients
    ):
        raise ValueError(
            'Model coefficients contain a non-finite value.'
        )

    if not math.isfinite(
        intercept
    ):
        raise ValueError(
            'Model intercept is not finite.'
        )

    # ------------------------------------------------------
    # Feature names
    # ------------------------------------------------------

    feature_names_json = json.dumps(
        feature_names
    )

    # ------------------------------------------------------
    # Coefficients
    # ------------------------------------------------------

    coefficients_json = json.dumps(
        coefficients
    )

    # ------------------------------------------------------
    # Preprocessing statistics
    #
    # LinearRegression currently receives the features
    # without standardization.
    #
    # Therefore there are no means/scales to store.
    # ------------------------------------------------------

    feature_means_json = json.dumps(
        {}
    )

    feature_scales_json = json.dumps(
        {}
    )

    # ------------------------------------------------------
    # Evaluation metrics
    # ------------------------------------------------------

    mae = None
    rmse = None
    r_squared = None

    if evaluation_result is not None:

        metrics = evaluation_result.get(
            'metrics',
            {}
        )

        mae = metrics.get(
            'mae'
        )

        rmse = metrics.get(
            'rmse'
        )

        r_squared = metrics.get(
            'r_squared'
        )

        # --------------------------------------------------
        # Convert valid metrics to float.
        #
        # None remains None.
        # --------------------------------------------------

        if mae is not None:

            mae = float(mae)

            if not math.isfinite(
                mae
            ):
                mae = None

        if rmse is not None:

            rmse = float(rmse)

            if not math.isfinite(
                rmse
            ):
                rmse = None

        if r_squared is not None:

            r_squared = float(
                r_squared
            )

            if not math.isfinite(
                r_squared
            ):
                r_squared = None

    # ------------------------------------------------------
    # Database
    # ------------------------------------------------------

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO model_history (
                trained_at,
                algorithm,
                target_name,
                training_rows,
                feature_names,
                coefficients,
                intercept,
                feature_means,
                feature_scales,
                mae,
                rmse,
                r_squared,
                reused_previous_state
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                datetime.now(),
                'LinearRegression',
                target_name,
                int(training_rows),
                feature_names_json,
                coefficients_json,
                intercept,
                feature_means_json,
                feature_scales_json,
                mae,
                rmse,
                r_squared,
                bool(
                    reused_previous_state
                ),
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        cursor.close()
        connection.close()