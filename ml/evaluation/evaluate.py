from ml.evaluation.metrics import (
    calculate_metrics,
    calculate_classification_metrics,
)


# ==========================================================
# EVALUATION STATUS
# ==========================================================

EVALUATION_VALID = 'valid'

EVALUATION_INSUFFICIENT_TRAINING_VARIATION = (
    'insufficient_training_variation'
)

EVALUATION_INSUFFICIENT_CLASSES = (
    'insufficient_classes'
)


# ==========================================================
# INPUT VALIDATION
# ==========================================================

def _validate_training_result(
    training_result,
):
    """
    Validate the unified training result produced by
    train_target_model().
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
        'target_name',
        'target_task',
        'target_type',
        'model_type',
        'algorithm',
        'feature_names',
        'training_rows',
        'test_rows',
        'X_test',
        'y_test',
    ]

    missing_keys = [
        key
        for key in required_keys
        if key not in training_result
    ]

    if missing_keys:

        raise ValueError(
            'Training result is missing required fields: '
            f'{missing_keys}'
        )


# ==========================================================
# TARGET VARIATION
# ==========================================================

def _get_unique_values(
    values,
):
    """
    Return sorted unique target values when possible.

    Falls back to insertion order when values cannot be
    sorted directly.
    """

    unique_values = list(
        set(values)
    )

    try:

        return sorted(
            unique_values
        )

    except TypeError:

        return unique_values


# ==========================================================
# REGRESSION EVALUATION
# ==========================================================

def _evaluate_regression(
    training_result,
):
    """
    Evaluate a regression model.

    Uses the already prepared test dataset contained in
    training_result.

    No additional training is performed here.
    """

    model = training_result[
        'model'
    ]

    X_test = training_result[
        'X_test'
    ]

    y_true = training_result[
        'y_test'
    ]

    if not X_test:

        raise ValueError(
            'No test features are available for regression '
            'evaluation.'
        )

    if not y_true:

        raise ValueError(
            'No test targets are available for regression '
            'evaluation.'
        )

    if len(X_test) != len(y_true):

        raise ValueError(
            'Test features and targets have different lengths.'
        )

    # ------------------------------------------------------
    # Training target analysis
    # ------------------------------------------------------

    y_train = training_result.get(
        'y_train',
        []
    )

    training_target_values = [
        float(value)
        for value in y_train
    ]

    unique_training_targets = (
        _get_unique_values(
            training_target_values
        )
    )

    training_target_unique_count = len(
        unique_training_targets
    )

    training_target_has_variation = (
        training_target_unique_count > 1
    )

    # ------------------------------------------------------
    # Predictions
    # ------------------------------------------------------

    y_pred_raw = model.predict(
        X_test
    )

    y_pred = [
        float(value)
        for value in y_pred_raw
    ]

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    metrics = calculate_metrics(
        y_true,
        y_pred,
    )

    # ------------------------------------------------------
    # Evaluation status
    # ------------------------------------------------------

    if not training_target_has_variation:

        evaluation_status = (
            EVALUATION_INSUFFICIENT_TRAINING_VARIATION
        )

        # R² is not considered a meaningful model-quality
        # indicator when the training target is constant.
        metrics['r_squared'] = None

    else:

        evaluation_status = (
            EVALUATION_VALID
        )

    # ------------------------------------------------------
    # Dates
    # ------------------------------------------------------

    test_data = training_result.get(
        'test_data',
        []
    )

    testing_dates = [
        row.get('Date')
        for row in test_data
        if 'Date' in row
    ]

    training_data = training_result.get(
        'training_data',
        []
    )

    training_dates = [
        row.get('Date')
        for row in training_data
        if 'Date' in row
    ]

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    return {

        'metrics':
            metrics,

        'evaluation_status':
            evaluation_status,

        'evaluation_valid':
            evaluation_status == EVALUATION_VALID,

        'target_name':
            training_result[
                'target_name'
            ],

        'target_task':
            training_result[
                'target_task'
            ],

        'target_type':
            training_result[
                'target_type'
            ],

        'model_type':
            training_result[
                'model_type'
            ],

        'algorithm':
            training_result[
                'algorithm'
            ],

        'training_target_values':
            training_target_values,

        'training_target_unique_values':
            unique_training_targets,

        'training_target_unique_count':
            training_target_unique_count,

        'training_target_has_variation':
            training_target_has_variation,

        'training_rows':
            training_result[
                'training_rows'
            ],

        'testing_rows':
            training_result[
                'test_rows'
            ],

        'feature_names':
            training_result[
                'feature_names'
            ],

        'training_dates':
            training_dates,

        'testing_dates':
            testing_dates,

        'actual_values':
            [
                float(value)
                for value in y_true
            ],

        'predicted_values':
            y_pred,
    }


# ==========================================================
# CLASSIFICATION EVALUATION
# ==========================================================

def _evaluate_classification(
    training_result,
):
    """
    Evaluate a binary or multiclass classification model.

    The model must already be trained.

    Evaluation is performed only against the unseen test
    dataset contained in training_result.
    """

    model = training_result[
        'model'
    ]

    X_test = training_result[
        'X_test'
    ]

    y_true = training_result[
        'y_test'
    ]

    if not X_test:

        raise ValueError(
            'No test features are available for '
            'classification evaluation.'
        )

    if not y_true:

        raise ValueError(
            'No test targets are available for '
            'classification evaluation.'
        )

    if len(X_test) != len(y_true):

        raise ValueError(
            'Test features and targets have different lengths.'
        )

    # ------------------------------------------------------
    # Training target analysis
    # ------------------------------------------------------

    y_train = training_result.get(
        'y_train',
        []
    )

    training_classes = (
        _get_unique_values(
            y_train
        )
    )

    training_class_count = len(
        training_classes
    )

    # ------------------------------------------------------
    # Classification requires at least two training classes
    # ------------------------------------------------------

    if training_class_count < 2:

        return {

            'metrics': None,

            'evaluation_status':
                EVALUATION_INSUFFICIENT_CLASSES,

            'evaluation_valid':
                False,

            'target_name':
                training_result[
                    'target_name'
                ],

            'target_task':
                training_result[
                    'target_task'
                ],

            'target_type':
                training_result[
                    'target_type'
                ],

            'model_type':
                training_result[
                    'model_type'
                ],

            'algorithm':
                training_result[
                    'algorithm'
                ],

            'training_classes':
                training_classes,

            'training_class_count':
                training_class_count,

            'training_rows':
                training_result[
                    'training_rows'
                ],

            'testing_rows':
                training_result[
                    'test_rows'
                ],

            'feature_names':
                training_result[
                    'feature_names'
                ],

            'actual_values':
                list(y_true),

            'predicted_values':
                [],

            'training_dates':
                [
                    row.get('Date')
                    for row in training_result.get(
                        'training_data',
                        []
                    )
                    if 'Date' in row
                ],

            'testing_dates':
                [
                    row.get('Date')
                    for row in training_result.get(
                        'test_data',
                        []
                    )
                    if 'Date' in row
                ],
        }

    # ------------------------------------------------------
    # Determine averaging strategy
    # ------------------------------------------------------

    class_count = training_result.get(
        'class_count'
    )

    if class_count == 2:

        average = 'binary'

    else:

        average = 'weighted'

    # ------------------------------------------------------
    # Predictions
    # ------------------------------------------------------

    y_pred = model.predict(
        X_test
    )

    y_pred = list(
        y_pred
    )

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    metrics = calculate_classification_metrics(
        y_true,
        y_pred,
        average=average,
    )

    # ------------------------------------------------------
    # Dates
    # ------------------------------------------------------

    training_data = training_result.get(
        'training_data',
        []
    )

    test_data = training_result.get(
        'test_data',
        []
    )

    training_dates = [
        row.get('Date')
        for row in training_data
        if 'Date' in row
    ]

    testing_dates = [
        row.get('Date')
        for row in test_data
        if 'Date' in row
    ]

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    return {

        'metrics':
            metrics,

        'evaluation_status':
            EVALUATION_VALID,

        'evaluation_valid':
            True,

        'target_name':
            training_result[
                'target_name'
            ],

        'target_task':
            training_result[
                'target_task'
            ],

        'target_type':
            training_result[
                'target_type'
            ],

        'model_type':
            training_result[
                'model_type'
            ],

        'algorithm':
            training_result[
                'algorithm'
            ],

        'training_classes':
            training_classes,

        'training_class_count':
            training_class_count,

        'classes':
            training_result.get(
                'classes'
            ),

        'class_count':
            class_count,

        'average':
            average,

        'training_rows':
            training_result[
                'training_rows'
            ],

        'testing_rows':
            training_result[
                'test_rows'
            ],

        'feature_names':
            training_result[
                'feature_names'
            ],

        'training_dates':
            training_dates,

        'testing_dates':
            testing_dates,

        'actual_values':
            list(y_true),

        'predicted_values':
            y_pred,
    }


# ==========================================================
# PUBLIC MODEL EVALUATION
# ==========================================================

def evaluate_model(
    training_result=None,
    test_ratio=None,
    min_test_rows=None,
):
    """
    Evaluate an already-trained target model.

    Architecture:

        train_target_model()
                ↓
        training_result
                ↓
        evaluate_model()
                ↓
        model_type
          │
          ├── regression
          │       ↓
          │   Regression Metrics
          │
          ├── classification
          │       ↓
          │   Classification Metrics
          │
          └── multiclass
                  ↓
              Classification Metrics

    Important:

        This function does NOT:

            - rebuild the dataset
            - retrain the model
            - shuffle data
            - select a target
            - select a model
            - create a new train/test split

        The training pipeline is responsible for preparing
        the chronological train/test datasets.

    Optional parameters:

        test_ratio:
            Expected test ratio used by the training pipeline.

            This parameter is accepted for pipeline
            compatibility and validation. It does not cause
            evaluate_model() to rebuild the split.

        min_test_rows:
            Minimum number of test observations required for
            evaluation.

            This is also validation only.
    """

    # ------------------------------------------------------
    # Validate training result
    # ------------------------------------------------------

    _validate_training_result(
        training_result
    )

    # ------------------------------------------------------
    # Validate optional test_ratio
    # ------------------------------------------------------

    if test_ratio is not None:

        try:

            test_ratio = float(
                test_ratio
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                'test_ratio must be numeric.'
            )

        if not (
            0.0 < test_ratio < 1.0
        ):

            raise ValueError(
                'test_ratio must be between 0 and 1.'
            )

    # ------------------------------------------------------
    # Validate optional minimum test rows
    # ------------------------------------------------------

    if min_test_rows is not None:

        if isinstance(
            min_test_rows,
            bool,
        ):

            raise ValueError(
                'min_test_rows must be an integer.'
            )

        try:

            min_test_rows = int(
                min_test_rows
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                'min_test_rows must be an integer.'
            )

        if min_test_rows <= 0:

            raise ValueError(
                'min_test_rows must be greater than zero.'
            )

        actual_test_rows = len(
            training_result.get(
                'X_test',
                []
            )
        )

        if actual_test_rows < min_test_rows:

            raise ValueError(
                'Test dataset contains fewer rows than '
                'min_test_rows: '
                f'{actual_test_rows} < {min_test_rows}'
            )

    # ------------------------------------------------------
    # Model type
    # ------------------------------------------------------

    model_type = training_result[
        'model_type'
    ]

    # ------------------------------------------------------
    # Regression
    # ------------------------------------------------------

    if model_type == 'regression':

        result = _evaluate_regression(
            training_result
        )

    # ------------------------------------------------------
    # Binary Classification
    # ------------------------------------------------------

    elif model_type == 'classification':

        result = _evaluate_classification(
            training_result
        )

    # ------------------------------------------------------
    # Multiclass Classification
    # ------------------------------------------------------

    elif model_type == 'multiclass':

        result = _evaluate_classification(
            training_result
        )

    # ------------------------------------------------------
    # Unsupported model type
    # ------------------------------------------------------

    else:

        raise ValueError(
            'Unsupported model type for evaluation: '
            f'{model_type}'
        )

    # ------------------------------------------------------
    # Evaluation configuration metadata
    # ------------------------------------------------------

    result['test_ratio'] = test_ratio

    result['min_test_rows'] = min_test_rows

    result['actual_test_rows'] = len(
        training_result.get(
            'X_test',
            []
        )
    )

    # ------------------------------------------------------
    # Chronological evaluation metadata
    # ------------------------------------------------------

    training_dates = result.get(
        'training_dates',
        []
    )

    testing_dates = result.get(
        'testing_dates',
        []
    )

    result['chronological_evaluation'] = True

    if (
        training_dates
        and testing_dates
    ):

        try:

            result['chronological_boundary_valid'] = (
                max(training_dates)
                < min(testing_dates)
            )

        except (
            TypeError,
            ValueError,
        ):

            # If dates cannot be compared safely,
            # do not make a false claim.
            result[
                'chronological_boundary_valid'
            ] = None

    else:

        result[
            'chronological_boundary_valid'
        ] = None

    return result
