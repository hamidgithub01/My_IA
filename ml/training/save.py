import json
import math
from datetime import datetime

from database.connection import get_connection


# ==========================================================
# JSON HELPERS
# ==========================================================

def _dump_json(
    value,
    field_name,
):
    """
    Convert a Python value into JSON suitable for storage.
    """

    try:

        return json.dumps(
            value,
            ensure_ascii=False,
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            f'Unable to serialize {field_name} to JSON.'
        ) from exc


# ==========================================================
# FINITE NUMBER
# ==========================================================

def _validate_finite_number(
    value,
    field_name,
):
    """
    Validate and convert a numeric value to float.
    """

    if isinstance(
        value,
        bool,
    ):

        raise ValueError(
            f'{field_name} must be numeric.'
        )

    try:

        number = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            f'{field_name} must be numeric.'
        ) from exc

    if not math.isfinite(
        number
    ):

        raise ValueError(
            f'{field_name} contains a non-finite value.'
        )

    return number


# ==========================================================
# TRAINING RESULT VALIDATION
# ==========================================================

def _validate_training_result(
    training_result,
):
    """
    Validate the unified result produced by the training
    pipeline.
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

    required_fields = [
        'model',
        'target_name',
        'target_task',
        'target_type',
        'model_type',
        'algorithm',
        'feature_names',
        'training_rows',
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in training_result
    ]

    if missing_fields:

        raise ValueError(
            'Training result is missing required fields: '
            f'{missing_fields}'
        )

    if training_result[
        'model'
    ] is None:

        raise ValueError(
            'Training result contains no model.'
        )

    if not training_result[
        'target_name'
    ]:

        raise ValueError(
            'Training result contains no target name.'
        )

    if not training_result[
        'target_task'
    ]:

        raise ValueError(
            'Training result contains no target task.'
        )

    if not training_result[
        'target_type'
    ]:

        raise ValueError(
            'Training result contains no target type.'
        )

    if not training_result[
        'model_type'
    ]:

        raise ValueError(
            'Training result contains no model type.'
        )

    if not training_result[
        'algorithm'
    ]:

        raise ValueError(
            'Training result contains no algorithm.'
        )

    feature_names = training_result[
        'feature_names'
    ]

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

    training_rows = training_result[
        'training_rows'
    ]

    if isinstance(
        training_rows,
        bool,
    ):

        raise ValueError(
            'training_rows must be an integer.'
        )

    try:

        training_rows = int(
            training_rows
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            'training_rows must be an integer.'
        ) from exc

    if training_rows < 0:

        raise ValueError(
            'training_rows cannot be negative.'
        )

    return True


# ==========================================================
# MODEL STRUCTURE
# ==========================================================

def _extract_model_parameters(
    training_result,
):
    """
    Extract sklearn learned parameters from the trained model.
    """

    model = training_result[
        'model'
    ]

    model_type = training_result[
        'model_type'
    ]

    feature_names = training_result[
        'feature_names'
    ]

    feature_count = len(
        feature_names
    )

    # ------------------------------------------------------
    # Coefficients
    # ------------------------------------------------------

    if not hasattr(
        model,
        'coef_',
    ):

        raise ValueError(
            'Trained model contains no coef_ attribute.'
        )

    coefficients = model.coef_

    # ------------------------------------------------------
    # Regression
    # ------------------------------------------------------

    if model_type == 'regression':

        if len(coefficients) != feature_count:

            raise ValueError(
                'Regression coefficient count does not '
                'match feature count.'
            )

        restored_coefficients = [
            _validate_finite_number(
                value,
                f'coefficients[{index}]',
            )
            for index, value in enumerate(
                coefficients
            )
        ]

    # ------------------------------------------------------
    # Classification / Multiclass
    # ------------------------------------------------------

    elif model_type in (
        'classification',
        'multiclass',
    ):

        restored_coefficients = []

        for row_index, row in enumerate(
            coefficients
        ):

            if len(row) != feature_count:

                raise ValueError(
                    'Classification coefficient row does not '
                    'match feature count.\n'
                    f'Row: {row_index}\n'
                    f'Expected: {feature_count}\n'
                    f'Actual: {len(row)}'
                )

            restored_row = [
                _validate_finite_number(
                    value,
                    f'coefficients[{row_index}][{index}]',
                )
                for index, value in enumerate(
                    row
                )
            ]

            restored_coefficients.append(
                restored_row
            )

    else:

        raise ValueError(
            'Unsupported model type: '
            f'{model_type}'
        )

    # ------------------------------------------------------
    # Intercept
    # ------------------------------------------------------

    if not hasattr(
        model,
        'intercept_',
    ):

        raise ValueError(
            'Trained model contains no intercept_ attribute.'
        )

    raw_intercept = model.intercept_

    if model_type == 'regression':

        intercept = _validate_finite_number(
            raw_intercept,
            'intercept',
        )

    else:

        intercept = [
            _validate_finite_number(
                value,
                f'intercept[{index}]',
            )
            for index, value in enumerate(
                raw_intercept
            )
        ]

    # ------------------------------------------------------
    # Classes
    # ------------------------------------------------------

    classes = None
    class_count = None

    if model_type in (
        'classification',
        'multiclass',
    ):

        if not hasattr(
            model,
            'classes_',
        ):

            raise ValueError(
                'Classification model contains no classes_.'
            )

        classes = list(
            model.classes_
        )

        if not classes:

            raise ValueError(
                'Classification model contains no classes.'
            )

        class_count = len(
            classes
        )

        if class_count < 2:

            raise ValueError(
                'Classification model must contain at least '
                'two classes.'
            )

    return {
        'coefficients':
            restored_coefficients,

        'intercept':
            intercept,

        'classes':
            classes,

        'class_count':
            class_count,
    }


# ==========================================================
# PREPROCESSING INFORMATION
# ==========================================================

def _extract_preprocessing_statistics(
    training_result,
):
    """
    Extract preprocessing statistics.

    The current project does not standardize features, so
    empty dictionaries are stored.

    This keeps the schema ready for future preprocessing.
    """

    feature_means = training_result.get(
        'feature_means',
        {},
    )

    feature_scales = training_result.get(
        'feature_scales',
        {},
    )

    return (
        feature_means,
        feature_scales,
    )


# ==========================================================
# EVALUATION INFORMATION
# ==========================================================

def _extract_evaluation_information(
    evaluation_result,
):
    """
    Extract evaluation metrics and status.

    Invalid or non-finite numeric metrics are stored as None.
    """

    mae = None
    rmse = None
    r_squared = None

    evaluation_status = None
    evaluation_metrics = None

    if evaluation_result is None:

        return {
            'mae':
                None,

            'rmse':
                None,

            'r_squared':
                None,

            'evaluation_status':
                None,

            'evaluation_metrics':
                None,
        }

    evaluation_status = (
        evaluation_result.get(
            'evaluation_status'
        )
    )

    metrics = evaluation_result.get(
        'metrics'
    )

    if metrics is not None:

        if not isinstance(
            metrics,
            dict,
        ):

            raise ValueError(
                'evaluation_result["metrics"] must be a dictionary.'
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

        if mae is not None:

            try:

                mae = _validate_finite_number(
                    mae,
                    'mae',
                )

            except ValueError:

                mae = None

        if rmse is not None:

            try:

                rmse = _validate_finite_number(
                    rmse,
                    'rmse',
                )

            except ValueError:

                rmse = None

        if r_squared is not None:

            try:

                r_squared = _validate_finite_number(
                    r_squared,
                    'r_squared',
                )

            except ValueError:

                r_squared = None

        evaluation_metrics = metrics

    return {
        'mae':
            mae,

        'rmse':
            rmse,

        'r_squared':
            r_squared,

        'evaluation_status':
            evaluation_status,

        'evaluation_metrics':
            evaluation_metrics,
    }


# ==========================================================
# MODEL HISTORY SAVE
# ==========================================================

def save_model_history(
    training_result,
    evaluation_result=None,
    reused_previous_state=False,
):
    """
    Save a trained model and its evaluation information
    into model_history.

    Every training operation creates a new history record.

    Previous model history is never deleted.

    Supports:

        regression
        binary classification
        multiclass classification
    """

    # ------------------------------------------------------
    # Validate training result
    # ------------------------------------------------------

    _validate_training_result(
        training_result
    )

    # ------------------------------------------------------
    # Extract basic model information
    # ------------------------------------------------------

    algorithm = training_result[
        'algorithm'
    ]

    model_type = training_result[
        'model_type'
    ]

    target_name = training_result[
        'target_name'
    ]

    target_task = training_result[
        'target_task'
    ]

    target_type = training_result[
        'target_type'
    ]

    training_rows = int(
        training_result[
            'training_rows'
        ]
    )

    feature_names = training_result[
        'feature_names'
    ]

    # ------------------------------------------------------
    # Extract learned model parameters
    # ------------------------------------------------------

    model_parameters = _extract_model_parameters(
        training_result
    )

    coefficients = model_parameters[
        'coefficients'
    ]

    intercept = model_parameters[
        'intercept'
    ]

    classes = model_parameters[
        'classes'
    ]

    class_count = model_parameters[
        'class_count'
    ]

    # ------------------------------------------------------
    # Preprocessing
    # ------------------------------------------------------

    (
        feature_means,
        feature_scales,
    ) = _extract_preprocessing_statistics(
        training_result
    )

    # ------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------

    evaluation = _extract_evaluation_information(
        evaluation_result
    )

    mae = evaluation[
        'mae'
    ]

    rmse = evaluation[
        'rmse'
    ]

    r_squared = evaluation[
        'r_squared'
    ]

    evaluation_status = evaluation[
        'evaluation_status'
    ]

    evaluation_metrics = evaluation[
        'evaluation_metrics'
    ]

    # ------------------------------------------------------
    # JSON
    # ------------------------------------------------------

    feature_names_json = _dump_json(
        feature_names,
        'feature_names',
    )

    coefficients_json = _dump_json(
        coefficients,
        'coefficients',
    )

    classes_json = None

    if classes is not None:

        classes_json = _dump_json(
            classes,
            'classes',
        )

    feature_means_json = _dump_json(
        feature_means,
        'feature_means',
    )

    feature_scales_json = _dump_json(
        feature_scales,
        'feature_scales',
    )

    evaluation_metrics_json = None

    if evaluation_metrics is not None:

        evaluation_metrics_json = _dump_json(
            evaluation_metrics,
            'evaluation_metrics',
        )

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
                algorithm,
                model_type,
                target_name,
                target_task,
                target_type,
                class_count,
                training_rows,
                feature_names_json,
                coefficients_json,
                classes_json,
                (
                    _dump_json(
                        intercept,
                        'intercept',
                    )
                    if isinstance(
                        intercept,
                        list,
                    )
                    else intercept
                ),
                feature_means_json,
                feature_scales_json,
                mae,
                rmse,
                r_squared,
                evaluation_status,
                evaluation_metrics_json,
                bool(
                    reused_previous_state
                ),
            ),
        )

        connection.commit()

        return cursor.lastrowid

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()
        connection.close()


# ==========================================================
# SIMPLE TEST
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )
    print(
        '             MODEL SAVE MODULE'
    )
    print(
        '=================================================='
    )

    print()
    print(
        'save.py loaded successfully.'
    )

    print()
    print(
        'Supported model types:'
    )

    print(
        '- regression'
    )

    print(
        '- classification'
    )

    print(
        '- multiclass'
    )

    print()
    print(
        '=================================================='
    )
    print(
        '             MODEL SAVE MODULE PASSED'
    )
    print(
        '=================================================='
    )