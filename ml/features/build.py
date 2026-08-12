from ml.preparation.preparation import (
    get_prepared_dataset,
)

from ml.features.behavioral import (
    create_behavioral_features,
)

from ml.features.financial import (
    create_financial_features,
)

from ml.features.temporal import (
    create_temporal_features,
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
        Financial Features
        Temporal Features
            ↓
        Final Feature Dataset
    """

    prepared_data = get_prepared_dataset()

    feature_dataset = []

    for row in prepared_data:

        features = {
            'Date': row['Date'],
        }

        features.update(
            create_behavioral_features(row)
        )

        features.update(
            create_financial_features(row)
        )

        features.update(
            create_temporal_features(row)
        )

        feature_dataset.append(features)

    return feature_dataset