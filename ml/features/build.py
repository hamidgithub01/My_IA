
from datetime import date

from ml.preparation.preparation import (
    get_prepared_dataset,
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

from ml.features.contextual import (
    create_known_future_features,
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

    Information is divided into two fundamentally different
    groups:

        1. Known future information
        2. Historical information

    Known future information:

        Plans and recurring activity that are already known
        before the target day occurs.

    Historical information:

        Information from dates strictly before the target
        date.

    IMPORTANT:

        The target day's actual outcomes must NEVER be used
        as features.

        Examples of forbidden target-day outcomes:

            Expense_Total
            Income_Total
            Activity_Cost
            Health_Record_Count
            etc.

    Date-related information is allowed because the calendar
    date is known before the target day occurs.
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
    # Known future features
    #
    # These are information sources that can be known before
    # the target day occurs.
    #
    # Plans:
    #     planned activities/events/costs.
    #
    # Recurring:
    #     expected recurring financial activity.
    #
    # These are NOT historical outcomes.
    # ------------------------------------------------------

    features.update(
        create_known_future_features(
            target_row
        )
    )

    # ------------------------------------------------------
    # Historical features
    #
    # previous_rows contains ONLY dates before target_row.
    #
    # Therefore actual outcomes from the target day cannot
    # leak into these features.
    # ------------------------------------------------------

    features.update(
        create_history_features(
            target_row,
            previous_rows,
        )
    )

    # ------------------------------------------------------
    # Lag features
    #
    # Only previous rows are allowed.
    # ------------------------------------------------------

    features.update(
        create_lag_features(
            target_row,
            previous_rows,
        )
    )

    # ------------------------------------------------------
    # Rolling historical features
    #
    # Only previous rows are allowed.
    # ------------------------------------------------------

    features.update(
        create_rolling_features(
            target_row,
            previous_rows,
        )
    )

    return features


# ==========================================================
# HISTORICAL TRAINING BOUNDARY
# ==========================================================

def get_training_cutoff_date(
    prepared_data,
):
    """
    Determine the latest date that is safe to use as a
    supervised-learning target.

    The preparation stage may create future calendar rows
    because of:

        Plans
        Recurring rules

    Those future rows contain known future information but
    do NOT contain an actual observed target outcome yet.

    Therefore, they must not be treated as historical
    training targets.

    The current calendar date provides a final safety
    boundary.

    Returns:

        A date object.
    """

    today = date.today()

    historical_dates = [
        row['Date']
        for row in prepared_data
        if row.get('Date') is not None
        and row['Date'] <= today
    ]

    if not historical_dates:
        return None

    return max(
        historical_dates
    )


# ==========================================================
# TRAINING DATASET
# ==========================================================

def build_training_dataset():
    """
    Build a supervised learning dataset for future
    financial forecasting.

    Learning structure:

        Previous historical days
                  ↓
        Known future information
                  ↓
        Features for target day
                  ↓
        Actual target-day outcome

    Example:

        Previous days
             +
        known plans
             +
        known recurring activity
             +
        calendar information
             +
        historical patterns
             ↓
        predict target-day expenses

    IMPORTANT:

        The target day's actual Expense_Total is NEVER used
        as an input feature.

    Future dates generated only by Plans or Recurring records
    are not included as training targets because their actual
    outcomes have not occurred yet.

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

    # ------------------------------------------------------
    # Determine the historical training boundary
    # ------------------------------------------------------

    training_cutoff_date = (
        get_training_cutoff_date(
            prepared_data
        )
    )

    if training_cutoff_date is None:
        return []

    # ------------------------------------------------------
    # Only dates that have already occurred may become
    # supervised-learning targets.
    #
    # This prevents future Plan/Recurring rows from becoming
    # fake targets with Expense_Total = 0.
    # ------------------------------------------------------

    historical_data = [
        row
        for row in prepared_data
        if row['Date']
        <= training_cutoff_date
    ]

    if len(historical_data) < 2:
        return []

    dataset = []

    for index in range(
        1,
        len(historical_data),
    ):

        target_row = historical_data[index]

        # --------------------------------------------------
        # Only information strictly before the target date.
        # --------------------------------------------------

        previous_rows = historical_data[
            :index
        ]

        features = build_feature_row(
            target_row,
            previous_rows,
        )

        # --------------------------------------------------
        # Target
        #
        # This is the actual expense of the target day.
        #
        # It is deliberately added AFTER all features have
        # been constructed.
        # --------------------------------------------------

        features[
            'Target_Expense_Total'
        ] = float(
            target_row.get(
                'Expense_Total'
            )
            or 0.0
        )

        dataset.append(
            features
        )

    return dataset


# ==========================================================
# FEATURE NAMES
# ==========================================================

def get_feature_names(
    data,
):
    """
    Return the names of features that are allowed to enter
    the machine-learning model.

    Date and target are metadata/target values and therefore
    are explicitly excluded.

    Known future information such as Plans and Recurring
    features is allowed because those values are available
    before the target day occurs.
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
