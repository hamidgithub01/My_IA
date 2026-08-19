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
                model_type,
                target_name,
                target_task,
                target_type,
                class_count,
                training_rows,
                feature_names,
                coefficients,
                classes,
                intercept,
                feature_means,
                feature_scales,
                mae,
                rmse,
                r_squared,
                evaluation_status,
                evaluation_metrics,
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

        row['classes'] = _decode_json_field(
            row['classes'],
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

        row['evaluation_metrics'] = _decode_json_field(
            row['evaluation_metrics'],
            {}
        )

        return row

    finally:

        cursor.close()
        connection.close()

def get_latest_model_history_by_target(
    target_name,
):
    """
    Return the most recently saved model history record
    for a specific target.

    Returns:
        Dictionary containing the latest model information
        for the target, or None when no model exists.
    """

    if not target_name:
        raise ValueError(
            'target_name is required.'
        )

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
                model_type,
                target_name,
                target_task,
                target_type,
                class_count,
                training_rows,
                feature_names,
                coefficients,
                classes,
                intercept,
                feature_means,
                feature_scales,
                mae,
                rmse,
                r_squared,
                evaluation_status,
                evaluation_metrics,
                reused_previous_state
            FROM model_history
            WHERE target_name = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                target_name,
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
                model_type,
                target_name,
                target_task,
                target_type,
                class_count,
                training_rows,
                feature_names,
                coefficients,
                classes,
                intercept,
                feature_means,
                feature_scales,
                mae,
                rmse,
                r_squared,
                evaluation_status,
                evaluation_metrics,
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

