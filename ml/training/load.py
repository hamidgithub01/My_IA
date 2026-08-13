import numpy as np

from sklearn.linear_model import LinearRegression

from ml.training.registry import (
    get_latest_model_history,
    get_model_history_by_id,
)


# ==========================================================
# MODEL LOADING
# ==========================================================

def load_model_from_history(
    model_history,
):
    """
    Reconstruct a trained model from a model history record.

    The model is reconstructed from:
        - algorithm
        - coefficients
        - intercept

    No training is performed.
    """

    if model_history is None:
        raise ValueError(
            'Model history record is required.'
        )

    algorithm = model_history.get(
        'algorithm'
    )

    if algorithm != 'LinearRegression':
        raise ValueError(
            f'Unsupported model algorithm: {algorithm}'
        )

    feature_names = model_history.get(
        'feature_names'
    ) or []

    coefficients = model_history.get(
        'coefficients'
    ) or []

    intercept = model_history.get(
        'intercept'
    )

    if not feature_names:
        raise ValueError(
            'Model history contains no feature names.'
        )

    if not coefficients:
        raise ValueError(
            'Model history contains no coefficients.'
        )

    if len(feature_names) != len(coefficients):
        raise ValueError(
            'Feature count does not match coefficient count.'
        )

    if intercept is None:
        raise ValueError(
            'Model history contains no intercept.'
        )

    model = LinearRegression()

    # ------------------------------------------------------
    # Reconstruct fitted model parameters
    # ------------------------------------------------------

    model.coef_ = np.asarray(
        [
            float(value)
            for value in coefficients
        ],
        dtype=float,
    )

    model.intercept_ = float(
        intercept
    )

    # ------------------------------------------------------
    # Required fitted-model attributes
    # ------------------------------------------------------

    model.n_features_in_ = len(
        feature_names
    )

    return {
        'model': model,
        'feature_names': feature_names,
        'training_rows':
            model_history.get(
                'training_rows',
                0,
            ),
        'target_name':
            'Target_Expense_Total',
        'model_history_id':
            model_history.get('id'),
    }


# ==========================================================
# LATEST MODEL
# ==========================================================

def load_latest_model():
    """
    Load the most recently saved model.

    Returns:
        Reconstructed model information,
        or None if no model has been saved yet.
    """

    model_history = (
        get_latest_model_history()
    )

    if model_history is None:
        return None

    return load_model_from_history(
        model_history
    )


# ==========================================================
# MODEL BY ID
# ==========================================================

def load_model_by_id(
    model_history_id,
):
    """
    Load a specific saved model by history ID.

    Returns:
        Reconstructed model information,
        or None if the model does not exist.
    """

    model_history = (
        get_model_history_by_id(
            model_history_id
        )
    )

    if model_history is None:
        return None

    return load_model_from_history(
        model_history
    )