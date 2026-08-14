
from datetime import timedelta


from ml.feature_engineering.features import (
    get_feature_dataset,
)

from ml.targets.build import (
    build_target_dataset,
)


# =========================================================
# CONFIGURATION
# =========================================================

# Number of historical observed rows used as input.
#
# Example:
#
#     HISTORY_SIZE = 7
#
# means that the model can use the latest 7 observed
# historical feature rows before the prediction anchor.
#
HISTORY_SIZE = 7


# Forecast horizons expressed in calendar days.
#
# The model will learn separate future outcomes for:
#
#     1 day
#     7 days
#     30 days
#
FORECAST_HORIZONS = (
    1,
    7,
    30,
)


# =========================================================
# BASIC HELPERS
# =========================================================

def _remove_date(row):
    """
    Return a copy of a row without the Date field.

    Date is used for chronological alignment and is not
    automatically treated as a numerical model feature.
    """

    return {
        key: value
        for key, value in row.items()
        if key != 'Date'
    }


def _get_target_names(target_rows):
    """
    Return target names excluding Date.
    """

    if not target_rows:
        return []

    names = set()

    for row in target_rows:

        for key in row.keys():

            if key != 'Date':
                names.add(key)

    return sorted(names)


# =========================================================
# DATE LOOKUPS
# =========================================================

def _build_feature_lookup(feature_rows):
    """
    Build a dictionary indexed by calendar date.
    """

    return {
        row['Date']: row
        for row in feature_rows
        if row.get('Date') is not None
    }


def _build_target_lookup(target_rows):
    """
    Build a dictionary indexed by calendar date.

    Each date points to the daily targets calculated
    for that date.
    """

    return {
        row['Date']: row
        for row in target_rows
        if row.get('Date') is not None
    }


# =========================================================
# HISTORICAL FEATURES
# =========================================================

def _add_history_features(
    sample,
    historical_rows,
):
    """
    Add historical feature rows to a training sample.

    The historical rows are prefixed with their relative
    position:

        History_1_*
        History_2_*
        ...

    The most recent historical row is History_1.

    Therefore:

        History_1 = immediately previous observed row
        History_2 = second previous observed row
        ...
    """

    # -----------------------------------------------------
    # Reverse the rows so History_1 is the most recent.
    # -----------------------------------------------------

    historical_rows = list(
        reversed(
            historical_rows
        )
    )

    for history_index, historical_row in enumerate(
        historical_rows,
        start=1,
    ):

        historical_features = _remove_date(
            historical_row
        )

        for feature_name, value in (
            historical_features.items()
        ):

            sample[
                f'History_{history_index}_{feature_name}'
            ] = value


# =========================================================
# FUTURE TARGET HELPERS
# =========================================================

def _is_binary_target(target_name):
    """
    Determine whether a target behaves like a binary label.

    Binary targets are aggregated differently from continuous
    or categorical targets.
    """

    return (
        target_name != 'Target_Location'
    )


def _aggregate_future_target(
    target_name,
    future_target_rows,
):
    """
    Aggregate one daily target across a future horizon.

    Binary targets:

        0, 0, 1, 0
            ↓
        1

    Meaning:

        The event happened at least once during the
        forecast horizon.

    Target_Location:

        The latest known future location is retained.

    Other target types are treated conservatively as
    "occurred at least once" when they are non-zero.
    """

    if not future_target_rows:
        return None

    # -----------------------------------------------------
    # Location
    # -----------------------------------------------------

    if target_name == 'Target_Location':

        for row in reversed(
            future_target_rows
        ):

            value = row.get(
                target_name
            )

            if value not in (
                None,
                '',
            ):

                return value

        return None

    # -----------------------------------------------------
    # Binary / event targets
    # -----------------------------------------------------

    values = []

    for row in future_target_rows:

        value = row.get(
            target_name
        )

        if value is None:
            continue

        try:
            numeric_value = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

        values.append(
            numeric_value
        )

    if not values:
        return 0

    return int(
        any(
            value != 0
            for value in values
        )
    )


def _build_future_targets(
    anchor_date,
    target_lookup,
    horizon,
):
    """
    Build targets for a future calendar horizon.

    Example:

        anchor_date = 2026-08-03
        horizon = 7

    Future period:

        2026-08-04
        ...
        2026-08-10

    Only dates that actually exist in the database are
    considered observed future dates.

    Missing calendar dates are NOT treated as zero activity.
    """

    future_target_rows = []

    for day_offset in range(
        1,
        horizon + 1,
    ):

        future_date = (
            anchor_date
            + timedelta(
                days=day_offset
            )
        )

        target_row = target_lookup.get(
            future_date
        )

        if target_row is not None:

            future_target_rows.append(
                target_row
            )

    if not future_target_rows:
        return {}

    target_names = _get_target_names(
        future_target_rows
    )

    future_targets = {}

    for target_name in target_names:

        future_targets[
            f'{target_name}_{horizon}D'
        ] = _aggregate_future_target(
            target_name,
            future_target_rows,
        )

    return future_targets


# =========================================================
# TRAINING DATASET
# =========================================================

def build_training_dataset(
    history_size=HISTORY_SIZE,
    forecast_horizons=FORECAST_HORIZONS,
):
    """
    Build a genuinely future-oriented training dataset.

    Core relationship:

        Historical Features(T)
                    ↓
             Future Targets
                    ↓
        T+1 / T+7 / T+30

    IMPORTANT:

    The feature input contains only information available
    on or before the prediction anchor date.

    Future target rows are NEVER used as input features.

    --------------------------------------------------------
    Example
    --------------------------------------------------------

    Suppose the available dates are:

        2026-08-03
        2026-08-05
        2026-08-07
        2026-08-08
        ...

    For anchor date:

        2026-08-05

    the model input can contain:

        History_1 = 2026-08-03

    while the targets describe what happened after:

        2026-08-06 → 1D
        2026-08-06 ... 2026-08-12 → 7D
        2026-08-06 ... 2026-09-04 → 30D

    Missing dates are not invented.

    --------------------------------------------------------
    """

    if history_size < 1:
        raise ValueError(
            'history_size must be at least 1.'
        )

    if not forecast_horizons:
        raise ValueError(
            'forecast_horizons cannot be empty.'
        )

    # -----------------------------------------------------
    # Validate horizons
    # -----------------------------------------------------

    normalized_horizons = []

    for horizon in forecast_horizons:

        try:
            horizon = int(
                horizon
            )
        except (
            TypeError,
            ValueError,
        ):
            raise ValueError(
                'Forecast horizons must be integers.'
            )

        if horizon < 1:
            raise ValueError(
                'Forecast horizons must be at least 1 day.'
            )

        normalized_horizons.append(
            horizon
        )

    normalized_horizons = tuple(
        sorted(
            set(
                normalized_horizons
            )
        )
    )

    # -----------------------------------------------------
    # Load data
    # -----------------------------------------------------

    feature_rows = get_feature_dataset()
    target_rows = build_target_dataset()

    if not feature_rows or not target_rows:
        return []

    # -----------------------------------------------------
    # Sort chronologically
    # -----------------------------------------------------

    feature_rows = sorted(
        feature_rows,
        key=lambda row: row['Date'],
    )

    target_rows = sorted(
        target_rows,
        key=lambda row: row['Date'],
    )

    # -----------------------------------------------------
    # Build lookups
    # -----------------------------------------------------

    feature_lookup = _build_feature_lookup(
        feature_rows
    )

    target_lookup = _build_target_lookup(
        target_rows
    )

    # -----------------------------------------------------
    # Build samples
    # -----------------------------------------------------

    dataset = []

    # -----------------------------------------------------
    # The prediction anchor must have enough historical
    # observed rows before it.
    #
    # Example with HISTORY_SIZE = 7:
    #
    #     first 7 rows = history
    #     8th row       = first possible anchor
    #
    # -----------------------------------------------------

    for anchor_index in range(
        history_size,
        len(feature_rows),
    ):

        anchor_row = feature_rows[
            anchor_index
        ]

        anchor_date = anchor_row[
            'Date'
        ]

        # -------------------------------------------------
        # Historical rows
        # -------------------------------------------------

        historical_rows = feature_rows[
            anchor_index - history_size:
            anchor_index
        ]

        if len(
            historical_rows
        ) < history_size:

            continue

        # -------------------------------------------------
        # Create sample
        # -------------------------------------------------

        sample = {
            'Date': anchor_date,
        }

        # -------------------------------------------------
        # Historical features only
        # -------------------------------------------------

        _add_history_features(
            sample,
            historical_rows,
        )

        # -------------------------------------------------
        # Future targets
        # -------------------------------------------------

        has_future_target = False

        for horizon in normalized_horizons:

            future_targets = _build_future_targets(
                anchor_date,
                target_lookup,
                horizon,
            )

            if future_targets:

                has_future_target = True

                sample.update(
                    future_targets
                )

        # -------------------------------------------------
        # Do not create a training sample if there is no
        # observed future information at all.
        # -------------------------------------------------

        if not has_future_target:
            continue

        dataset.append(
            sample
        )

    return dataset


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def get_training_dataset():
    """
    Public entry point for the future-oriented training
    dataset.

    Returns samples where:

        Historical Features(T)
                ↓
        Future Targets(T+1 / T+7 / T+30)

    The Date field represents the prediction anchor date.
    """

    return build_training_dataset()
