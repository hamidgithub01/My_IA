from ml.preparation.preparation import (
    get_prepared_dataset,
)

from ml.features.behavioral import (
    create_behavioral_features,
)

from ml.features.contextual import (
    create_contextual_features,
)

from ml.features.financial import (
    create_financial_features,
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


def build_feature_dataset():
    """
    Build the final machine-learning feature dataset.

    Pipeline:

        Database
            ↓
        Data Preparation
            ↓
        Behavioral Features
        Contextual Features
        Financial Features
        Temporal Features
        History Features
        Lag Features
        Rolling Features
            ↓
        Final Feature Dataset
    """

    prepared_data = get_prepared_dataset()

    feature_dataset = []

    for index, row in enumerate(prepared_data):

        previous_rows = prepared_data[:index]

        features = {
            'Date': row['Date'],
        }

        # ==================================================
        # BEHAVIORAL FEATURES
        # ==================================================

        features.update(
            create_behavioral_features(row)
        )

        # ==================================================
        # CONTEXTUAL FEATURES
        # ==================================================

        features.update(
            create_contextual_features(row)
        )

        # ==================================================
        # FINANCIAL FEATURES
        # ==================================================

        features.update(
            create_financial_features(row)
        )

        # ==================================================
        # TEMPORAL FEATURES
        # ==================================================

        features.update(
            create_temporal_features(row)
        )

        # ==================================================
        # HISTORY FEATURES
        # ==================================================

        features.update(
            create_history_features(
                row,
                previous_rows,
            )
        )

        # ==================================================
        # LAG FEATURES
        # ==================================================

        features.update(
            create_lag_features(
                row,
                previous_rows,
            )
        )

        # ==================================================
        # ROLLING FEATURES
        # ==================================================

        features.update(
            create_rolling_features(
                row,
                previous_rows,
            )
        )

        feature_dataset.append(features)

    return feature_dataset