from sklearn.linear_model import LinearRegression

from ml.training.dataset import (
    prepare_model_dataset,
)


# ==========================================================
# MODEL TRAINING
# ==========================================================

def train_model():
    """
    Train the financial forecasting model.

    Training pipeline:

        Prepared historical dataset
                    ↓
            Temporal train/test split
                    ↓
                X_train / y_train
                    ↓
            LinearRegression
                    ↓
                Trained model

    Important:

        Target_Expense_Total is the value that the model
        learns to predict.

        A target value of 0.0 is a valid real observation.
        It means that no expense occurred on that day.

        The target is NEVER included in the input features.

        Date is also excluded from the model inputs.
    """

    # ------------------------------------------------------
    # Prepare the complete model dataset
    #
    # This guarantees that training uses the same
    # chronological dataset construction and validation
    # rules used by the ML pipeline.
    # ------------------------------------------------------

    dataset = prepare_model_dataset()

    X_train = dataset['X_train']
    y_train = dataset['y_train']

    feature_names = dataset['feature_names']
    target_name = dataset['target_name']

    # ------------------------------------------------------
    # Basic safety checks
    # ------------------------------------------------------

    if not X_train:
        raise ValueError(
            'No training features are available.'
        )

    if not y_train:
        raise ValueError(
            'No training targets are available.'
        )

    if len(X_train) != len(y_train):
        raise ValueError(
            'Training features and targets have '
            'different lengths.'
        )

    if len(X_train) < 2:
        raise ValueError(
            'At least two historical records are required '
            'for training.'
        )

    if not feature_names:
        raise ValueError(
            'No features available for training.'
        )

    # ------------------------------------------------------
    # Train model
    # ------------------------------------------------------

    model = LinearRegression()

    model.fit(
        X_train,
        y_train,
    )

    # ------------------------------------------------------
    # Return complete training result
    # ------------------------------------------------------

    return {
        'model': model,

        'feature_names':
            feature_names,

        'training_rows':
            len(X_train),

        'target_name':
            target_name,

        'training_data':
            dataset['training_data'],

        'test_data':
            dataset['test_data'],

        'X_train':
            X_train,

        'y_train':
            y_train,

        'X_test':
            dataset['X_test'],

        'y_test':
            dataset['y_test'],

        'validation_report':
            dataset['validation_report'],
    }