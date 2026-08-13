from ml.preparation.preparation import (
    get_prepared_dataset,
)

from ml.features.behavioral import (
    create_behavioral_features,
)

from ml.features.contextual import (
    create_contextual_features,
)

from ml.features.temporal import (
    create_temporal_features,
)

from ml.features.history import (
    create_history_features,
)

from ml.features.lags import (
    create_lag_features,
)

from ml.features.rolling import (
    create_rolling_features,
)


# ==========================================================
# FEATURE ROW
# ==========================================================

def build_feature_row(
    target_row,
    previous_rows,
):
    """
    Build features for a target day.

    Important rule:

        Information from the target day's actual financial
        outcome must never be used as a feature.

    Historical features are calculated only from
    previous_rows.

    Date-related information is allowed because the
    calendar date is known before the day occurs.
    """

    features = {
        'Date': target_row['Date'],
    }

    # ------------------------------------------------------
    # Temporal features
    #
    # The calendar date of a future day is known in advance.
    # ------------------------------------------------------

    features.update(
        create_temporal_features(
            target_row
        )
    )

    # ------------------------------------------------------
    # Contextual features
    #
    # These are only useful when the information is already
    # known/planned for the target day.
    # ------------------------------------------------------

    features.update(
        create_contextual_features(
            target_row
        )
    )

    # ------------------------------------------------------
    # Behavioral features
    #
    # Only values that are legitimately known for the target
    # day should be used here.
    # ------------------------------------------------------

    features.update(
        create_behavioral_features(
            target_row
        )
    )

    # ------------------------------------------------------
    # Historical features
    #
    # IMPORTANT:
    # previous_rows contains ONLY dates before target_row.
    # ------------------------------------------------------

    features.update(
        create_history_features(
            target_row,
            previous_rows,
        )
    )

    # ------------------------------------------------------
    # Lag features
    # ------------------------------------------------------

    features.update(
        create_lag_features(
            target_row,
            previous_rows,
        )
    )

    # ------------------------------------------------------
    # Rolling historical features
    # ------------------------------------------------------

    features.update(
        create_rolling_features(
            target_row,
            previous_rows,
        )
    )

    return features


# ==========================================================
# TRAINING DATASET
# ==========================================================

def build_training_dataset():
    """
    Build a supervised learning dataset for future
    financial forecasting.

    Learning structure:

        Previous days
              ↓
        Features for target day
              ↓
        Target_Expense_Total

    The target day's actual Expense_Total is NEVER used
    as an input feature.

    Date remains in every row only for identification,
    ordering, evaluation and reporting.
    It is explicitly excluded from X during training.
    """

    prepared_data = get_prepared_dataset()

    if len(prepared_data) < 2:
        return []

    # ------------------------------------------------------
    # Ensure chronological order
    # ------------------------------------------------------

    prepared_data = sorted(
        prepared_data,
        key=lambda row: row['Date'],
    )

    dataset = []

    for index in range(
        1,
        len(prepared_data),
    ):

        target_row = prepared_data[index]

        # Only information strictly before the target date.
        previous_rows = prepared_data[:index]

        features = build_feature_row(
            target_row,
            previous_rows,
        )

        # --------------------------------------------------
        # Target
        #
        # This is the actual expense of the target day.
        # It is NOT part of the input features.
        # --------------------------------------------------

        features['Target_Expense_Total'] = float(
            target_row.get(
                'Expense_Total'
            ) or 0.0
        )

        dataset.append(features)

    return dataset


# ==========================================================
# FEATURE NAMES
# ==========================================================

def get_feature_names(data):
    """
    Return the names of features that are allowed to enter
    the machine-learning model.

    Date and target are metadata/target values and therefore
    are explicitly excluded.
    """

    if not data:
        return []

    excluded = {
        'Date',
        'Target_Expense_Total',
    }

    return [
        key
        for key in data[0].keys()
        if key not in excluded
    ]


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def build_feature_dataset():
    """
    Backward-compatible alias.

    New training/evaluation code should use
    build_training_dataset().
    """

    return build_training_dataset()