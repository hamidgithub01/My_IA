import json
import math
import numpy as np

from database.connection import get_connection
from sklearn.linear_model import LinearRegression
from ml.models.forecasting import (
    create_forecasting_model,
)

from ml.training import registry


# ==========================================================
# JSON HELPERS
# ==========================================================

def _load_json(
    value,
    field_name,
):
    """
    Decode JSON stored inside model_history.

    Returns:
        Python representation of the stored JSON value.
    """

    if value is None:
        return None

    if isinstance(
        value,
        (dict, list),
    ):
        return value

    try:

        return json.loads(
            value
        )

    except (
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:

        raise ValueError(
            f'Invalid JSON stored in field: '
            f'{field_name}'
        ) from exc


# ==========================================================
# NUMERIC VALIDATION
# ==========================================================

def _validate_finite_number(
    value,
    field_name,
):
    """
    Validate that a value is a finite numeric value.
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
# DATABASE RECORD
# ==========================================================

def _get_model_history_record(
    model_history_id,
):
    """
    Retrieve one model_history record by ID.
    """

    if isinstance(
        model_history_id,
        bool,
    ):

        raise ValueError(
            'model_history_id must be an integer.'
        )

    try:

        model_history_id = int(
            model_history_id
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            'model_history_id must be an integer.'
        ) from exc

    if model_history_id <= 0:

        raise ValueError(
            'model_history_id must be greater than zero.'
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
            WHERE id = %s
            LIMIT 1
            """,
            (
                model_history_id,
            ),
        )

        record = cursor.fetchone()

        if record is None:

            raise ValueError(
                'Model history record not found: '
                f'{model_history_id}'
            )

        return record

    finally:

        cursor.close()
        connection.close()


# ==========================================================
# RECORD VALIDATION
# ==========================================================

def _validate_model_history_record(
    record,
):
    """
    Validate the structural integrity of a model_history
    record before attempting to rebuild the model.
    """

    if record is None:

        raise ValueError(
            'Model history record is required.'
        )

    required_fields = [
        'id',
        'algorithm',
        'model_type',
        'target_name',
        'target_task',
        'target_type',
        'training_rows',
        'feature_names',
        'coefficients',
        'intercept',
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in record
    ]

    if missing_fields:

        raise ValueError(
            'Model history record is missing required '
            f'fields: {missing_fields}'
        )

    if not record.get(
        'target_name'
    ):

        raise ValueError(
            'Model history record contains no target name.'
        )

    if not record.get(
        'model_type'
    ):

        raise ValueError(
            'Model history record contains no model type.'
        )

    if not record.get(
        'target_task'
    ):

        raise ValueError(
            'Model history record contains no target task.'
        )

    if not record.get(
        'target_type'
    ):

        raise ValueError(
            'Model history record contains no target type.'
        )

    training_rows = record.get(
        'training_rows'
    )

    if training_rows is None:

        raise ValueError(
            'Model history record contains no training row count.'
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
            'Stored training_rows is invalid.'
        ) from exc

    if training_rows < 0:

        raise ValueError(
            'Stored training_rows cannot be negative.'
        )

    return True


# ==========================================================
# FEATURE RESTORATION
# ==========================================================

def _restore_feature_names(
    record,
):
    """
    Restore and validate the feature schema.
    """

    feature_names = _load_json(
        record.get(
            'feature_names'
        ),
        'feature_names',
    )

    if not isinstance(
        feature_names,
        list,
    ):

        raise ValueError(
            'Stored feature_names must be a JSON list.'
        )

    if not feature_names:

        raise ValueError(
            'Stored feature_names are empty.'
        )

    for index, name in enumerate(
        feature_names
    ):

        if not isinstance(
            name,
            str,
        ):

            raise ValueError(
                'Stored feature name must be a string.\n'
                f'Index: {index}\n'
                f'Value: {name!r}'
            )

        if not name:

            raise ValueError(
                'Stored feature name cannot be empty.\n'
                f'Index: {index}'
            )

    return feature_names


# ==========================================================
# COEFFICIENT RESTORATION
# ==========================================================

def _restore_coefficients(
    record,
):
    """
    Restore model coefficients.

    Regression:

        [c1, c2, c3]

    Classification / multiclass:

        [
            [c1, c2, c3],
            [c4, c5, c6],
        ]
    """

    coefficients = _load_json(
        record.get(
            'coefficients'
        ),
        'coefficients',
    )

    if not isinstance(
        coefficients,
        list,
    ):

        raise ValueError(
            'Stored coefficients must be a JSON list.'
        )

    if not coefficients:

        raise ValueError(
            'Stored coefficients are empty.'
        )

    return coefficients


# ==========================================================
# INTERCEPT RESTORATION
# ==========================================================

def _restore_intercept(
    record,
):
    """
    Restore the model intercept.
    """

    intercept = record.get(
        'intercept'
    )

    if intercept is None:

        raise ValueError(
            'Stored model contains no intercept.'
        )

    return intercept


# ==========================================================
# CLASSES RESTORATION
# ==========================================================

def _restore_classes(
    record,
):
    """
    Restore classification classes.

    Regression models do not require classes.
    """

    raw_classes = record.get(
        'classes'
    )

    if raw_classes is None:

        return None

    classes = _load_json(
        raw_classes,
        'classes',
    )

    if not isinstance(
        classes,
        list,
    ):

        raise ValueError(
            'Stored classes must be a JSON list.'
        )

    if not classes:

        raise ValueError(
            'Stored classes are empty.'
        )

    return classes


# ==========================================================
# MODEL TYPE VALIDATION
# ==========================================================

def _validate_model_configuration(
    record,
):
    """
    Validate consistency between target type, task and
    model family.
    """

    target_task = record[
        'target_task'
    ]

    target_type = record[
        'target_type'
    ]

    model_type = record[
        'model_type'
    ]

    # ------------------------------------------------------
    # Regression
    # ------------------------------------------------------

    if target_task == 'regression':

        if target_type != 'numeric':

            raise ValueError(
                'Invalid model history configuration: '
                'regression target must have numeric target_type.'
            )

        if model_type != 'regression':

            raise ValueError(
                'Invalid model history configuration: '
                'regression target must use regression model_type.'
            )

        return True

    # ------------------------------------------------------
    # Binary Classification
    # ------------------------------------------------------

    if target_task == 'classification':

        if target_type != 'categorical':

            raise ValueError(
                'Invalid model history configuration: '
                'classification target must have categorical '
                'target_type.'
            )

        if model_type != 'classification':

            raise ValueError(
                'Invalid model history configuration: '
                'binary classification must use classification '
                'model_type.'
            )

        return True

    # ------------------------------------------------------
    # Multiclass
    # ------------------------------------------------------

    if target_task == 'categorical':

        if target_type != 'categorical':

            raise ValueError(
                'Invalid model history configuration: '
                'categorical target must have categorical '
                'target_type.'
            )

        if model_type != 'multiclass':

            raise ValueError(
                'Invalid model history configuration: '
                'categorical target must use multiclass model_type.'
            )

        return True

    raise ValueError(
        'Unsupported stored target task: '
        f'{target_task}'
    )


# ==========================================================
# MODEL CREATION
# ==========================================================

def _create_model_from_record(
    record,
):
    """
    Create the correct empty sklearn model from the stored
    model configuration.
    """

    target_type = record[
        'target_type'
    ]

    class_count = record.get(
        'class_count'
    )

    if target_type == 'categorical':

        if class_count is None:

            raise ValueError(
                'Categorical model history contains no class_count.'
            )

        try:

            class_count = int(
                class_count
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                'Stored class_count is invalid.'
            ) from exc

        if class_count < 2:

            raise ValueError(
                'Stored categorical model must contain at '
                'least two classes.'
            )

    model = create_forecasting_model(
        target_type=target_type,
        class_count=class_count,
    )

    if model is None:

        raise ValueError(
            'Unable to create model from stored model configuration.'
        )

    return model


# ==========================================================
# PARAMETER RESTORATION
# ==========================================================

def _restore_model_parameters(
    model,
    record,
    feature_names,
    coefficients,
    intercept,
    classes,
):
    """
    Restore the learned parameters directly into a newly
    created sklearn model.

    No training is performed.

    Parameters are restored as NumPy arrays because
    scikit-learn expects learned model attributes such as
    coef_, intercept_ and classes_ to use NumPy-compatible
    structures.
    """

    model_type = record[
        'model_type'
    ]

    feature_count = len(
        feature_names
    )

    # ------------------------------------------------------
    # Regression
    # ------------------------------------------------------

    if model_type == 'regression':

        if len(
            coefficients
        ) != feature_count:

            raise ValueError(
                'Stored regression coefficient count does not '
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

        restored_intercept = (
            _validate_finite_number(
                intercept,
                'intercept',
            )
        )

        # --------------------------------------------------
        # scikit-learn expects NumPy-compatible parameters
        # --------------------------------------------------

        model.coef_ = np.asarray(
            restored_coefficients,
            dtype=float,
        )

        model.intercept_ = float(
            restored_intercept
        )

        return model

    # ------------------------------------------------------
    # Classification / Multiclass
    # ------------------------------------------------------

    if model_type in (
        'classification',
        'multiclass',
    ):

        if classes is None:

            raise ValueError(
                'Classification model contains no stored classes.'
            )

        if not isinstance(
            coefficients,
            list,
        ):

            raise ValueError(
                'Classification coefficients must be a list.'
            )

        if not coefficients:

            raise ValueError(
                'Classification coefficients are empty.'
            )

        restored_coefficients = []

        for row_index, row in enumerate(
            coefficients
        ):

            if not isinstance(
                row,
                list,
            ):

                raise ValueError(
                    'Classification coefficients must be a '
                    'two-dimensional list.'
                )

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

        # --------------------------------------------------
        # Classification intercept
        # --------------------------------------------------

        if not isinstance(
            intercept,
            list,
        ):

            raise ValueError(
                'Classification intercept must be a JSON list.'
            )

        if len(intercept) != len(
            restored_coefficients
        ):

            raise ValueError(
                'Classification intercept count does not '
                'match coefficient rows.'
            )

        restored_intercept = [
            _validate_finite_number(
                value,
                f'intercept[{index}]',
            )
            for index, value in enumerate(
                intercept
            )
        ]

        # --------------------------------------------------
        # Validate classes
        # --------------------------------------------------

        if not isinstance(
            classes,
            list,
        ):

            raise ValueError(
                'Stored classes must be a list.'
            )

        if not classes:

            raise ValueError(
                'Stored classes are empty.'
            )

        # --------------------------------------------------
        # scikit-learn parameters
        # --------------------------------------------------

        model.coef_ = np.asarray(
            restored_coefficients,
            dtype=float,
        )

        model.intercept_ = np.asarray(
            restored_intercept,
            dtype=float,
        )

        model.classes_ = np.asarray(
            classes
        )

        return model

    raise ValueError(
        'Unsupported model type: '
        f'{model_type}'
    )


# ==========================================================
# PUBLIC LOAD FUNCTION
# ==========================================================

def load_model_history(
    model_history_id,
):
    """
    Load and reconstruct a trained model from model_history.

    This function does NOT:

        - train the model
        - rebuild the dataset
        - create a train/test split
        - evaluate the model
        - select the best model

    It only restores the stored model state.
    """

    record = _get_model_history_record(
        model_history_id
    )

    _validate_model_history_record(
        record
    )

    _validate_model_configuration(
        record
    )

    feature_names = _restore_feature_names(
        record
    )

    coefficients = _restore_coefficients(
        record
    )

    intercept = _restore_intercept(
        record
    )

    classes = _restore_classes(
        record
    )

    model = _create_model_from_record(
        record
    )

    model = _restore_model_parameters(
        model,
        record,
        feature_names,
        coefficients,
        intercept,
        classes,
    )

    evaluation_metrics = _load_json(
        record.get(
            'evaluation_metrics'
        ),
        'evaluation_metrics',
    )

    return {

        # --------------------------------------------------
        # Model
        # --------------------------------------------------

        'model':
            model,

        # --------------------------------------------------
        # Registry identity
        # --------------------------------------------------

        'model_history_id':
            record['id'],

        'trained_at':
            record.get(
                'trained_at'
            ),

        # --------------------------------------------------
        # Model information
        # --------------------------------------------------

        'algorithm':
            record['algorithm'],

        'model_type':
            record['model_type'],

        # --------------------------------------------------
        # Target information
        # --------------------------------------------------

        'target_name':
            record['target_name'],

        'target_task':
            record['target_task'],

        'target_type':
            record['target_type'],

        'class_count':
            record.get(
                'class_count'
            ),

        'classes':
            classes,

        # --------------------------------------------------
        # Feature information
        # --------------------------------------------------

        'feature_names':
            feature_names,

        # --------------------------------------------------
        # Training information
        # --------------------------------------------------

        'training_rows':
            record.get(
                'training_rows'
            ),

        # --------------------------------------------------
        # Evaluation information
        # --------------------------------------------------

        'mae':
            record.get(
                'mae'
            ),

        'rmse':
            record.get(
                'rmse'
            ),

        'r_squared':
            record.get(
                'r_squared'
            ),

        'evaluation_status':
            record.get(
                'evaluation_status'
            ),

        'evaluation_metrics':
            evaluation_metrics,

        # --------------------------------------------------
        # Registry state
        # --------------------------------------------------

        'reused_previous_state':
            bool(
                record.get(
                    'reused_previous_state'
                )
            ),
    }

# ==========================================================
# BACKWARD-COMPATIBLE MODEL LOADING API
# ==========================================================

def load_model_from_history(
    history,
):
    """
    Reconstruct a trained model directly from a model-history
    dictionary.

    This is the backward-compatible API used by the persistence
    tests.

    It does not access the database.
    It does not train the model.
    It does not evaluate the model.

    The newer database-backed API remains:

        load_model_history(model_history_id)
    """

    if history is None:

        raise ValueError(
            'Model history is required.'
        )

    if not isinstance(
        history,
        dict,
    ):

        raise ValueError(
            'Model history must be a dictionary.'
        )

    required_fields = [
        'algorithm',
        'model_type',
        'feature_names',
        'coefficients',
        'intercept',
        'target_name',
        'training_rows',
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in history
    ]

    if missing_fields:

        raise ValueError(
            'Model history is missing required fields: '
            f'{missing_fields}'
        )

    algorithm = history.get(
        'algorithm'
    )

    if algorithm != 'LinearRegression':

        raise ValueError(
            'Unsupported model algorithm: '
            f'{algorithm}'
        )

    model_type = history.get(
        'model_type'
    )

    if model_type != 'regression':

        raise ValueError(
            'Unsupported model type for '
            'LinearRegression: '
            f'{model_type}'
        )

    feature_names = history.get(
        'feature_names'
    )

    if not isinstance(
        feature_names,
        list,
    ):

        raise ValueError(
            'Stored feature_names must be a list.'
        )

    if not feature_names:

        raise ValueError(
            'Stored feature_names cannot be empty.'
        )

    for index, name in enumerate(
        feature_names
    ):

        if not isinstance(
            name,
            str,
        ):

            raise ValueError(
                'Stored feature name must be a string. '
                f'Index: {index}'
            )

        if not name.strip():

            raise ValueError(
                'Stored feature name cannot be empty. '
                f'Index: {index}'
            )

    coefficients = history.get(
        'coefficients'
    )

    if not isinstance(
        coefficients,
        list,
    ):

        raise ValueError(
            'Stored coefficients must be a list.'
        )

    if not coefficients:

        raise ValueError(
            'Stored coefficients cannot be empty.'
        )

    if len(
        coefficients
    ) != len(
        feature_names
    ):

        raise ValueError(
            'Stored coefficient count does not match '
            'feature count.'
        )

    restored_coefficients = []

    for index, value in enumerate(
        coefficients
    ):

        restored_coefficients.append(
            _validate_finite_number(
                value,
                f'coefficients[{index}]',
            )
        )

    intercept = history.get(
        'intercept'
    )

    if intercept is None:

        raise ValueError(
            'Stored intercept is required.'
        )

    restored_intercept = (
        _validate_finite_number(
            intercept,
            'intercept',
        )
    )

    training_rows = history.get(
        'training_rows'
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
            'Stored training_rows is invalid.'
        ) from exc

    if training_rows < 0:

        raise ValueError(
            'Stored training_rows cannot be negative.'
        )

    target_name = history.get(
        'target_name'
    )

    if not target_name:

        raise ValueError(
            'Stored target_name is required.'
        )

    model = LinearRegression()

    model.coef_ = np.asarray(
        restored_coefficients,
        dtype=float,
    )

    model.intercept_ = float(
        restored_intercept
    )

    return {

        # --------------------------------------------------
        # Model
        # --------------------------------------------------

        'model':
            model,

        # --------------------------------------------------
        # Registry identity
        # --------------------------------------------------

        'model_history_id':
            history.get(
                'id'
            ),

        'trained_at':
            history.get(
                'trained_at'
            ),

        # --------------------------------------------------
        # Model information
        # --------------------------------------------------

        'algorithm':
            algorithm,

        'model_type':
            model_type,

        # --------------------------------------------------
        # Target information
        # --------------------------------------------------

        'target_name':
            target_name,

        'target_task':
            history.get(
                'target_task'
            ),

        'target_type':
            history.get(
                'target_type'
            ),

        'class_count':
            history.get(
                'class_count'
            ),

        'classes':
            history.get(
                'classes'
            ),

        # --------------------------------------------------
        # Feature information
        # --------------------------------------------------

        'feature_names':
            list(
                feature_names
            ),

        # --------------------------------------------------
        # Training information
        # --------------------------------------------------

        'training_rows':
            training_rows,

        # --------------------------------------------------
        # Feature statistics
        # --------------------------------------------------

        'feature_means':
            history.get(
                'feature_means',
                {},
            ),

        'feature_scales':
            history.get(
                'feature_scales',
                {},
            ),

        # --------------------------------------------------
        # Evaluation information
        # --------------------------------------------------

        'mae':
            history.get(
                'mae'
            ),

        'rmse':
            history.get(
                'rmse'
            ),

        'r_squared':
            history.get(
                'r_squared'
            ),

        'evaluation_status':
            history.get(
                'evaluation_status'
            ),

        'evaluation_metrics':
            history.get(
                'evaluation_metrics'
            ),

        # --------------------------------------------------
        # Registry state
        # --------------------------------------------------

        'reused_previous_state':
            bool(
                history.get(
                    'reused_previous_state',
                    False,
                )
            ),
    }


# ==========================================================
# REGISTRY COMPATIBILITY HELPERS
# ==========================================================

def get_latest_model_history():
    """
    Return the latest model history record from the registry.

    This wrapper intentionally resolves the registry function
    at call time so tests and other callers can patch the
    registry implementation safely.
    """

    return registry.get_latest_model_history()


def get_model_history_by_id(
    model_history_id,
):
    """
    Return a model history record by ID from the registry.

    This wrapper intentionally resolves the registry function
    at call time so tests and other callers can patch the
    registry implementation safely.
    """

    return registry.get_model_history_by_id(
        model_history_id
    )


# ==========================================================
# BACKWARD-COMPATIBLE MODEL LOADING API
# ==========================================================

def load_latest_model():
    """
    Load the latest model from the model registry.

    Backward-compatible API.
    """

    history = get_latest_model_history()

    if history is None:

        return None

    return load_model_from_history(
        history
    )


def load_model_by_id(
    model_history_id,
):
    """
    Load a model by its model_history ID.

    Backward-compatible API.
    """

    history = get_model_history_by_id(
        model_history_id
    )

    if history is None:

        return None

    return load_model_from_history(
        history
    )

# ==========================================================
# SIMPLE TEST
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )
    print(
        '             MODEL LOAD TEST'
    )
    print(
        '=================================================='
    )

    model_history_id = 29

    print()
    print(
        'Loading model history ID:',
        model_history_id,
    )

    result = load_model_history(
        model_history_id
    )

    model = result[
        'model'
    ]

    print()
    print(
        '========== LOADED MODEL =========='
    )

    print(
        'Model history ID:',
        result[
            'model_history_id'
        ]
    )

    print(
        'Algorithm:',
        result[
            'algorithm'
        ]
    )

    print(
        'Model type:',
        result[
            'model_type'
        ]
    )

    print(
        'Target:',
        result[
            'target_name'
        ]
    )

    print(
        'Target task:',
        result[
            'target_task'
        ]
    )

    print(
        'Target type:',
        result[
            'target_type'
        ]
    )

    print(
        'Training rows:',
        result[
            'training_rows'
        ]
    )

    print(
        'Feature count:',
        len(
            result[
                'feature_names'
            ]
        )
    )

    print(
        'Algorithm restored:',
        model.__class__.__name__
    )

    print()
    print(
        '=================================================='
    )
    print(
        '             MODEL LOAD TEST PASSED'
    )
    print(
        '=================================================='
    )