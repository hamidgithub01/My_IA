import math

from datetime import date, timedelta
from ml.preparation.preparation import get_prepared_dataset
from ml.preparation.preparation import (
    get_prepared_dataset,
)

from ml.features.build import build_feature_row

from ml.models.registry import (
    REGISTRY_VALID,
    REGISTRY_NOT_FOUND,
    REGISTRY_INVALID,
    get_active_model_version,
    load_active_model,
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
    the feature schema stored with the active registered model.

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
# LOAD ACTIVE REGISTERED MODEL
# ==========================================================

def generate_expense_forecast(
    days=30,
    target_name=DEFAULT_TARGET_NAME,
    registry_dir=None,
):
    """
    Generate a multi-day expense forecast.

    Future feature rows are constructed from the prepared
    dataset and historical rows.

    No training is performed.
    """

    if not isinstance(days, int) or days <= 0:
        raise ValueError(
            'days must be a positive integer.'
        )

    model_info = load_active_registered_model(
        target_name=target_name,
        registry_dir=registry_dir,
    )

    if model_info['status'] != PREDICTION_VALID:

        return {
            'status':
                model_info['status'],

            'forecast':
                [],

            'error':
                model_info.get(
                    'error'
                ),

            'target_name':
                target_name,

            'version':
                model_info.get(
                    'version'
                ),
        }

    metadata = model_info.get(
        'metadata'
    )

    if not isinstance(
        metadata,
        dict,
    ):

        return {
            'status':
                PREDICTION_INVALID,

            'forecast':
                [],

            'error':
                'Registered model metadata is invalid.',

            'target_name':
                target_name,

            'version':
                model_info.get(
                    'version'
                ),
        }

    feature_names = metadata.get(
        'feature_names'
    )

    if not isinstance(
        feature_names,
        list,
    ) or not feature_names:

        return {
            'status':
                PREDICTION_INVALID,

            'forecast':
                [],

            'error':
                'Registered model feature_names are invalid.',

            'target_name':
                target_name,

            'version':
                model_info.get(
                    'version'
                ),
        }

    # ------------------------------------------------------
    # Load prepared historical / known-future data
    # ------------------------------------------------------

    prepared_dataset = get_prepared_dataset()

    if not isinstance(
        prepared_dataset,
        list,
    ) or not prepared_dataset:

        return {
            'status':
                PREDICTION_INVALID,

            'forecast':
                [],

            'error':
                'Prepared dataset is empty.',

            'target_name':
                target_name,

            'version':
                model_info.get(
                    'version'
                ),
        }

    # ------------------------------------------------------
    # Sort by date
    # ------------------------------------------------------

    prepared_dataset = sorted(
        prepared_dataset,
        key=lambda row: row['Date'],
    )

    # ------------------------------------------------------
    # Historical rows available before the first forecast day
    # ------------------------------------------------------

    historical_rows = list(
        prepared_dataset
    )

    last_known_date = historical_rows[-1][
        'Date'
    ]

    start_date = (
        last_known_date + timedelta(days=1)
    )

    forecast = []

    # ------------------------------------------------------
    # Generate future predictions sequentially.
    #
    # Each future day becomes available to the history
    # for the next prediction.
    #
    # IMPORTANT:
    # The predicted Expense_Total is NOT inserted into
    # the target row as an actual outcome.
    # ------------------------------------------------------

    for offset in range(days):

        forecast_date = (
            start_date
            + timedelta(days=offset)
        )

        # --------------------------------------------------
        # Build a future target row.
        #
        # Start with a neutral row containing the fields
        # expected by the feature-building pipeline.
        # --------------------------------------------------

        target_row = {
            key: None
            for key in historical_rows[-1].keys()
        }

        target_row['Date'] = forecast_date

        # --------------------------------------------------
        # Future actual outcomes are unknown.
        #
        # Numeric actual fields are initialized to zero
        # only because this row is a structural future row;
        # these values must NOT become prediction features.
        # --------------------------------------------------

        for key in (
            'Expense_Total',
            'Expense_Count',
            'Income_Total',
            'Income_Count',
            'Event_Count',
            'Health_Record_Count',
            'Max_Health_Severity',
            'Avg_Energy_Level',
            'Activity_Count',
            'Activity_Duration_Minutes',
            'Activity_Cost',
            'Sleep_Record_Count',
            'Sleep_Duration_Minutes',
            'Avg_Sleep_Quality',
            'Total_Awakenings',
        ):

            if key in target_row:

                target_row[key] = 0.0

        # --------------------------------------------------
        # Known future information can be inherited from
        # the prepared dataset only when the exact future
        # date exists there.
        #
        # Otherwise keep unknown fields as None.
        # --------------------------------------------------

        prepared_by_date = {
            row['Date']: row
            for row in prepared_dataset
        }

        known_future_row = prepared_by_date.get(
            forecast_date
        )

        if known_future_row is not None:

            for key in (
                'Day_Type',
                'Work_Status',
                'Health_Impact',
                'Travel',
                'Special_Event',
                'Stress_Level',
                'Notes',
                'Sleep_Hours',
                'Social_Activity',
                'Location',
                'Plan_Count',
                'Plan_Expected_Cost',
                'Plan_Duration_Days',
                'High_Importance_Plan_Count',
                'Active_Plan_Count',
                'Active_Plan_Expected_Cost',
                'Active_High_Importance_Plan_Count',
                'Recurring_Count',
                'Recurring_Amount',
                'Recurring_Expense_Amount',
                'Recurring_Income_Amount',
                'Fixed_Recurring_Amount',
            ):

                if key in known_future_row:

                    target_row[key] = (
                        known_future_row[key]
                    )

        # --------------------------------------------------
        # Build features using ONLY:
        #
        #   target_row
        #   previous historical rows
        #
        # build_feature_row() itself guarantees that target
        # day actual outcomes are not used as historical
        # features.
        # --------------------------------------------------

        features = build_feature_row(
            target_row=target_row,
            previous_rows=historical_rows,
        )

        # --------------------------------------------------
        # Keep only the model's registered feature schema.
        #
        # Date and any auxiliary fields generated by the
        # feature builder are excluded unless registered.
        # --------------------------------------------------

        model_features = {}

        for feature_name in feature_names:

            if feature_name not in features:

                return {
                    'status':
                        PREDICTION_INVALID,

                    'forecast':
                        forecast,

                    'error':
                        (
                            'Feature generated by '
                            f'build_feature_row is missing: '
                            f'{feature_name}'
                        ),

                    'target_name':
                        target_name,

                    'version':
                        model_info.get(
                            'version'
                        ),
                }

            model_features[
                feature_name
            ] = features[
                feature_name
            ]

        # --------------------------------------------------
        # Predict
        # --------------------------------------------------

        result = predict_from_registered_model(
            features=model_features,
            target_name=target_name,
            registry_dir=registry_dir,
        )

        if result['status'] != PREDICTION_VALID:

            return {
                'status':
                    PREDICTION_INVALID,

                'forecast':
                    forecast,

                'error':
                    result.get(
                        'error'
                    ),

                'target_name':
                    target_name,

                'version':
                    model_info.get(
                        'version'
                    ),
            }

        prediction = result[
            'prediction'
        ]

        forecast.append({
            'Date':
                forecast_date,

            'Predicted_Expense':
                prediction,
        })

        # --------------------------------------------------
        # IMPORTANT:
        #
        # The prediction is NOT added to target_row as
        # Expense_Total.
        #
        # This prevents predicted values from becoming
        # fake historical observations.
        #
        # The target row itself is therefore NOT appended
        # to historical_rows.
        # --------------------------------------------------

    return {
        'status':
            PREDICTION_VALID,

        'forecast':
            forecast,

        'target_name':
            target_name,

        'version':
            model_info.get(
                'version'
            ),
    }


# ==========================================================
# EXPLICIT ACTIVE MODEL API
# ==========================================================

def load_latest_registered_model(
    target_name=DEFAULT_TARGET_NAME,
    registry_dir=None,
):
    """
    Load the active registered model for a target.

    The historical function name is preserved for
    backward compatibility.

    Prediction always uses the ACTIVE registered model.
    """

    target_name = _validate_target_name(
        target_name
    )

    version = get_active_model_version(
        target_name,
        registry_dir,
    )

    if version is None:
        return {
            'status': PREDICTION_MODEL_NOT_FOUND,
            'target_name': target_name,
            'version': None,
            'model': None,
            'metadata': None,
            'model_path': None,
            'metadata_path': None,
        }

    result = load_active_model(
        target_name,
        registry_dir,
    )

    if result['status'] == REGISTRY_VALID:
        return {
            'status': PREDICTION_VALID,
            'target_name': target_name,
            'version': result.get(
                'version',
                version,
            ),
            'model': result['model'],
            'metadata': result['metadata'],
            'model_path': result['model_path'],
            'metadata_path': result['metadata_path'],
        }

    if result['status'] == REGISTRY_NOT_FOUND:
        return {
            'status': PREDICTION_MODEL_NOT_FOUND,
            'target_name': target_name,
            'version': result.get(
                'version',
                version,
            ),
            'model': None,
            'metadata': result.get('metadata'),
            'model_path': result.get('model_path'),
            'metadata_path': result.get(
                'metadata_path'
            ),
        }

    return {
        'status': PREDICTION_INVALID,
        'target_name': target_name,
        'version': result.get(
            'version',
            version,
        ),
        'model': None,
        'metadata': result.get('metadata'),
        'model_path': result.get('model_path'),
        'metadata_path': result.get(
            'metadata_path'
        ),
        'error': result.get('error'),
    }


def load_active_registered_model(
    target_name=DEFAULT_TARGET_NAME,
    registry_dir=None,
):
    """
    Explicit public API for loading the active registered model.

    This is the preferred name for new callers.

    The older load_latest_registered_model() name is preserved
    for backward compatibility and now also loads ACTIVE.
    """

    return load_latest_registered_model(
        target_name=target_name,
        registry_dir=registry_dir,
    )


# ==========================================================
# REGISTERED MODEL PREDICTION
# ==========================================================

def predict_from_registered_model(
    features,
    target_name=DEFAULT_TARGET_NAME,
    registry_dir=None,
):
    """
    Generate a prediction using the active registered model.

    Pipeline:

        Load active registered model
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

    model_info = load_active_registered_model(
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

    Uses the active registered model.

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
        '       ACTIVE REGISTERED MODEL PREDICTION TEST'
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
        load_active_registered_model(
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
        'Active model version:',
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
        '   ACTIVE REGISTERED MODEL PREDICTION TEST PASSED'
    )

    print(
        '=================================================='
    )


# ==========================================================
# BACKWARD-COMPATIBLE FEATURE VALUE VALIDATOR
# ==========================================================

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


# ==========================================================
# EXPENSE FORECAST
# ==========================================================

def generate_expense_forecast(
    days=30,
    target_name=DEFAULT_TARGET_NAME,
    registry_dir=None,
):
    """
    Generate a multi-day expense forecast.

    Uses the active registered model.

    IMPORTANT:

        Forecast features are built through the same feature
        engineering pipeline used by the project.

        For every forecast date:

            target_row
                  +
            historical rows strictly before today
                  ↓
            build_feature_row()
                  ↓
            registered model
                  ↓
            prediction

        The target day's actual outcomes are never passed
        as prediction features.

        Known future information such as Plans and Recurring
        activity is taken from target_row.

        Historical features, lag features and rolling
        features are built only from historical rows.

    The current day is NOT included in the historical rows
    used for future inference because the current day may
    still be in progress.
    """

    if not isinstance(
        days,
        int,
    ) or days <= 0:

        raise ValueError(
            'days must be a positive integer.'
        )

    # ------------------------------------------------------
    # Load active registered model.
    # ------------------------------------------------------

    model_info = load_active_registered_model(
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

            'forecast':
                [],

            'error':
                model_info.get(
                    'error'
                ),

            'target_name':
                target_name,

            'version':
                model_info.get(
                    'version'
                ),
        }

    metadata = model_info.get(
        'metadata'
    )

    if not isinstance(
        metadata,
        dict,
    ):

        return {

            'status':
                PREDICTION_INVALID,

            'forecast':
                [],

            'error':
                'Registered model metadata is invalid.',

            'target_name':
                target_name,

            'version':
                model_info.get(
                    'version'
                ),
        }

    feature_names = metadata.get(
        'feature_names'
    )

    if not isinstance(
        feature_names,
        list,
    ) or not feature_names:

        return {

            'status':
                PREDICTION_INVALID,

            'forecast':
                [],

            'error':
                'Registered model feature_names are invalid.',

            'target_name':
                target_name,

            'version':
                model_info.get(
                    'version'
                ),
        }

    # ------------------------------------------------------
    # Load the prepared daily dataset.
    #
    # This is essential because future Plans and Recurring
    # information must reach the prediction pipeline.
    # ------------------------------------------------------

    prepared_data = get_prepared_dataset()

    if prepared_data is None:

        return {

            'status':
                PREDICTION_INVALID,

            'forecast':
                [],

            'error':
                'Prepared dataset is unavailable.',

            'target_name':
                target_name,

            'version':
                model_info.get(
                    'version'
                ),
        }

    if not isinstance(
        prepared_data,
        list,
    ):

        return {

            'status':
                PREDICTION_INVALID,

            'forecast':
                [],

            'error':
                'Prepared dataset must be a list.',

            'target_name':
                target_name,

            'version':
                model_info.get(
                    'version'
                ),
        }

    # ------------------------------------------------------
    # Sort prepared data chronologically.
    # ------------------------------------------------------

    prepared_data = sorted(
        prepared_data,
        key=lambda row: row.get(
            'Date'
        )
        if isinstance(
            row,
            dict,
        )
        else date.min,
    )

    # ------------------------------------------------------
    # Build a direct date → prepared row lookup.
    #
    # This allows future forecast dates to receive their
    # known Plans / Recurring information.
    # ------------------------------------------------------

    rows_by_date = {}

    for row in prepared_data:

        if not isinstance(
            row,
            dict,
        ):

            continue

        row_date = row.get(
            'Date'
        )

        if row_date is None:

            continue

        rows_by_date[
            row_date
        ] = row

    # ------------------------------------------------------
    # Historical inference boundary.
    #
    # Only dates strictly before today are treated as
    # historical observations.
    #
    # This prevents today's potentially incomplete actual
    # outcomes from entering the historical feature set.
    # ------------------------------------------------------

    today = date.today()

    historical_rows = [
        row
        for row in prepared_data
        if isinstance(
            row,
            dict,
        )
        and row.get(
            'Date'
        ) is not None
        and row.get(
            'Date'
        ) < today
    ]

    # ------------------------------------------------------
    # Ensure chronological ordering of historical rows.
    # ------------------------------------------------------

    historical_rows = sorted(
        historical_rows,
        key=lambda row: row[
            'Date'
        ],
    )

    forecast = []

    # ------------------------------------------------------
    # Generate each future prediction.
    # ------------------------------------------------------

    for offset in range(
        days
    ):

        forecast_date = (
            today
            + timedelta(
                days=offset
            )
        )

        # --------------------------------------------------
        # Get the prepared row for this forecast date.
        #
        # If the preparation stage has no row for the date,
        # create a minimal calendar row. build_feature_row()
        # will then safely produce zero known-future values.
        #
        # This fallback does NOT fabricate historical data.
        # --------------------------------------------------

        target_row = rows_by_date.get(
            forecast_date
        )

        if target_row is None:

            target_row = {
                'Date':
                    forecast_date,
            }

        else:

            # ----------------------------------------------
            # Do not mutate the preparation dataset.
            # ----------------------------------------------

            target_row = dict(
                target_row
            )

            target_row[
                'Date'
            ] = forecast_date

        # --------------------------------------------------
        # Build prediction features through the real feature
        # engineering pipeline.
        #
        # build_feature_row() provides:
        #
        #     Temporal
        #     Known Future
        #     History
        #     Lag
        #     Rolling
        #
        # The actual target-day outcomes are not used by
        # build_feature_row().
        # --------------------------------------------------

        features = build_feature_row(
            target_row=target_row,
            previous_rows=historical_rows,
        )

        # --------------------------------------------------
        # The Date field identifies the forecast day but is
        # not a model feature.
        #
        # get_feature_names() and training explicitly exclude
        # Date, while the registered model schema contains
        # only actual model features.
        # --------------------------------------------------

        features.pop(
            'Date',
            None,
        )

        # --------------------------------------------------
        # Strictly verify that the feature engineering output
        # matches the registered model schema.
        # --------------------------------------------------

        try:

            validate_feature_schema(
                features,
                feature_names,
            )

        except ValueError as exc:

            return {

                'status':
                    PREDICTION_INVALID,

                'forecast':
                    forecast,

                'error':
                    (
                        'Forecast feature schema validation '
                        f'failed: {exc}'
                    ),

                'target_name':
                    target_name,

                'version':
                    model_info.get(
                        'version'
                    ),
            }

        # --------------------------------------------------
        # Generate the prediction.
        # --------------------------------------------------

        result = predict_from_registered_model(
            features=features,
            target_name=target_name,
            registry_dir=registry_dir,
        )

        if result[
            'status'
        ] != PREDICTION_VALID:

            return {

                'status':
                    PREDICTION_INVALID,

                'forecast':
                    forecast,

                'error':
                    result.get(
                        'error'
                    ),

                'target_name':
                    target_name,

                'version':
                    model_info.get(
                        'version'
                    ),
            }

        prediction = result[
            'prediction'
        ]

        # --------------------------------------------------
        # Expense cannot be negative.
        #
        # A regression model may mathematically return a
        # negative value even though an expense cannot be
        # negative.
        # --------------------------------------------------

        prediction = max(
            0.0,
            float(
                prediction
            ),
        )

        forecast.append({

            'Date':
                forecast_date,

            'Predicted_Expense':
                prediction,
        })

    return {

        'status':
            PREDICTION_VALID,

        'forecast':
            forecast,

        'target_name':
            target_name,

        'version':
            model_info.get(
                'version'
            ),
    }


# ==========================================================
# PREDICTIONS PAGE DATA
# ==========================================================

def load_predictions_page_data(
    days=30,
    target_name=DEFAULT_TARGET_NAME,
    registry_dir=None,
):
    """
    Load all data required by the Predictions page.
    """

    forecast_result = generate_expense_forecast(
        days=days,
        target_name=target_name,
        registry_dir=registry_dir,
    )

    forecast = forecast_result.get(
        'forecast',
        [],
    )

    values = [
        float(
            row.get(
                'Predicted_Expense',
                0.0,
            )
        )
        for row in forecast
    ]

    summary = {

        'days':
            len(forecast),

        'total':
            sum(values),

        'average_daily':
            (
                sum(values) / len(values)
                if values
                else 0.0
            ),

        'minimum':
            min(values)
            if values
            else 0.0,

        'maximum':
            max(values)
            if values
            else 0.0,

        'first_day':
            (
                forecast[0].get(
                    'Date'
                )
                if forecast
                else None
            ),

        'last_day':
            (
                forecast[-1].get(
                    'Date'
                )
                if forecast
                else None
            ),
    }

    model = {

        'target_name':
            target_name,

        'version':
            forecast_result.get(
                'version'
            ),

        'feature_count':
            None,
    }

    model_info = load_active_registered_model(
        target_name=target_name,
        registry_dir=registry_dir,
    )

    if model_info.get(
        'status'
    ) == PREDICTION_VALID:

        metadata = model_info.get(
            'metadata'
        )

        if isinstance(
            metadata,
            dict,
        ):

            feature_names = metadata.get(
                'feature_names'
            )

            if isinstance(
                feature_names,
                list,
            ):

                model['feature_count'] = len(
                    feature_names
                )

        model['version'] = model_info.get(
            'version'
        )

    return {

        'status':
            forecast_result.get(
                'status',
                PREDICTION_INVALID,
            ),

        'forecast':
            forecast,

        'summary':
            summary,

        'model':
            model,

        'error':
            forecast_result.get(
                'error'
            ),
    }