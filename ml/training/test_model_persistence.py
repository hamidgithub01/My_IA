import json
from unittest.mock import MagicMock, patch

import numpy as np
from sklearn.linear_model import LinearRegression

from ml.training.save import (
    save_model_history,
)

from ml.training.load import (
    load_model_from_history,
    load_latest_model,
    load_model_by_id,
)

from ml.training.registry import (
    get_latest_model_history,
    get_model_history_by_id,
)


# ==========================================================
# SYNTHETIC MODEL
# ==========================================================

def create_synthetic_model():
    """
    Create a completely synthetic LinearRegression model.

    No project dataset or database is used.
    """

    X = np.array([
        [1.0, 10.0],
        [2.0, 20.0],
        [3.0, 30.0],
        [4.0, 40.0],
        [5.0, 50.0],
    ])

    y = np.array([
        15.0,
        30.0,
        45.0,
        60.0,
        75.0,
    ])

    model = LinearRegression()

    model.fit(
        X,
        y,
    )

    return model


def create_synthetic_training_result(
    evaluation_result=None,
):
    """
    Build a synthetic training-result structure.
    """

    model = create_synthetic_model()

    result = {
        'model':
            model,

        'feature_names':
            [
                'Feature_1',
                'Feature_2',
            ],

        'training_rows':
            5,

        'target_name':
            'Target_Expense_Total_1D',
    }

    if evaluation_result is not None:

        result['evaluation_result'] = (
            evaluation_result
        )

    return result


def create_synthetic_evaluation_result():
    """
    Synthetic evaluation result.
    """

    return {
        'metrics': {
            'mae': 1.25,
            'rmse': 2.50,
            'r_squared': 0.95,
        },

        'evaluation_status':
            'valid',

        'evaluation_valid':
            True,
    }


def create_synthetic_history(
    model_history_id=101,
):
    """
    Synthetic model_history database record.
    """

    model = create_synthetic_model()

    return {
        'id':
            model_history_id,

        'trained_at':
            None,

        'algorithm':
            'LinearRegression',

        'target_name':
            'Target_Expense_Total_1D',

        'training_rows':
            5,

        'feature_names':
            [
                'Feature_1',
                'Feature_2',
            ],

        'coefficients':
            [
                float(value)
                for value in model.coef_
            ],

        'intercept':
            float(
                model.intercept_
            ),

        'feature_means':
            {},

        'feature_scales':
            {},

        'mae':
            1.25,

        'rmse':
            2.50,

        'r_squared':
            0.95,

        'reused_previous_state':
            False,
    }


# ==========================================================
# MOCK DATABASE
# ==========================================================

def create_mock_connection(
    fetchone_result=None,
):
    """
    Create a mocked database connection.
    """

    connection = MagicMock()

    cursor = MagicMock()

    cursor.lastrowid = 101

    cursor.fetchone.return_value = (
        fetchone_result
    )

    connection.cursor.return_value = (
        cursor
    )

    return connection, cursor


# ==========================================================
# SAVE TEST
# ==========================================================

def test_save_model_history():
    print(
        '========== SAVE MODEL HISTORY TEST =========='
    )

    training_result = (
        create_synthetic_training_result()
    )

    connection, cursor = (
        create_mock_connection()
    )

    with patch(
        'ml.training.save.get_connection',
        return_value=connection,
    ):

        model_history_id = (
            save_model_history(
                training_result,
            )
        )

    if model_history_id != 101:

        raise AssertionError(
            'Model history ID was not returned correctly.'
        )

    if not cursor.execute.called:

        raise AssertionError(
            'INSERT query was not executed.'
        )

    if not connection.commit.called:

        raise AssertionError(
            'Database transaction was not committed.'
        )

    print(
        'Model save: PASSED'
    )

    print(
        f'Model history ID: {model_history_id}'
    )


# ==========================================================
# SAVE PARAMETERS TEST
# ==========================================================

def test_save_model_parameters():
    print()
    print(
        '========== SAVE MODEL PARAMETERS TEST =========='
    )

    training_result = (
        create_synthetic_training_result()
    )

    model = training_result[
        'model'
    ]

    connection, cursor = (
        create_mock_connection()
    )

    with patch(
        'ml.training.save.get_connection',
        return_value=connection,
    ):

        save_model_history(
            training_result,
        )

    query = cursor.execute.call_args

    if query is None:

        raise AssertionError(
            'Database execute call was not captured.'
        )

    parameters = query.args[1]

    # ------------------------------------------------------
    # Expected parameter positions
    # ------------------------------------------------------

    algorithm = parameters[1]

    target_name = parameters[2]

    training_rows = parameters[3]

    feature_names_json = parameters[4]

    coefficients_json = parameters[5]

    intercept = parameters[6]

    feature_means_json = parameters[7]

    feature_scales_json = parameters[8]

    if algorithm != 'LinearRegression':

        raise AssertionError(
            'Algorithm was not saved correctly.'
        )

    if target_name != (
        'Target_Expense_Total_1D'
    ):

        raise AssertionError(
            'Target name was not saved correctly.'
        )

    if training_rows != 5:

        raise AssertionError(
            'Training row count was not saved correctly.'
        )

    if json.loads(
        feature_names_json
    ) != training_result[
        'feature_names'
    ]:

        raise AssertionError(
            'Feature names were not serialized correctly.'
        )

    if json.loads(
        coefficients_json
    ) != [
        float(value)
        for value in model.coef_
    ]:

        raise AssertionError(
            'Coefficients were not serialized correctly.'
        )

    if abs(
        float(intercept)
        - float(model.intercept_)
    ) > 1e-10:

        raise AssertionError(
            'Intercept was not saved correctly.'
        )

    if json.loads(
        feature_means_json
    ) != {}:

        raise AssertionError(
            'Feature means were not saved correctly.'
        )

    if json.loads(
        feature_scales_json
    ) != {}:

        raise AssertionError(
            'Feature scales were not saved correctly.'
        )

    print(
        'Model parameters persistence: PASSED'
    )


# ==========================================================
# SAVE EVALUATION TEST
# ==========================================================

def test_save_evaluation_metrics():
    print()
    print(
        '========== SAVE EVALUATION METRICS TEST =========='
    )

    evaluation_result = (
        create_synthetic_evaluation_result()
    )

    training_result = (
        create_synthetic_training_result()
    )

    connection, cursor = (
        create_mock_connection()
    )

    with patch(
        'ml.training.save.get_connection',
        return_value=connection,
    ):

        save_model_history(
            training_result,
            evaluation_result=evaluation_result,
        )

    parameters = (
        cursor.execute.call_args.args[1]
    )

    mae = parameters[9]

    rmse = parameters[10]

    r_squared = parameters[11]

    if mae != 1.25:

        raise AssertionError(
            'MAE was not saved correctly.'
        )

    if rmse != 2.50:

        raise AssertionError(
            'RMSE was not saved correctly.'
        )

    if r_squared != 0.95:

        raise AssertionError(
            'R-squared was not saved correctly.'
        )

    print(
        'Evaluation metrics persistence: PASSED'
    )


# ==========================================================
# ZERO METRIC TEST
# ==========================================================

def test_zero_metrics_are_preserved():
    print()
    print(
        '========== ZERO METRICS TEST =========='
    )

    evaluation_result = {
        'metrics': {
            'mae': 0.0,
            'rmse': 0.0,
            'r_squared': 0.0,
        },
    }

    training_result = (
        create_synthetic_training_result()
    )

    connection, cursor = (
        create_mock_connection()
    )

    with patch(
        'ml.training.save.get_connection',
        return_value=connection,
    ):

        save_model_history(
            training_result,
            evaluation_result=evaluation_result,
        )

    parameters = (
        cursor.execute.call_args.args[1]
    )

    if parameters[9] != 0.0:

        raise AssertionError(
            'MAE = 0.0 was incorrectly discarded.'
        )

    if parameters[10] != 0.0:

        raise AssertionError(
            'RMSE = 0.0 was incorrectly discarded.'
        )

    if parameters[11] != 0.0:

        raise AssertionError(
            'R-squared = 0.0 was incorrectly discarded.'
        )

    print(
        'Zero metrics preservation: PASSED'
    )


# ==========================================================
# INVALID TRAINING RESULT TEST
# ==========================================================

def test_invalid_training_result():
    print()
    print(
        '========== INVALID TRAINING RESULT TEST =========='
    )

    invalid_cases = [

        None,

        {},

        {
            'model': None,
            'feature_names': [
                'Feature_1'
            ],
            'training_rows': 5,
            'target_name':
                'Target_Expense_Total_1D',
        },

        {
            'model':
                create_synthetic_model(),

            'feature_names': [],

            'training_rows': 5,

            'target_name':
                'Target_Expense_Total_1D',
        },

        {
            'model':
                create_synthetic_model(),

            'feature_names': [
                'Feature_1',
                'Feature_2',
            ],

            'training_rows': None,

            'target_name':
                'Target_Expense_Total_1D',
        },

        {
            'model':
                create_synthetic_model(),

            'feature_names': [
                'Feature_1',
                'Feature_2',
            ],

            'training_rows': 5,

            'target_name': None,
        },
    ]

    for invalid_result in invalid_cases:

        try:

            save_model_history(
                invalid_result,
            )

        except ValueError:

            continue

        raise AssertionError(
            'Invalid training result was not rejected.'
        )

    print(
        'Invalid training result handling: PASSED'
    )


# ==========================================================
# INVALID MODEL PARAMETERS TEST
# ==========================================================

def test_invalid_model_parameters():
    print()
    print(
        '========== INVALID MODEL PARAMETERS TEST =========='
    )

    # ------------------------------------------------------
    # Non-finite coefficient
    # ------------------------------------------------------

    model = create_synthetic_model()

    model.coef_[0] = np.nan

    training_result = {
        'model':
            model,

        'feature_names':
            [
                'Feature_1',
                'Feature_2',
            ],

        'training_rows':
            5,

        'target_name':
            'Target_Expense_Total_1D',
    }

    connection, _ = (
        create_mock_connection()
    )

    with patch(
        'ml.training.save.get_connection',
        return_value=connection,
    ):

        try:

            save_model_history(
                training_result,
            )

        except ValueError:

            pass

        else:

            raise AssertionError(
                'Non-finite coefficient was not rejected.'
            )

    # ------------------------------------------------------
    # Non-finite intercept
    # ------------------------------------------------------

    model = create_synthetic_model()

    model.intercept_ = np.inf

    training_result['model'] = model

    with patch(
        'ml.training.save.get_connection',
        return_value=connection,
    ):

        try:

            save_model_history(
                training_result,
            )

        except ValueError:

            pass

        else:

            raise AssertionError(
                'Non-finite intercept was not rejected.'
            )

    # ------------------------------------------------------
    # Feature/coefficient mismatch
    # ------------------------------------------------------

    model = create_synthetic_model()

    training_result = {
        'model':
            model,

        'feature_names':
            [
                'Feature_1',
            ],

        'training_rows':
            5,

        'target_name':
            'Target_Expense_Total_1D',
    }

    with patch(
        'ml.training.save.get_connection',
        return_value=connection,
    ):

        try:

            save_model_history(
                training_result,
            )

        except ValueError:

            pass

        else:

            raise AssertionError(
                'Feature/coefficient mismatch was not rejected.'
            )

    print(
        'Invalid model parameter handling: PASSED'
    )


# ==========================================================
# LOAD MODEL TEST
# ==========================================================

def test_load_model_from_history():
    print()
    print(
        '========== LOAD MODEL TEST =========='
    )

    history = (
        create_synthetic_history()
    )

    loaded_result = (
        load_model_from_history(
            history
        )
    )

    if loaded_result is None:

        raise AssertionError(
            'Loaded result is None.'
        )

    loaded_model = (
        loaded_result['model']
    )

    if loaded_model is None:

        raise AssertionError(
            'Loaded model is None.'
        )

    if loaded_result[
        'feature_names'
    ] != history[
        'feature_names'
    ]:

        raise AssertionError(
            'Feature names were not preserved.'
        )

    if loaded_result[
        'target_name'
    ] != history[
        'target_name'
    ]:

        raise AssertionError(
            'Target name was not preserved.'
        )

    print(
        'Model reconstruction: PASSED'
    )

    print(
        f"Target: {loaded_result['target_name']}"
    )


# ==========================================================
# LOAD PARAMETERS TEST
# ==========================================================

def test_loaded_model_parameters():
    print()
    print(
        '========== LOADED MODEL PARAMETERS TEST =========='
    )

    history = (
        create_synthetic_history()
    )

    loaded_result = (
        load_model_from_history(
            history
        )
    )

    loaded_model = (
        loaded_result['model']
    )

    for original, loaded in zip(
        history['coefficients'],
        loaded_model.coef_,
    ):

        if abs(
            float(original)
            - float(loaded)
        ) > 1e-10:

            raise AssertionError(
                'Loaded coefficient does not match.'
            )

    if abs(
        float(history['intercept'])
        - float(
            loaded_model.intercept_
        )
    ) > 1e-10:

        raise AssertionError(
            'Loaded intercept does not match.'
        )

    print(
        'Coefficient preservation: PASSED'
    )

    print(
        'Intercept preservation: PASSED'
    )


# ==========================================================
# PREDICTION PRESERVATION TEST
# ==========================================================

def test_prediction_preservation():
    print()
    print(
        '========== PREDICTION PRESERVATION TEST =========='
    )

    original_model = (
        create_synthetic_model()
    )

    history = (
        create_synthetic_history()
    )

    loaded_result = (
        load_model_from_history(
            history
        )
    )

    loaded_model = (
        loaded_result['model']
    )

    X = np.array([
        [6.0, 60.0],
        [7.0, 70.0],
        [8.0, 80.0],
    ])

    original_predictions = (
        original_model.predict(X)
    )

    loaded_predictions = (
        loaded_model.predict(X)
    )

    if len(
        original_predictions
    ) != len(
        loaded_predictions
    ):

        raise AssertionError(
            'Prediction count mismatch.'
        )

    for original, loaded in zip(
        original_predictions,
        loaded_predictions,
    ):

        if abs(
            float(original)
            - float(loaded)
        ) > 1e-10:

            raise AssertionError(
                'Loaded predictions do not match original predictions.'
            )

    print(
        'Prediction preservation: PASSED'
    )

    print(
        'Original predictions:',
        [
            float(value)
            for value in original_predictions
        ],
    )

    print(
        'Loaded predictions:',
        [
            float(value)
            for value in loaded_predictions
        ],
    )


# ==========================================================
# INVALID HISTORY TEST
# ==========================================================

def test_invalid_history():
    print()
    print(
        '========== INVALID HISTORY TEST =========='
    )

    invalid_histories = [

        None,

        {},

        {
            'algorithm':
                'RandomForest',
            'feature_names':
                ['Feature_1'],
            'coefficients':
                [1.0],
            'intercept':
                0.0,
        },

        {
            'algorithm':
                'LinearRegression',
            'feature_names':
                [],
            'coefficients':
                [1.0],
            'intercept':
                0.0,
        },

        {
            'algorithm':
                'LinearRegression',
            'feature_names':
                ['Feature_1'],
            'coefficients':
                [],
            'intercept':
                0.0,
        },

        {
            'algorithm':
                'LinearRegression',
            'feature_names':
                ['Feature_1'],
            'coefficients':
                [1.0, 2.0],
            'intercept':
                0.0,
        },

        {
            'algorithm':
                'LinearRegression',
            'feature_names':
                ['Feature_1'],
            'coefficients':
                [np.nan],
            'intercept':
                0.0,
        },

        {
            'algorithm':
                'LinearRegression',
            'feature_names':
                ['Feature_1'],
            'coefficients':
                [1.0],
            'intercept':
                np.inf,
        },

        {
            'algorithm':
                'LinearRegression',
            'feature_names':
                ['Feature_1'],
            'coefficients':
                [1.0],
            'intercept':
                None,
        },
    ]

    for history in invalid_histories:

        try:

            load_model_from_history(
                history
            )

        except ValueError:

            continue

        raise AssertionError(
            'Invalid model history was not rejected.'
        )

    print(
        'Invalid model history handling: PASSED'
    )


# ==========================================================
# REGISTRY LATEST MODEL TEST
# ==========================================================

def test_registry_latest_model():
    print()
    print(
        '========== REGISTRY LATEST MODEL TEST =========='
    )

    history = (
        create_synthetic_history(
            model_history_id=201
        )
    )

    connection, cursor = (
        create_mock_connection(
            history
        )
    )

    with patch(
        'ml.training.registry.get_connection',
        return_value=connection,
    ):

        result = (
            get_latest_model_history()
        )

    if result is None:

        raise AssertionError(
            'Latest model history was not returned.'
        )

    if result['id'] != 201:

        raise AssertionError(
            'Latest model ID is incorrect.'
        )

    if result[
        'target_name'
    ] != 'Target_Expense_Total_1D':

        raise AssertionError(
            'Latest model target name is incorrect.'
        )

    if not cursor.execute.called:

        raise AssertionError(
            'Registry query was not executed.'
        )

    print(
        'Latest model registry lookup: PASSED'
    )


# ==========================================================
# REGISTRY MODEL BY ID TEST
# ==========================================================

def test_registry_model_by_id():
    print()
    print(
        '========== REGISTRY MODEL BY ID TEST =========='
    )

    history = (
        create_synthetic_history(
            model_history_id=202
        )
    )

    connection, cursor = (
        create_mock_connection(
            history
        )
    )

    with patch(
        'ml.training.registry.get_connection',
        return_value=connection,
    ):

        result = (
            get_model_history_by_id(
                202
            )
        )

    if result is None:

        raise AssertionError(
            'Model history by ID was not returned.'
        )

    if result['id'] != 202:

        raise AssertionError(
            'Returned model ID is incorrect.'
        )

    if result[
        'target_name'
    ] != 'Target_Expense_Total_1D':

        raise AssertionError(
            'Target name was not returned by registry.'
        )

    parameters = (
        cursor.execute.call_args.args[1]
    )

    if parameters != (202,):

        raise AssertionError(
            'Model history ID was not passed correctly.'
        )

    print(
        'Model-by-ID registry lookup: PASSED'
    )


# ==========================================================
# REGISTRY JSON DECODING TEST
# ==========================================================

def test_registry_json_decoding():
    print()
    print(
        '========== REGISTRY JSON DECODING TEST =========='
    )

    history = (
        create_synthetic_history(
            model_history_id=203
        )
    )

    # Simulate actual database representation.
    history['feature_names'] = json.dumps(
        history['feature_names']
    )

    history['coefficients'] = json.dumps(
        history['coefficients']
    )

    history['feature_means'] = json.dumps(
        history['feature_means']
    )

    history['feature_scales'] = json.dumps(
        history['feature_scales']
    )

    connection, _ = (
        create_mock_connection(
            history
        )
    )

    with patch(
        'ml.training.registry.get_connection',
        return_value=connection,
    ):

        result = (
            get_latest_model_history()
        )

    if not isinstance(
        result['feature_names'],
        list,
    ):

        raise AssertionError(
            'Feature names were not decoded into a list.'
        )

    if not isinstance(
        result['coefficients'],
        list,
    ):

        raise AssertionError(
            'Coefficients were not decoded into a list.'
        )

    if not isinstance(
        result['feature_means'],
        dict,
    ):

        raise AssertionError(
            'Feature means were not decoded into a dictionary.'
        )

    if not isinstance(
        result['feature_scales'],
        dict,
    ):

        raise AssertionError(
            'Feature scales were not decoded into a dictionary.'
        )

    print(
        'Registry JSON decoding: PASSED'
    )


# ==========================================================
# NO MODEL TEST
# ==========================================================

def test_no_model():
    print()
    print(
        '========== NO MODEL TEST =========='
    )

    connection, cursor = (
        create_mock_connection(
            None
        )
    )

    with patch(
        'ml.training.registry.get_connection',
        return_value=connection,
    ):

        latest = (
            get_latest_model_history()
        )

    if latest is not None:

        raise AssertionError(
            'Latest model should be None when database has no model.'
        )

    print(
        'No-model handling: PASSED'
    )


# ==========================================================
# LOAD LATEST MODEL TEST
# ==========================================================

def test_load_latest_model():
    print()
    print(
        '========== LOAD LATEST MODEL TEST =========='
    )

    history = (
        create_synthetic_history(
            model_history_id=301
        )
    )

    with patch(
        'ml.training.load.get_latest_model_history',
        return_value=history,
    ):

        result = (
            load_latest_model()
        )

    if result is None:

        raise AssertionError(
            'Latest model could not be loaded.'
        )

    if result[
        'model_history_id'
    ] != 301:

        raise AssertionError(
            'Latest model history ID is incorrect.'
        )

    if result[
        'target_name'
    ] != 'Target_Expense_Total_1D':

        raise AssertionError(
            'Latest model target name is incorrect.'
        )

    print(
        'Latest model loading: PASSED'
    )


# ==========================================================
# LOAD MODEL BY ID TEST
# ==========================================================

def test_load_model_by_id():
    print()
    print(
        '========== LOAD MODEL BY ID TEST =========='
    )

    history = (
        create_synthetic_history(
            model_history_id=302
        )
    )

    with patch(
        'ml.training.load.get_model_history_by_id',
        return_value=history,
    ):

        result = (
            load_model_by_id(
                302
            )
        )

    if result is None:

        raise AssertionError(
            'Model could not be loaded by ID.'
        )

    if result[
        'model_history_id'
    ] != 302:

        raise AssertionError(
            'Loaded model history ID is incorrect.'
        )

    print(
        'Model-by-ID loading: PASSED'
    )


# ==========================================================
# LOAD NONEXISTENT MODEL TEST
# ==========================================================

def test_load_nonexistent_model():
    print()
    print(
        '========== LOAD NONEXISTENT MODEL TEST =========='
    )

    with patch(
        'ml.training.load.get_latest_model_history',
        return_value=None,
    ):

        latest = (
            load_latest_model()
        )

    if latest is not None:

        raise AssertionError(
            'load_latest_model() should return None.'
        )

    with patch(
        'ml.training.load.get_model_history_by_id',
        return_value=None,
    ):

        result = (
            load_model_by_id(
                999999
            )
        )

    if result is not None:

        raise AssertionError(
            'load_model_by_id() should return None.'
        )

    print(
        'Nonexistent model handling: PASSED'
    )


# ==========================================================
# FULL PERSISTENCE INTEGRATION TEST
# ==========================================================

def test_full_persistence_integration():
    print()
    print(
        '========== FULL PERSISTENCE INTEGRATION TEST =========='
    )

    # ------------------------------------------------------
    # 1. Create synthetic model
    # ------------------------------------------------------

    training_result = (
        create_synthetic_training_result()
    )

    original_model = (
        training_result['model']
    )

    evaluation_result = (
        create_synthetic_evaluation_result()
    )

    # ------------------------------------------------------
    # 2. Save
    # ------------------------------------------------------

    connection, cursor = (
        create_mock_connection()
    )

    with patch(
        'ml.training.save.get_connection',
        return_value=connection,
    ):

        model_history_id = (
            save_model_history(
                training_result,
                evaluation_result=evaluation_result,
            )
        )

    if model_history_id != 101:

        raise AssertionError(
            'Synthetic model was not saved correctly.'
        )

    # ------------------------------------------------------
    # 3. Build synthetic DB history
    # ------------------------------------------------------

    history = (
        create_synthetic_history(
            model_history_id
        )
    )

    # ------------------------------------------------------
    # 4. Load
    # ------------------------------------------------------

    loaded_result = (
        load_model_from_history(
            history
        )
    )

    loaded_model = (
        loaded_result['model']
    )

    # ------------------------------------------------------
    # 5. Predictions
    # ------------------------------------------------------

    X = np.array([
        [9.0, 90.0],
        [10.0, 100.0],
        [11.0, 110.0],
    ])

    original_predictions = (
        original_model.predict(X)
    )

    loaded_predictions = (
        loaded_model.predict(X)
    )

    # ------------------------------------------------------
    # 6. Compare
    # ------------------------------------------------------

    if not np.allclose(
        original_predictions,
        loaded_predictions,
        atol=1e-10,
    ):

        raise AssertionError(
            'Predictions changed after persistence.'
        )

    if loaded_result[
        'feature_names'
    ] != training_result[
        'feature_names'
    ]:

        raise AssertionError(
            'Feature names changed after persistence.'
        )

    if loaded_result[
        'target_name'
    ] != training_result[
        'target_name'
    ]:

        raise AssertionError(
            'Target name changed after persistence.'
        )

    print(
        'Save → Load → Predict integration: PASSED'
    )


# ==========================================================
# RUN ALL TESTS
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )

    print(
        '          MODEL PERSISTENCE TEST SUITE'
    )

    print(
        '=================================================='
    )

    test_save_model_history()

    test_save_model_parameters()

    test_save_evaluation_metrics()

    test_zero_metrics_are_preserved()

    test_invalid_training_result()

    test_invalid_model_parameters()

    test_load_model_from_history()

    test_loaded_model_parameters()

    test_prediction_preservation()

    test_invalid_history()

    test_registry_latest_model()

    test_registry_model_by_id()

    test_registry_json_decoding()

    test_no_model()

    test_load_latest_model()

    test_load_model_by_id()

    test_load_nonexistent_model()

    test_full_persistence_integration()

    print()
    print(
        '=================================================='
    )

    print(
        '       ALL MODEL PERSISTENCE TESTS PASSED'
    )

    print(
        '=================================================='
    )