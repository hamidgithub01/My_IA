import json

from database.connection import get_connection

def _decode_json_field(
    value,
    default,
):
    if value is None:
        return default

    if isinstance(
        value,
        str,
    ):
        return json.loads(
            value
        )

    if isinstance(
        value,
        (list, dict),
    ):
        return value

    raise ValueError(
        'Invalid JSON field type.'
    )


# ==========================================================
# MODEL REGISTRY
# ==========================================================

def get_latest_model_history():
    """
    Return the most recently saved model history record.

    Returns:
        Dictionary containing the latest model information,
        or None when no model has been saved yet.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
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
            FROM model_history
            ORDER BY id DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

        if row is None:
            return None

        # --------------------------------------------------
        # Decode JSON fields
        # --------------------------------------------------

        row['feature_names'] = _decode_json_field(
            row['feature_names'],
            []
        )

        row['coefficients'] = _decode_json_field(
            row['coefficients'],
            []
        )

        row['feature_means'] = _decode_json_field(
            row['feature_means'],
            {}
        )

        row['feature_scales'] = _decode_json_field(
            row['feature_scales'],
            {}
        )

        return row

    finally:

        cursor.close()
        connection.close()


def get_model_history_by_id(
    model_history_id,
):
    """
    Return a specific model history record.

    Args:
        model_history_id:
            ID of the model history record.

    Returns:
        Dictionary containing the model information,
        or None when the record does not exist.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
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
            FROM model_history
            WHERE id = %s
            LIMIT 1
            """,
            (
                model_history_id,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        # --------------------------------------------------
        # Decode JSON fields
        # --------------------------------------------------

        row['feature_names'] = _decode_json_field(
            row['feature_names'],
            []
        )

        row['coefficients'] = _decode_json_field(
            row['coefficients'],
            []
        )

        row['feature_means'] = _decode_json_field(
            row['feature_means'],
            {}
        )

        row['feature_scales'] = _decode_json_field(
            row['feature_scales'],
            {}
        )

        return row

    finally:

        cursor.close()
        connection.close()

