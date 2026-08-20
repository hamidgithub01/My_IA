import numpy as np

from ml.training.train import (
    train_target_model,
)

from ml.training.save import (
    save_model_history,
)

from ml.training.load import (
    load_model_history,
)


# ==========================================================
# MODEL PERSISTENCE TEST
# ==========================================================


def test_model_persistence():
    """
    Test the complete model persistence lifecycle:

        Train
          ↓
        Save to model_history
          ↓
        Load from model_history
          ↓
        Verify restored model
          ↓
        Verify model metadata
          ↓
        Verify learned parameters

    The loaded model must be reconstructed from the stored
    model state without retraining.
    """

    # ------------------------------------------------------
    # TARGET
    # ------------------------------------------------------

    target_name = (
        'Target_Expense_Total_1D'
    )

    print()
    print(
        '=================================================='
    )
    print(
        '             MODEL PERSISTENCE TEST'
    )
    print(
        '=================================================='
    )

    print()
    print(
        'Target:',
        target_name,
    )

    # ------------------------------------------------------
    # TRAIN
    # ------------------------------------------------------

    print()
    print(
        '========== TRAINING =========='
    )

    training_result = train_target_model(
        target_name
    )

    if not training_result:

        raise AssertionError(
            'Training result is empty.'
        )

    original_model = training_result.get(
        'model'
    )

    if original_model is None:

        raise AssertionError(
            'Training result contains no model.'
        )

    print(
        'Algorithm:',
        training_result[
            'algorithm'
        ]
    )

    print(
        'Model type:',
        training_result[
            'model_type'
        ]
    )

    print(
        'Target task:',
        training_result[
            'target_task'
        ]
    )

    print(
        'Training rows:',
        training_result[
            'training_rows'
        ]
    )

    print(
        'Feature count:',
        len(
            training_result[
                'feature_names'
            ]
        )
    )

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    print()
    print(
        '========== SAVING MODEL =========='
    )

    model_history_id = save_model_history(
        training_result,
        evaluation_result=None,
        reused_previous_state=False,
    )

    if model_history_id is None:

        raise AssertionError(
            'Model history ID was not returned.'
        )

    print(
        'Model history ID:',
        model_history_id
    )

    # ------------------------------------------------------
    # LOAD
    # ------------------------------------------------------

    print()
    print(
        '========== LOADING MODEL =========='
    )

    loaded_result = load_model_history(
        model_history_id
    )

    if not loaded_result:

        raise AssertionError(
            'Loaded model result is empty.'
        )

    loaded_model = loaded_result.get(
        'model'
    )

    if loaded_model is None:

        raise AssertionError(
            'Loaded result contains no model.'
        )

    print(
        'Loaded algorithm:',
        loaded_result[
            'algorithm'
        ]
    )

    print(
        'Loaded model type:',
        loaded_result[
            'model_type'
        ]
    )

    print(
        'Loaded target:',
        loaded_result[
            'target_name'
        ]
    )

    print(
        'Loaded training rows:',
        loaded_result[
            'training_rows'
        ]
    )

    print(
        'Loaded feature count:',
        len(
            loaded_result[
                'feature_names'
            ]
        )
    )

    # ------------------------------------------------------
    # VERIFY MODEL ID
    # ------------------------------------------------------

    if loaded_result[
        'model_history_id'
    ] != model_history_id:

        raise AssertionError(
            'Loaded model history ID does not match '
            'the saved model history ID.'
        )

    # ------------------------------------------------------
    # VERIFY TARGET INFORMATION
    # ------------------------------------------------------

    if loaded_result[
        'target_name'
    ] != training_result[
        'target_name'
    ]:

        raise AssertionError(
            'Loaded target name does not match '
            'the trained target name.'
        )

    if loaded_result[
        'target_task'
    ] != training_result[
        'target_task'
    ]:

        raise AssertionError(
            'Loaded target task does not match '
            'the trained target task.'
        )

    if loaded_result[
        'target_type'
    ] != training_result[
        'target_type'
    ]:

        raise AssertionError(
            'Loaded target type does not match '
            'the trained target type.'
        )

    # ------------------------------------------------------
    # VERIFY MODEL INFORMATION
    # ------------------------------------------------------

    if loaded_result[
        'model_type'
    ] != training_result[
        'model_type'
    ]:

        raise AssertionError(
            'Loaded model type does not match '
            'the trained model type.'
        )

    if loaded_result[
        'algorithm'
    ] != training_result[
        'algorithm'
    ]:

        raise AssertionError(
            'Loaded algorithm does not match '
            'the trained algorithm.'
        )

    # ------------------------------------------------------
    # VERIFY FEATURE SCHEMA
    # ------------------------------------------------------

    if loaded_result[
        'feature_names'
    ] != training_result[
        'feature_names'
    ]:

        raise AssertionError(
            'Loaded feature names do not match '
            'the original feature schema.'
        )

    # ------------------------------------------------------
    # VERIFY TRAINING ROW COUNT
    # ------------------------------------------------------

    if loaded_result[
        'training_rows'
    ] != training_result[
        'training_rows'
    ]:

        raise AssertionError(
            'Loaded training row count does not match '
            'the original training row count.'
        )

    # ------------------------------------------------------
    # VERIFY COEFFICIENTS
    # ------------------------------------------------------

    if not hasattr(
        original_model,
        'coef_',
    ):

        raise AssertionError(
            'Original trained model contains no coef_.'
        )

    if not hasattr(
        loaded_model,
        'coef_',
    ):

        raise AssertionError(
            'Loaded model contains no coef_.'
        )

    original_coefficients = (
        original_model.coef_
    )

    loaded_coefficients = (
        loaded_model.coef_
    )

    if original_coefficients.shape != (
        loaded_coefficients.shape
    ):

        raise AssertionError(
            'Loaded coefficient shape does not match '
            'the original coefficient shape.'
        )

    if not (
        original_coefficients
        == loaded_coefficients
    ).all():

        raise AssertionError(
            'Loaded coefficients do not exactly match '
            'the original trained coefficients.'
        )

    # ------------------------------------------------------
    # VERIFY INTERCEPT
    # ------------------------------------------------------

    if not hasattr(
        original_model,
        'intercept_',
    ):

        raise AssertionError(
            'Original trained model contains no intercept_.'
        )

    if not hasattr(
        loaded_model,
        'intercept_',
    ):

        raise AssertionError(
            'Loaded model contains no intercept_.'
        )

    original_intercept = (
        original_model.intercept_
    )

    loaded_intercept = (
        loaded_model.intercept_
    )

    if not np.allclose(
        original_intercept,
        loaded_intercept,
    ):

        raise AssertionError(
            'Loaded intercept does not match '
            'the original trained intercept.'
        )

    print(
        'Intercept verification: PASSED'
    )

    # ------------------------------------------------------
    # VERIFY CLASSES
    # ------------------------------------------------------

    if hasattr(
        original_model,
        'classes_',
    ):

        if not hasattr(
            loaded_model,
            'classes_',
        ):

            raise AssertionError(
                'Original model has classes_ but loaded '
                'model does not.'
            )

        if (
            original_model.classes_.tolist()
            != loaded_model.classes_.tolist()
        ):

            raise AssertionError(
                'Loaded classes do not match '
                'the original model classes.'
            )

    # ------------------------------------------------------
    # VERIFY PREDICTION
    # ------------------------------------------------------

    X_test = training_result.get(
        'X_test',
        []
    )

    if X_test:

        original_predictions = (
            original_model.predict(
                X_test
            )
        )

        loaded_predictions = (
            loaded_model.predict(
                X_test
            )
        )

        if (
            original_predictions.tolist()
            != loaded_predictions.tolist()
        ):

            raise AssertionError(
                'Loaded model predictions do not match '
                'the original model predictions.'
            )

        print()
        print(
            'Prediction verification: PASSED'
        )

    else:

        print()
        print(
            'Prediction verification: SKIPPED '
            '(no test features available)'
        )

    # ------------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------------

    print()
    print(
        '=================================================='
    )
    print(
        '       MODEL PERSISTENCE TEST PASSED'
    )
    print(
        '=================================================='
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    test_model_persistence()
