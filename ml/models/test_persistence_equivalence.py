from math import isclose

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
# PERSISTENCE EQUIVALENCE TEST
# ==========================================================

def test_persistence_equivalence():
    """
    Verify that a model produces the same predictions before
    and after persistence.

    Pipeline:

        Train
          ↓
        Predict
          ↓
        Save
          ↓
        Load
          ↓
        Predict
          ↓
        Compare

    No retraining is performed after loading.
    """

    target_name = (
        'Target_Expense_Total_1D'
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

    model = training_result[
        'model'
    ]

    X_test = training_result[
        'X_test'
    ]

    if not X_test:

        raise ValueError(
            'No test features are available for '
            'persistence equivalence test.'
        )

    print(
        'Target:',
        training_result[
            'target_name'
        ]
    )

    print(
        'Algorithm:',
        training_result[
            'algorithm'
        ]
    )

    print(
        'Training rows:',
        training_result[
            'training_rows'
        ]
    )

    print(
        'Test rows:',
        training_result[
            'test_rows'
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
    # ORIGINAL PREDICTIONS
    # ------------------------------------------------------

    print()
    print(
        '========== ORIGINAL MODEL =========='
    )

    original_predictions = model.predict(
        X_test
    )

    original_predictions = [
        float(value)
        for value in original_predictions
    ]

    print(
        'Original predictions:',
        original_predictions
    )

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    print()
    print(
        '========== SAVE MODEL =========='
    )

    model_history_id = save_model_history(
        training_result,
        evaluation_result=None,
        reused_previous_state=False,
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
        '========== LOAD MODEL =========='
    )

    loaded_result = load_model_history(
        model_history_id
    )

    loaded_model = loaded_result[
        'model'
    ]

    print(
        'Loaded model:',
        loaded_model.__class__.__name__
    )

    print(
        'Loaded target:',
        loaded_result[
            'target_name'
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
    # RESTORED PREDICTIONS
    # ------------------------------------------------------

    print()
    print(
        '========== RESTORED MODEL =========='
    )

    restored_predictions = (
        loaded_model.predict(
            X_test
        )
    )

    restored_predictions = [
        float(value)
        for value in restored_predictions
    ]

    print(
        'Restored predictions:',
        restored_predictions
    )

    # ------------------------------------------------------
    # PREDICTION COUNT
    # ------------------------------------------------------

    if len(
        original_predictions
    ) != len(
        restored_predictions
    ):

        raise AssertionError(
            'Original and restored models produced '
            'different numbers of predictions.'
        )

    # ------------------------------------------------------
    # PREDICTION EQUIVALENCE
    # ------------------------------------------------------

    differences = []

    for index, (
        original,
        restored,
    ) in enumerate(
        zip(
            original_predictions,
            restored_predictions,
        )
    ):

        if not isclose(
            original,
            restored,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):

            differences.append(
                {
                    'index':
                        index,

                    'original':
                        original,

                    'restored':
                        restored,

                    'difference':
                        abs(
                            original
                            - restored
                        ),
                }
            )

    if differences:

        raise AssertionError(
            'Model persistence changed predictions:\n'
            f'{differences}'
        )

    # ------------------------------------------------------
    # FEATURE SCHEMA
    # ------------------------------------------------------

    original_features = (
        training_result[
            'feature_names'
        ]
    )

    restored_features = (
        loaded_result[
            'feature_names'
        ]
    )

    if original_features != restored_features:

        raise AssertionError(
            'Feature schema changed after model persistence.'
        )

    # ------------------------------------------------------
    # MODEL ID
    # ------------------------------------------------------

    if loaded_result[
        'model_history_id'
    ] != model_history_id:

        raise AssertionError(
            'Loaded model history ID does not match '
            'the saved model history ID.'
        )

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    return {
        'passed':
            True,

        'model_history_id':
            model_history_id,

        'target_name':
            target_name,

        'original_predictions':
            original_predictions,

        'restored_predictions':
            restored_predictions,

        'feature_count':
            len(
                original_features
            ),
    }


# ==========================================================
# SIMPLE TEST
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )

    print(
        '       MODEL PERSISTENCE EQUIVALENCE TEST'
    )

    print(
        '=================================================='
    )

    result = test_persistence_equivalence()

    print()
    print(
        '========== RESULT =========='
    )

    print(
        'Model history ID:',
        result[
            'model_history_id'
        ]
    )

    print(
        'Target:',
        result[
            'target_name'
        ]
    )

    print(
        'Feature count:',
        result[
            'feature_count'
        ]
    )

    print(
        'Original predictions:',
        result[
            'original_predictions'
        ]
    )

    print(
        'Restored predictions:',
        result[
            'restored_predictions'
        ]
    )

    print(
        'Predictions identical: YES'
    )

    print()
    print(
        '=================================================='
    )

    print(
        '     MODEL PERSISTENCE EQUIVALENCE PASSED'
    )

    print(
        '=================================================='
    )