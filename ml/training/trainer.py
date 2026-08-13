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

    The model is always saved after successful training.

    Chronological evaluation is optional because it requires
    enough historical records.

    When evaluation is unavailable, the model is still saved
    with NULL evaluation metrics.
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
            training_result=None,
        )

    except ValueError:

        # Not enough historical data for chronological
        # evaluation.
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