from ml.training.train import (
    train_model,
)

from ml.evaluation.evaluate import (
    evaluate_model,
)

from ml.training.save import (
    save_model_history,
)


def train_and_register_model():
    """
    Train the forecasting model, evaluate it when possible,
    and save the trained model into model history.

    The model is saved only after successful training.

    Evaluation uses the exact training_result produced by
    the training pipeline.

    No second dataset is created and no retraining occurs.
    """

    # ------------------------------------------------------
    # TRAIN
    # ------------------------------------------------------

    training_result = train_model()

    # ------------------------------------------------------
    # EVALUATION
    # ------------------------------------------------------

    evaluation_result = None

    try:

        evaluation_result = evaluate_model(
            training_result=training_result,
        )

    except ValueError as exc:

        # Evaluation may legitimately be unavailable when
        # the test dataset is insufficient.
        #
        # However, do not silently hide unrelated pipeline
        # errors.

        message = str(
            exc
        )

        evaluation_unavailable_messages = (
            'No test features are available',
            'No test targets are available',
            'Test dataset contains fewer rows',
        )

        if not message.startswith(
            evaluation_unavailable_messages
        ):

            raise

        evaluation_result = None

    # ------------------------------------------------------
    # SAVE
    # ------------------------------------------------------

    model_history_id = save_model_history(
        training_result,
        evaluation_result,
        reused_previous_state=False,
    )

    # ------------------------------------------------------
    # RESULT
    # ------------------------------------------------------

    return {

        'training_result':
            training_result,

        'evaluation_result':
            evaluation_result,

        'model_history_id':
            model_history_id,
    }


if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )
    print(
        '          TRAIN AND REGISTER MODEL'
    )
    print(
        '=================================================='
    )

    result = train_and_register_model()

    training_result = result[
        'training_result'
    ]

    evaluation_result = result[
        'evaluation_result'
    ]

    model_history_id = result[
        'model_history_id'
    ]

    print()
    print(
        '========== TRAINING =========='
    )

    print(
        'Target:',
        training_result[
            'target_name'
        ]
    )

    print(
        'Target task:',
        training_result[
            'target_task'
        ]
    )

    print(
        'Target type:',
        training_result[
            'target_type'
        ]
    )

    print(
        'Model type:',
        training_result[
            'model_type'
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

    print()
    print(
        '========== EVALUATION =========='
    )

    if evaluation_result is None:

        print(
            'Evaluation: NOT AVAILABLE'
        )

    else:

        print(
            'Evaluation status:',
            evaluation_result.get(
                'evaluation_status'
            )
        )

        print(
            'Metrics:',
            evaluation_result.get(
                'metrics'
            )
        )

    print()
    print(
        '========== MODEL REGISTRY =========='
    )

    print(
        'Model history ID:',
        model_history_id
    )

    print()
    print(
        '=================================================='
    )
    print(
        '       TRAIN AND REGISTER MODEL PASSED'
    )
    print(
        '=================================================='
    )