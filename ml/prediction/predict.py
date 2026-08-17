import math
from numbers import Number

from ml.training.load import (
    load_latest_model,
)


# ==========================================================
# FEATURE VALIDATION
# ==========================================================

def validate_prediction_features(
    data,
    feature_names,
):
    """
    Validate prediction input against the features stored
    with the trained model.

    Rules:
        - data must be a dictionary.
        - every trained feature must exist.
        - Date cannot be a model feature.
        - Target_* fields cannot be model features.
        - extra input fields are allowed.
    """

    if not isinstance(data, dict):
        raise TypeError(
            'Prediction data must be a dictionary.'
        )

    if not isinstance(feature_names, list):
        raise TypeError(
            'Model feature names must be a list.'
        )

    if not feature_names:
        raise ValueError(
            'Model contains no feature names.'
        )

    forbidden_features = [
        name
        for name in feature_names
        if (
            name == 'Date'
            or name.startswith('Target_')
        )
    ]

    if forbidden_features:
        raise ValueError(
            'Forbidden model features detected: '
            + ', '.join(forbidden_features)
        )

    missing_features = [
        name
        for name in feature_names
        if name not in data
    ]

    if missing_features:
        raise ValueError(
            'Missing prediction features: '
            + ', '.join(missing_features)
        )

    return True


# ==========================================================
# FEATURE VALUE VALIDATION
# ==========================================================

def validate_feature_value(
    feature_name,
    value,
):
    """
    Validate and normalize one prediction feature value.

    Returns:
        float
    """

    if isinstance(value, bool):
        raise ValueError(
            f'Boolean value is not valid for feature: '
            f'{feature_name}'
        )

    if isinstance(value, Number):
        numeric_value = float(value)

    else:
        try:
            numeric_value = float(value)

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                f'Non-numeric value for feature: '
                f'{feature_name}'
            ) from exc

    if not math.isfinite(
        numeric_value
    ):
        raise ValueError(
            f'Feature contains a non-finite value: '
            f'{feature_name}'
        )

    return numeric_value


# ==========================================================
# FEATURE VECTOR
# ==========================================================

def build_prediction_vector(
    data,
    feature_names,
):
    """
    Build the prediction vector using exactly the same
    feature order stored with the trained model.

    No feature engineering is performed here.

    The caller must provide already prepared features.
    """

    validate_prediction_features(
        data,
        feature_names,
    )

    vector = []

    for feature_name in feature_names:

        value = data[
            feature_name
        ]

        numeric_value = validate_feature_value(
            feature_name,
            value,
        )

        vector.append(
            numeric_value
        )

    return vector


# ==========================================================
# PREDICTION
# ==========================================================

def predict(
    data,
):
    """
    Generate a prediction using the latest saved model.

    No training is performed.

    Returns:
        {
            'prediction': float,
            'target_name': str,
            'model_history_id': int | None,
            'feature_count': int,
        }
    """

    model_info = load_latest_model()

    if model_info is None:
        raise ValueError(
            'No trained model is available.'
        )

    model = model_info.get(
        'model'
    )

    feature_names = model_info.get(
        'feature_names'
    )

    target_name = model_info.get(
        'target_name'
    )

    model_history_id = model_info.get(
        'model_history_id'
    )

    if model is None:
        raise ValueError(
            'Loaded model is missing.'
        )

    if not feature_names:
        raise ValueError(
            'Loaded model contains no feature names.'
        )

    if not target_name:
        raise ValueError(
            'Loaded model contains no target name.'
        )

    vector = build_prediction_vector(
        data,
        feature_names,
    )

    prediction = model.predict([
        vector
    ])[0]

    prediction = float(
        prediction
    )

    if not math.isfinite(
        prediction
    ):
        raise ValueError(
            'Model produced a non-finite prediction.'
        )

    return {
        'prediction':
            prediction,

        'target_name':
            target_name,

        'model_history_id':
            model_history_id,

        'feature_count':
            len(feature_names),
    }


# ==========================================================
# BACKWARD-COMPATIBLE EXPENSE PREDICTION
# ==========================================================

def predict_expense(
    data,
):
    """
    Backward-compatible wrapper.

    The actual target is determined by the saved model.
    """

    return predict(
        data
    )