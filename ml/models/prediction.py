
import math


# ==========================================================
# PREDICTION STATUS
# ==========================================================

PREDICTION_VALID = 'valid'
PREDICTION_INVALID_INPUT = 'invalid_input'
PREDICTION_MODEL_NOT_FOUND = 'model_not_found'
PREDICTION_INVALID_MODEL = 'invalid_model'
PREDICTION_INVALID_FEATURES = 'invalid_features'
PREDICTION_INVALID_OUTPUT = 'invalid_output'


# ==========================================================
# BASIC VALIDATION
# ==========================================================

def _validate_model(
    model,
):
    """
    Validate that a model object is available and exposes
    the predict() interface.
    """

    if model is None:

        raise ValueError(
            'model is required.'
        )

    predict_method = getattr(
        model,
        'predict',
        None,
    )

    if not callable(
        predict_method
    ):

        raise ValueError(
            'model must provide a callable predict() method.'
        )


def _validate_feature_names(
    feature_names,
):
    """
    Validate feature name definitions.
    """

    if not isinstance(
        feature_names,
        list,
    ):

        raise ValueError(
            'feature_names must be a list.'
        )

    if not feature_names:

        raise ValueError(
            'feature_names cannot be empty.'
        )

    for feature_name in feature_names:

        if not isinstance(
            feature_name,
            str,
        ):

            raise ValueError(
                'Every feature name must be a string.'
            )

        if not feature_name.strip():

            raise ValueError(
                'Feature names cannot be empty.'
            )


def _validate_feature_vector(
    feature_values,
    expected_feature_count,
):
    """
    Validate one feature vector.
    """

    if feature_values is None:

        raise ValueError(
            'feature_values are required.'
        )

    try:

        values = list(
            feature_values
        )

    except TypeError:

        raise ValueError(
            'feature_values must be iterable.'
        )

    if len(values) != (
        expected_feature_count
    ):

        raise ValueError(
            'Feature count does not match '
            'the trained model.'
        )

    for value in values:

        try:

            numeric_value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                'All feature values must be numeric.'
            )

        if not math.isfinite(
            numeric_value
        ):

            raise ValueError(
                'Feature values must be finite.'
            )


def _validate_prediction_output(
    predictions,
):
    """
    Validate model prediction output.
    """

    if predictions is None:

        raise ValueError(
            'Model returned no predictions.'
        )

    try:

        predictions = list(
            predictions
        )

    except TypeError:

        raise ValueError(
            'Model predictions must be iterable.'
        )

    if not predictions:

        raise ValueError(
            'Model returned an empty prediction result.'
        )

    return predictions


# ==========================================================
# FEATURE MAPPING
# ==========================================================

def build_feature_vector(
    feature_names,
    feature_data,
):
    """
    Build a feature vector from a dictionary.

    The order is determined exclusively by feature_names.

    The feature schema is strict:

        - Missing features are rejected.
        - Unknown features are rejected.
        - Feature order follows feature_names exactly.
        - Feature values must be numeric and finite.

    This prevents accidental feature-schema changes during
    production inference.
    """

    _validate_feature_names(
        feature_names
    )

    if not isinstance(
        feature_data,
        dict,
    ):

        raise ValueError(
            'feature_data must be a dictionary.'
        )

    # ------------------------------------------------------
    # Missing features
    # ------------------------------------------------------

    missing_features = [
        feature_name
        for feature_name in feature_names
        if feature_name not in feature_data
    ]

    if missing_features:

        raise ValueError(
            'Missing required features: '
            f'{missing_features}'
        )

    # ------------------------------------------------------
    # Unknown features
    #
    # Production inference must use exactly the same
    # feature schema that was used during training.
    # ------------------------------------------------------

    unknown_features = [
        feature_name
        for feature_name in feature_data
        if feature_name not in feature_names
    ]

    if unknown_features:

        raise ValueError(
            'Unknown features were provided: '
            f'{unknown_features}'
        )

    # ------------------------------------------------------
    # Exact feature order
    # ------------------------------------------------------

    values = [
        feature_data[
            feature_name
        ]
        for feature_name in feature_names
    ]

    # ------------------------------------------------------
    # Numeric / finite validation
    # ------------------------------------------------------

    _validate_feature_vector(
        values,
        len(feature_names),
    )

    return values

     


# ==========================================================
# PREDICTION
# ==========================================================

def predict_with_model(
    model,
    feature_vector,
    feature_names,
):
    """
    Generate one production prediction.

    The model is assumed to have already been trained.
    """

    _validate_model(
        model
    )

    _validate_feature_names(
        feature_names
    )

    _validate_feature_vector(
        feature_vector,
        len(feature_names),
    )

    try:

        raw_predictions = model.predict(
            [
                feature_vector
            ]
        )

    except Exception as exc:

        raise ValueError(
            'Model prediction failed.'
        ) from exc

    predictions = _validate_prediction_output(
        raw_predictions
    )

    prediction = predictions[0]

    return prediction


# ==========================================================
# PRODUCTION PREDICTION
# ==========================================================

def generate_prediction(
    model,
    feature_names,
    feature_data,
    target_name,
    target_task,
    model_version=None,
):
    """
    Generate a structured production prediction.

    Parameters:

        model:
            Already-trained model.

        feature_names:
            Exact feature order used during training.

        feature_data:
            Dictionary containing production input features.

        target_name:
            Target being predicted.

        target_task:
            regression / classification / categorical.

        model_version:
            Optional registered model version.
    """

    if target_name is None:

        raise ValueError(
            'target_name is required.'
        )

    if target_task is None:

        raise ValueError(
            'target_task is required.'
        )

    feature_vector = build_feature_vector(
        feature_names,
        feature_data,
    )

    prediction = predict_with_model(
        model,
        feature_vector,
        feature_names,
    )

    return {

        'status':
            PREDICTION_VALID,

        'target_name':
            target_name,

        'target_task':
            target_task,

        'model_version':
            model_version,

        'prediction':
            prediction,

        'feature_count':
            len(feature_names),

        'feature_names':
            list(feature_names),

        'features':
            dict(feature_data),
    }


# ==========================================================
# BATCH PREDICTION
# ==========================================================

def generate_batch_predictions(
    model,
    feature_names,
    feature_data_list,
    target_name,
    target_task,
    model_version=None,
):
    """
    Generate predictions for multiple observations.

    Every observation is validated independently before
    prediction.
    """

    if feature_data_list is None:

        raise ValueError(
            'feature_data_list is required.'
        )

    try:

        feature_data_list = list(
            feature_data_list
        )

    except TypeError:

        raise ValueError(
            'feature_data_list must be iterable.'
        )

    if not feature_data_list:

        raise ValueError(
            'feature_data_list cannot be empty.'
        )

    results = []

    for feature_data in (
        feature_data_list
    ):

        result = generate_prediction(
            model,
            feature_names,
            feature_data,
            target_name,
            target_task,
            model_version,
        )

        results.append(
            result
        )

    return {

        'status':
            PREDICTION_VALID,

        'target_name':
            target_name,

        'target_task':
            target_task,

        'model_version':
            model_version,

        'prediction_count':
            len(results),

        'predictions':
            results,
    }


# ==========================================================
# TRAINING RESULT INTEGRATION
# ==========================================================

def generate_prediction_from_training_result(
    training_result,
    feature_data,
):
    """
    Generate a production prediction using the metadata
    contained in training_result.

    This is useful during the transition from training
    pipeline to production model registry.
    """

    if training_result is None:

        raise ValueError(
            'training_result is required.'
        )

    if not isinstance(
        training_result,
        dict,
    ):

        raise ValueError(
            'training_result must be a dictionary.'
        )

    required_keys = [
        'model',
        'feature_names',
        'target_name',
        'target_task',
    ]

    missing_keys = [
        key
        for key in required_keys
        if key not in training_result
    ]

    if missing_keys:

        raise ValueError(
            'training_result is missing required fields: '
            f'{missing_keys}'
        )

    return generate_prediction(
        model=training_result[
            'model'
        ],
        feature_names=training_result[
            'feature_names'
        ],
        feature_data=feature_data,
        target_name=training_result[
            'target_name'
        ],
        target_task=training_result[
            'target_task'
        ],
        model_version=training_result.get(
            'model_version'
        ),
    )


# ==========================================================
# SIMPLE MANUAL TEST
# ==========================================================

if __name__ == '__main__':

    class DemoModel:

        def predict(
            self,
            values,
        ):

            return [
                sum(values[0])
            ]

    model = DemoModel()
