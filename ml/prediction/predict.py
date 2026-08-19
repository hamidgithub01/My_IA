import math


from ml.models.registry import (
    REGISTRY_VALID,
    REGISTRY_NOT_FOUND,
    REGISTRY_INVALID,
    get_latest_model_version,
    load_registered_model,
)


# ==========================================================
# PREDICTION STATUS
# ==========================================================

PREDICTION_VALID = 'valid'
PREDICTION_INVALID = 'invalid'
PREDICTION_MODEL_NOT_FOUND = 'model_not_found'


# ==========================================================
# DEFAULT TARGET
# ==========================================================

DEFAULT_TARGET_NAME = (
    'Target_Expense_Total_1D'
)


# ==========================================================
# BASIC VALIDATION
# ==========================================================

def _validate_target_name(
    target_name,
):
    """
    Validate target name.
    """

    if not isinstance(
        target_name,
        str,
    ):

        raise ValueError(
            'target_name must be a string.'
        )

    target_name = target_name.strip()

    if not target_name:

        raise ValueError(
            'target_name cannot be empty.'
        )

    return target_name


def _validate_features(
    features,
):
    """
    Validate the feature container.

    Features must be supplied as a dictionary:

        {
            'feature_a': 10.0,
            'feature_b': 5.0,
        }
    """

    if features is None:

        raise ValueError(
            'features are required.'
        )

    if not isinstance(
        features,
        dict,
    ):

        raise ValueError(
            'features must be a dictionary.'
        )

    if not features:

        raise ValueError(
            'features cannot be empty.'
        )

    return features


def _validate_numeric_feature(
    value,
    feature_name,
):
    """
    Validate one feature value.
    """

    if isinstance(
        value,
        bool,
    ):

        raise ValueError(
            f'Feature "{feature_name}" must be numeric.'
        )

    try:

        numeric_value = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            f'Feature "{feature_name}" must be numeric.'
        ) from exc

    if not math.isfinite(
        numeric_value
    ):

        raise ValueError(
            f'Feature "{feature_name}" must be finite.'
        )

    return numeric_value


# ==========================================================
# FEATURE SCHEMA VALIDATION
# ==========================================================

def validate_feature_schema(
    features,
    feature_names,
):
    """
    Validate that the supplied features exactly match
    the feature schema stored with the registered model.

    This is intentionally strict.

    Missing features are rejected.

    Unexpected features are rejected.

    Feature order is determined exclusively by
    feature_names from the registered model.
    """

    features = _validate_features(
        features
    )

    if feature_names is None:

        raise ValueError(
            'feature_names are required.'
        )

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

    normalized_feature_names = []

    for index, name in enumerate(
        feature_names
    ):

        if not isinstance(
            name,
            str,
        ):

            raise ValueError(
                'Feature name must be a string. '
                f'Index: {index}'
            )

        name = name.strip()

        if not name:

            raise ValueError(
                'Feature name cannot be empty. '
                f'Index: {index}'
            )

        normalized_feature_names.append(
            name
        )

    # ------------------------------------------------------
    # Duplicate feature names are not allowed.
    # ------------------------------------------------------

    if len(
        normalized_feature_names
    ) != len(
        set(normalized_feature_names)
    ):

        duplicates = sorted({
            name
            for name in normalized_feature_names
            if normalized_feature_names.count(name) > 1
        })

        raise ValueError(
            'Duplicate feature names are not allowed: '
            f'{duplicates}'
        )

    expected = set(
        normalized_feature_names
    )

    provided = set(
        features.keys()
    )

    missing = sorted(
        expected - provided
    )

    unexpected = sorted(
        provided - expected
    )

    if missing:

        raise ValueError(
            'Missing required features: '
            f'{missing}'
        )

    if unexpected:

        raise ValueError(
            'Unexpected features supplied: '
            f'{unexpected}'
        )

    return True


# ==========================================================
# BUILD FEATURE VECTOR
# ==========================================================

def build_feature_vector(
    features,
    feature_names,
):
    """
    Build the exact feature vector expected by the model.

    The order comes from the registered model metadata.

    This prevents accidental feature-order changes.
    """

    validate_feature_schema(
        features,
        feature_names,
    )

    vector = []

    for feature_name in feature_names:

        value = _validate_numeric_feature(
            features[
                feature_name
            ],
            feature_name,
        )

        vector.append(
            value
        )

    return [
        vector
    ]


# ==========================================================
# LOAD LATEST REGISTERED MODEL
# ==========================================================

def load_latest_registered_model(
    target_name=DEFAULT_TARGET_NAME,
    registry_dir=None,
):
    """
    Load the latest registered model for a target.

    No training is performed.

    Returns a structured result containing:

        status
        target_name
        version
        model
        metadata
        model_path
        metadata_path
    """

    target_name = _validate_target_name(
        target_name
    )

    version = get_latest_model_version(
        target_name,
        registry_dir,
    )

    if version is None:

        return {

            'status':
                PREDICTION_MODEL_NOT_FOUND,

            'target_name':
                target_name,

            'version':
                None,

            'model':
                None,

            'metadata':
                None,

            'model_path':
                None,

            'metadata_path':
                None,
        }

    result = load_registered_model(
        target_name,
        version,
        registry_dir,
    )

    if result[
        'status'
    ] == REGISTRY_VALID:

        return {

            'status':
                PREDICTION_VALID,

            'target_name':
                target_name,

            'version':
                version,

            'model':
                result[
                    'model'
                ],

            'metadata':
                result[
                    'metadata'
                ],

            'model_path':
                result[
                    'model_path'
                ],

            'metadata_path':
                result[
                    'metadata_path'
                ],
        }

    if result[
        'status'
    ] == REGISTRY_NOT_FOUND:

        return {

            'status':
                PREDICTION_MODEL_NOT_FOUND,

            'target_name':
                target_name,

            'version':
                version,

            'model':
                None,

            'metadata':
                result.get(
                    'metadata'
                ),

            'model_path':
                result.get(
                    'model_path'
                ),

            'metadata_path':
                result.get(
                    'metadata_path'
                ),
        }

    return {

        'status':
            PREDICTION_INVALID,

        'target_name':
            target_name,

        'version':
            version,

        'model':
            None,

        'metadata':
            result.get(
                'metadata'
            ),

        'model_path':
            result.get(
                'model_path'
            ),

        'metadata_path':
            result.get(
                'metadata_path'
            ),

        'error':
            result.get(
                'error'
            ),
    }


# ==========================================================
# REGISTERED MODEL PREDICTION
# ==========================================================

def predict_from_registered_model(
    features,
    target_name=DEFAULT_TARGET_NAME,
    registry_dir=None,
):
    """
    Generate a prediction using the latest registered model.

    Pipeline:

        Load latest registered model
              ↓
        Load metadata
              ↓
        Validate feature schema
              ↓
        Build feature vector
              ↓
        Predict

    No training is performed.
    """

    target_name = _validate_target_name(
        target_name
    )

    features = _validate_features(
        features
    )

    model_info = load_latest_registered_model(
        target_name=target_name,
        registry_dir=registry_dir,
    )

    if model_info[
        'status'
    ] != PREDICTION_VALID:

        return {

            'status':
                model_info[
                    'status'
                ],

            'target_name':
                target_name,

            'version':
                model_info.get(
                    'version'
                ),

            'prediction':
                None,

            'metadata':
                model_info.get(
                    'metadata'
                ),

            'model_path':
                model_info.get(
                    'model_path'
                ),

            'metadata_path':
                model_info.get(
                    'metadata_path'
                ),

            'error':
                model_info.get(
                    'error'
            ),
        }

    model = model_info[
        'model'
    ]

    metadata = model_info[
        'metadata'
    ]

    # ------------------------------------------------------
    # Validate registered model metadata.
    # ------------------------------------------------------

    if not isinstance(
        metadata,
        dict,
    ):

        return {

            'status':
                PREDICTION_INVALID,

            'target_name':
                target_name,

            'version':
                model_info[
                    'version'
                ],

            'prediction':
                None,

            'metadata':
                metadata,

            'model_path':
                model_info[
                    'model_path'
                ],

            'metadata_path':
                model_info[
                    'metadata_path'
                ],

            'error':
                'Registered model metadata is invalid.',
        }

    metadata_target_name = metadata.get(
        'target_name'
    )

    if metadata_target_name != target_name:

        return {

            'status':
                PREDICTION_INVALID,

            'target_name':
                target_name,

            'version':
                model_info[
                    'version'
                ],

            'prediction':
                None,

            'metadata':
                metadata,

            'model_path':
                model_info[
                    'model_path'
                ],

            'metadata_path':
                model_info[
                    'metadata_path'
                ],

            'error':
                'Registered model target_name does not '
                'match the requested target_name.',
        }

    if model is None:

        return {

            'status':
                PREDICTION_INVALID,

            'target_name':
                target_name,

            'version':
                model_info[
                    'version'
                ],

            'prediction':
                None,

            'metadata':
                metadata,

            'model_path':
                model_info[
                    'model_path'
                ],

            'metadata_path':
                model_info[
                    'metadata_path'
                ],

            'error':
                'Registered model is missing.',
        }

    if not hasattr(
        model,
        'predict',
    ):

        return {

            'status':
                PREDICTION_INVALID,

            'target_name':
                target_name,

            'version':
                model_info[
                    'version'
                ],

            'prediction':
                None,

            'metadata':
                metadata,

            'model_path':
                model_info[
                    'model_path'
                ],

            'metadata_path':
                model_info[
                    'metadata_path'
                ],

            'error':
                'Registered model does not provide '
                'a predict() method.',
        }

    feature_names = metadata.get(
        'feature_names'
    )

    try:

        X = build_feature_vector(
            features,
            feature_names,
        )

    except ValueError as exc:

        return {

            'status':
                PREDICTION_INVALID,

            'target_name':
                target_name,

            'version':
                model_info[
                    'version'
                ],

            'prediction':
                None,

            'metadata':
                metadata,

            'model_path':
                model_info[
                    'model_path'
                ],

            'metadata_path':
                model_info[
                    'metadata_path'
                ],

            'error':
                str(exc),
        }

    try:

        raw_prediction = model.predict(
            X
        )

    except Exception as exc:

        return {

            'status':
                PREDICTION_INVALID,

            'target_name':
                target_name,

            'version':
                model_info[
                    'version'
                ],

            'prediction':
                None,

            'metadata':
                metadata,

            'model_path':
                model_info[
                    'model_path'
                ],

            'metadata_path':
                model_info[
                    'metadata_path'
                ],

            'error':
                f'Model prediction failed: {exc}',
        }

    if raw_prediction is None:

        return {

            'status':
                PREDICTION_INVALID,

            'target_name':
                target_name,

            'version':
                model_info[
                    'version'
                ],

            'prediction':
                None,

            'metadata':
                metadata,

            'model_path':
                model_info[
                    'model_path'
                ],

            'metadata_path':
                model_info[
                    'metadata_path'
                ],

            'error':
                'Model returned no prediction.',
        }

    try:

        if hasattr(
            raw_prediction,
            'tolist',
        ):

            raw_prediction = (
                raw_prediction.tolist()
            )

        if isinstance(
            raw_prediction,
            (list, tuple),
        ):

            if len(
                raw_prediction
            ) != 1:

                raise ValueError(
                    'Expected exactly one prediction.'
                )

            prediction = (
                raw_prediction[0]
            )

        else:

            prediction = raw_prediction

        prediction = float(
            prediction
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        return {

            'status':
                PREDICTION_INVALID,

            'target_name':
                target_name,

            'version':
                model_info[
                    'version'
                ],

            'prediction':
                None,

            'metadata':
                metadata,

            'model_path':
                model_info[
                    'model_path'
                ],

            'metadata_path':
                model_info[
                    'metadata_path'
                ],

            'error':
                f'Invalid model prediction: {exc}',
        }

    if not math.isfinite(
        prediction
    ):

        return {

            'status':
                PREDICTION_INVALID,

            'target_name':
                target_name,

            'version':
                model_info[
                    'version'
                ],

            'prediction':
                None,

            'metadata':
                metadata,

            'model_path':
                model_info[
                    'model_path'
                ],

            'metadata_path':
                model_info[
                    'metadata_path'
                ],

            'error':
                'Model returned a non-finite prediction.',
        }

    return {

        'status':
            PREDICTION_VALID,

        'target_name':
            target_name,

        'version':
            model_info[
                'version'
            ],

        'prediction':
            prediction,

        'feature_count':
            len(
                feature_names
            ),

        'feature_names':
            list(
                feature_names
            ),

        'metadata':
            metadata,

        'model_path':
            model_info[
                'model_path'
            ],

        'metadata_path':
            model_info[
                'metadata_path'
            ],
    }


# ==========================================================
# BACKWARD-COMPATIBLE PUBLIC API
# ==========================================================

def predict(
    features,
    target_name=DEFAULT_TARGET_NAME,
    registry_dir=None,
):
    """
    Public prediction API.

    Uses the latest registered model.

    No training is performed.
    """

    return predict_from_registered_model(
        features=features,
        target_name=target_name,
        registry_dir=registry_dir,
    )


# ==========================================================
# SIMPLE MANUAL TEST
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )

    print(
        '       REGISTERED MODEL PREDICTION TEST'
    )

    print(
        '=================================================='
    )

    target_name = (
        DEFAULT_TARGET_NAME
    )

    print()
    print(
        'Target:',
        target_name,
    )

    model_info = (
        load_latest_registered_model(
            target_name
        )
    )

    print(
        'Registry status:',
        model_info[
            'status'
        ]
    )

    print(
        'Model version:',
        model_info[
            'version'
        ]
    )

    if model_info[
        'status'
    ] != PREDICTION_VALID:

        print()
        print(
            'Prediction test cannot continue.'
        )

        print(
            'Reason:',
            model_info.get(
                'error'
            ),
        )

        raise SystemExit(1)

    metadata = model_info[
        'metadata'
    ]

    feature_names = metadata[
        'feature_names'
    ]

    # ------------------------------------------------------
    # Build deterministic test features
    # ------------------------------------------------------

    features = {
        feature_name: 0.0
        for feature_name
        in feature_names
    }

    result = predict_from_registered_model(
        features=features,
        target_name=target_name,
    )

    print()
    print(
        'Prediction status:',
        result[
            'status'
        ]
    )

    print(
        'Target:',
        result[
            'target_name'
        ]
    )

    print(
        'Model version:',
        result[
            'version'
        ]
    )

    print(
        'Feature count:',
        result[
            'feature_count'
        ]
    )

    print(
        'Prediction:',
        result[
            'prediction'
        ]
    )

    if result[
        'status'
    ] != PREDICTION_VALID:

        print()
        print(
            'Error:',
            result.get(
                'error'
            ),
        )

        raise SystemExit(1)

    print()
    print(
        '=================================================='
    )

    print(
        '   REGISTERED MODEL PREDICTION TEST PASSED'
    )

    print(
        '=================================================='
    )


def _validate_feature_value(
    value,
    feature_name,
):
    """
    Backward-compatible alias for the feature-value validator.
    """

    return _validate_numeric_feature(
        value,
        feature_name,
    )