import json
from datetime import datetime

from database.connection import get_connection


# ==========================================================
# MODEL HISTORY
# ==========================================================

def save_model_history(
    training_result,
    evaluation_result,
    reused_previous_state=False,
):
    """
    Save a trained model and its evaluation metrics
    into the model_history table.

    Previous model history is never deleted.
    Each training operation creates a new record.
    """

    model = training_result['model']
    feature_names = training_result['feature_names']
    training_rows = training_result['training_rows']

    metrics = evaluation_result['metrics']

    coefficients = [
        float(value)
        for value in model.coef_
    ]

    intercept = float(
        model.intercept_
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
    # Model preprocessing statistics
    #
    # LinearRegression currently does not perform
    # feature scaling, therefore these values are
    # stored as empty JSON objects.
    # ------------------------------------------------------

    feature_means_json = json.dumps({})

    feature_scales_json = json.dumps({})

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
                %s
            )
            """,
            (
                datetime.now(),
                'LinearRegression',
                training_rows,
                feature_names_json,
                coefficients_json,
                intercept,
                feature_means_json,
                feature_scales_json,
                metrics['mae'],
                metrics['rmse'],
                metrics['r_squared'],
                bool(reused_previous_state),
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        cursor.close()
        connection.close()