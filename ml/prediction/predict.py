from numbers import Number

from ml.training.load import (
load_latest_model,
)

# ==========================================================

# CONSTANTS

# ==========================================================

TARGET_NAME = 'Target_Expense_Total'

# ==========================================================

# FEATURE VALIDATION

# ==========================================================

def validate_prediction_features(
            
    data,
    feature_names,
    ):
    """
    Validate that prediction data contains exactly the
    features expected by the trained model.

    ```
    Date and Target_* fields are never used as model input.
    """

    if not isinstance(data, dict):
        raise TypeError(
            'Prediction data must be a dictionary.'
        )

    if not feature_names:
        raise ValueError(
            'Model contains no feature names.'
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

    forbidden_features = []

    for name in feature_names:

        if name == 'Date':
            forbidden_features.append(name)

        elif name.startswith('Target_'):
            forbidden_features.append(name)

    if forbidden_features:
        raise ValueError(
            'Forbidden model features detected: '
            + ', '.join(forbidden_features)
        )

    return True


# ==========================================================

# FEATURE VECTOR

# ==========================================================

def build_prediction_vector(
            
    data,
    feature_names,
    ):
    """
    Build a prediction vector using exactly the same
    feature order stored with the trained model.

    ```
    Values must be numeric.
    """

    validate_prediction_features(
        data,
        feature_names,
    )

    vector = []

    for feature_name in feature_names:

        value = data.get(
            feature_name
        )

        if isinstance(value, bool):

            raise ValueError(
                f'Boolean value is not valid for '
                f'feature: {feature_name}'
            )

        if not isinstance(
            value,
            Number,
        ):

            try:
                value = float(value)

            except (
                TypeError,
                ValueError,
            ):

                raise ValueError(
                    f'Non-numeric value for '
                    f'feature: {feature_name}'
                )

        vector.append(
            float(value)
        )

    return vector

# ==========================================================

# MODEL PREDICTION

# ==========================================================

def predict_expense(
            
    data,
    ):
    """
    Generate an expense prediction using the latest
    saved model.

    ```
    No training is performed.

    Returns:
        Dictionary containing:
            - prediction
            - target_name
            - model_history_id
            - feature_count
    """

    model_info = load_latest_model()

    if model_info is None:

        raise ValueError(
            'No trained model is available.'
        )

    model = model_info[
        'model'
    ]

    feature_names = model_info[
        'feature_names'
    ]

    vector = build_prediction_vector(
        data,
        feature_names,
    )

    prediction = model.predict([
        vector
    ])[0]

    prediction = max(
        0.0,
        float(prediction),
    )

    return {
        'prediction':
            prediction,

        'target_name':
            TARGET_NAME,

        'model_history_id':
            model_info.get(
                'model_history_id'
            ),

        'feature_count':
            len(feature_names),
    }
