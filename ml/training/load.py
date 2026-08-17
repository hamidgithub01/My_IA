import math

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
    Reconstruct a trained LinearRegression model from a
    model_history database record.

    No training is performed.

    The model is reconstructed from:

        - algorithm
        - feature_names
        - coefficients
        - intercept

    Target_Expense_Total remains the target definition.
    """

    # ------------------------------------------------------
    # Validate history record
    # ------------------------------------------------------

    if model_history is None:
        raise ValueError(
            'Model history record is required.'
        )

    # ------------------------------------------------------
    # Algorithm
    # ------------------------------------------------------

    algorithm = model_history.get(
        'algorithm'
    )

    if algorithm != 'LinearRegression':
        raise ValueError(
            f'Unsupported model algorithm: {algorithm}'
        )

    # ------------------------------------------------------
    # Feature names
    # ------------------------------------------------------

    feature_names = model_history.get(
        'feature_names'
    ) or []

    if not isinstance(
        feature_names,
        list,
    ):
        raise ValueError(
            'Model history feature_names must be a list.'
        )

    if not feature_names:
        raise ValueError(
            'Model history contains no feature names.'
        )

    # ------------------------------------------------------
    # Coefficients
    # ------------------------------------------------------

    coefficients = model_history.get(
        'coefficients'
    ) or []

    if not isinstance(
        coefficients,
        list,
    ):
        raise ValueError(
            'Model history coefficients must be a list.'
        )

    if not coefficients:
        raise ValueError(
            'Model history contains no coefficients.'
        )

    # ------------------------------------------------------
    # Feature / coefficient consistency
    # ------------------------------------------------------

    if len(feature_names) != len(
        coefficients
    ):
        raise ValueError(
            'Feature count does not match coefficient count.'
        )

    # ------------------------------------------------------
    # Convert and validate coefficients
    # ------------------------------------------------------

    try:

        coefficient_values = [
            float(value)
            for value in coefficients
        ]

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            'Model history contains invalid coefficients.'
        ) from exc

    if not all(
        math.isfinite(value)
        for value in coefficient_values
    ):
        raise ValueError(
            'Model coefficients contain a non-finite value.'
        )

    # ------------------------------------------------------
    # Intercept
    # ------------------------------------------------------

    intercept = model_history.get(
        'intercept'
    )

    if intercept is None:
        raise ValueError(
            'Model history contains no intercept.'
        )

    try:

        intercept_value = float(
            intercept
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            'Model history contains an invalid intercept.'
        ) from exc

    if not math.isfinite(
        intercept_value
    ):
        raise ValueError(
            'Model intercept is not finite.'
        )

    # ------------------------------------------------------
    # Reconstruct model
    # ------------------------------------------------------

    model = LinearRegression()

    model.coef_ = np.asarray(
        coefficient_values,
        dtype=float,
    )

    model.intercept_ = intercept_value

    # ------------------------------------------------------
    # sklearn fitted-model metadata
    # ------------------------------------------------------

    model.n_features_in_ = len(
        feature_names
    )

    # ------------------------------------------------------
    # Build training-result-compatible structure
    # ------------------------------------------------------

    target_name = model_history.get(
        'target_name'
    )

    if not target_name:
        raise ValueError(
            'Model history contains no target name.'
        )

    return {
        'model':
            model,

        'feature_names':
            feature_names,

        'training_rows':
            int(
                model_history.get(
                    'training_rows',
                    0,
                )
                or 0
            ),

        'target_name':
            target_name,

        'model_history_id':
            model_history.get(
                'id'
            ),
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