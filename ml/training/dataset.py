from ml.features.build import (
    build_training_dataset,
    get_feature_names,
)

from ml.preparation.validation import (
    validate_training_dataset,
)


# ==========================================================
# TEMPORAL SPLIT
# ==========================================================

def temporal_train_test_split(
    data,
    test_ratio=0.2,
):
    """
    Split a supervised dataset chronologically.

    Earlier observations are used for training.
    Later observations are used for testing.

    No random shuffling is performed.
    """

    if not data:
        return [], []

    data = sorted(
        data,
        key=lambda row: row['Date'],
    )

    if len(data) < 2:
        return data, []

    split_index = int(
        len(data) * (1 - test_ratio)
    )

    split_index = max(
        1,
        min(
            split_index,
            len(data) - 1,
        ),
    )

    training_data = data[
        :split_index
    ]

    test_data = data[
        split_index:
    ]

    return (
        training_data,
        test_data,
    )


# ==========================================================
# X / Y EXTRACTION
# ==========================================================

def split_features_and_target(
    data,
    target_name='Target_Expense_Total',
):
    """
    Convert dataset rows into model inputs X
    and target vector y.

    Date and Target_* columns are never included
    in X.
    """

    if not data:
        return [], []

    feature_names = get_feature_names(
        data
    )

    X = []
    y = []

    for row in data:

        X.append([
            row[name]
            for name in feature_names
        ])

        y.append(
            row[target_name]
        )

    return X, y


# ==========================================================
# COMPLETE MODEL DATASET
# ==========================================================

def prepare_model_dataset(
    target_name='Target_Expense_Total',
    test_ratio=0.2,
):
    """
    Build and prepare the complete model dataset.

    Pipeline:

        Feature Dataset
              ↓
        Validation
              ↓
        Temporal Split
              ↓
        X / y extraction
              ↓
        Training + Test datasets
    """

    data = build_training_dataset()

    validation_report = (
        validate_training_dataset(
            data
        )
    )

    if not validation_report[
        'ready_for_training'
    ]:

        raise ValueError(
            'Training dataset validation failed: '
            + '; '.join(
                validation_report['errors']
            )
        )

    training_data, test_data = (
        temporal_train_test_split(
            data,
            test_ratio,
        )
    )

    X_train, y_train = (
        split_features_and_target(
            training_data,
            target_name,
        )
    )

    X_test, y_test = (
        split_features_and_target(
            test_data,
            target_name,
        )
    )

    return {
        'X_train': X_train,
        'y_train': y_train,

        'X_test': X_test,
        'y_test': y_test,

        'training_data':
            training_data,

        'test_data':
            test_data,

        'feature_names':
            get_feature_names(data),

        'target_name':
            target_name,

        'validation_report':
            validation_report,
    }