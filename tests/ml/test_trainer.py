from ml.training.trainer import (
    train_and_register_model,
)


print()
print('========== TRAINER PIPELINE TEST ==========')


try:

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
    print('========== TRAINING ==========')

    print(
        'Training completed successfully.'
    )

    print(
        f"Training rows: "
        f"{training_result['training_rows']}"
    )

    print(
        f"Feature count: "
        f"{len(training_result['feature_names'])}"
    )

    print(
        f"Algorithm: "
        f"{training_result['model'].__class__.__name__}"
    )

    print()
    print('========== EVALUATION ==========')

    if evaluation_result is None:

        print(
            'Evaluation unavailable.'
        )

        print(
            'Reason: insufficient historical data.'
        )

    else:

        metrics = evaluation_result[
            'metrics'
        ]

        print(
            f"MAE: "
            f"{metrics['mae']:.4f}"
        )

        print(
            f"RMSE: "
            f"{metrics['rmse']:.4f}"
        )

        r_squared = metrics[
            'r_squared'
        ]

        if r_squared is None:

            print(
                'R²: unavailable'
            )

            print(
                'Reason: insufficient target '
                'variation for R² evaluation.'
            )

        else:

            print(
                f"R²: "
                f"{r_squared:.4f}"
            )

    print()
    print('========== MODEL HISTORY ==========')

    if model_history_id is None:

        print(
            'Model history was not saved.'
        )

    else:

        print(
            f"Model history ID: "
            f"{model_history_id}"
        )

    print()
    print('========== TEST RESULT ==========')

    if model_history_id is not None:

        print(
            'PASS: Training pipeline completed '
            'and model history was saved.'
        )

    else:

        print(
            'PASS: Training completed, '
            'but model history was not saved.'
        )


except Exception as error:

    print()
    print('========== TEST RESULT ==========')

    print(
        'FAIL: Trainer pipeline failed.'
    )

    print(
        f'Reason: {error}'
    )

    raise