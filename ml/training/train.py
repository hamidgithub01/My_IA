from ml.training.dataset import (
    prepare_model_dataset,
    validate_target_name,
    get_target_class_count,
)

from ml.targets.registry import (
    get_target_task,
)

from ml.models.forecasting import (
    create_forecasting_model,
    get_model_type,
)


# ==========================================================
# MODEL TRAINING
# ==========================================================


def train_target_model(
    target_name,
):
    """
    Train a machine-learning model for one selected target.

    Architecture:

        Target Name
             ↓
        Target Registry
             ↓
        Target Task
             ↓
        Model Dataset
             ↓
        Target Type / Class Count
             ↓
        Forecasting Model Factory
             ↓
        Model Training
             ↓
        Unified Training Result

    Supported target tasks:

        regression
        classification
        categorical

    Supported model families:

        regression
        classification
        multiclass
    """

    # ------------------------------------------------------
    # Validate target
    # ------------------------------------------------------

    validate_target_name(
        target_name
    )

    # ------------------------------------------------------
    # Determine target task from Registry
    #
    # The Registry is the single source of truth for the
    # machine-learning task assigned to the target.
    # ------------------------------------------------------

    target_task = get_target_task(
        target_name
    )

    # ------------------------------------------------------
    # Prepare the supervised dataset
    #
    # The selected target is explicitly passed to the
    # Training Dataset Pipeline.
    # ------------------------------------------------------

    dataset = prepare_model_dataset(
        target_name=target_name
    )

    # ------------------------------------------------------
    # Basic dataset validation
    # ------------------------------------------------------

    if not dataset:
        raise ValueError(
            'Model dataset could not be created.'
        )

    X_train = dataset.get(
        'X_train',
        []
    )

    y_train = dataset.get(
        'y_train',
        []
    )

    X_test = dataset.get(
        'X_test',
        []
    )

    y_test = dataset.get(
        'y_test',
        []
    )

    feature_names = dataset.get(
        'feature_names',
        []
    )

    training_data = dataset.get(
        'training_data',
        []
    )

    test_data = dataset.get(
        'test_data',
        []
    )

    validation_report = dataset.get(
        'validation_report',
        {}
    )

    # ------------------------------------------------------
    # Ensure the dataset actually corresponds to the target
    # requested by the caller.
    # ------------------------------------------------------

    dataset_target_name = dataset.get(
        'target_name'
    )

    if dataset_target_name != target_name:

        raise ValueError(
            'Dataset target does not match the requested '
            f'target.\n'
            f'Requested: {target_name}\n'
            f'Dataset: {dataset_target_name}'
        )

    # ------------------------------------------------------
    # Training data checks
    # ------------------------------------------------------

    if not X_train:
        raise ValueError(
            f'No training features are available for '
            f'target: {target_name}'
        )

    if not y_train:
        raise ValueError(
            f'No training targets are available for '
            f'target: {target_name}'
        )

    if len(X_train) != len(y_train):

        raise ValueError(
            'Training features and targets have '
            'different lengths.'
        )

    if len(X_train) < 2:

        raise ValueError(
            'At least two historical records are required '
            f'for training target: {target_name}'
        )

    if not feature_names:

        raise ValueError(
            f'No features are available for target: '
            f'{target_name}'
        )

    # ------------------------------------------------------
    # Determine target data type
    #
    # The Registry defines the task.
    #
    # The Dataset defines the actual representation.
    #
    # Regression:
    #     numeric
    #
    # Classification:
    #     categorical
    #
    # Categorical:
    #     categorical
    # ------------------------------------------------------

    if target_task == 'regression':

        target_type = 'numeric'

    elif target_task in (
        'classification',
        'categorical',
    ):

        target_type = 'categorical'

    else:

        raise ValueError(
            f'Unsupported target task: '
            f'{target_task}'
        )

    # ------------------------------------------------------
    # Determine class count
    #
    # Regression does not require classes.
    # Classification / categorical targets do.
    # ------------------------------------------------------

    class_count = None

    if target_type == 'categorical':

        class_count = get_target_class_count(
            dataset['dataset'],
            target_name,
        )

        if class_count < 2:

            raise ValueError(
                f'Target "{target_name}" does not contain '
                'enough distinct classes for classification. '
                f'Found: {class_count}'
            )

    # ------------------------------------------------------
    # Determine model family
    #
    # Forecasting layer remains responsible for the actual
    # model-family decision.
    # ------------------------------------------------------

    model_type = get_model_type(
        target_type=target_type,
        class_count=class_count,
    )

    # ------------------------------------------------------
    # Create model
    # ------------------------------------------------------

    model = create_forecasting_model(
        target_type=target_type,
        class_count=class_count,
    )

    if model is None:

        raise ValueError(
            f'Unable to create model for target: '
            f'{target_name}'
        )

    # ------------------------------------------------------
    # Train model
    # ------------------------------------------------------

    model.fit(
        X_train,
        y_train,
    )

    # ------------------------------------------------------
    # Determine classes
    #
    # LinearRegression does not have classes_.
    #
    # LogisticRegression does.
    # ------------------------------------------------------

    classes = None

    if hasattr(
        model,
        'classes_',
    ):

        classes = (
            model.classes_.tolist()
            if hasattr(
                model.classes_,
                'tolist',
            )
            else list(
                model.classes_
            )
        )

    # ------------------------------------------------------
    # Model algorithm
    # ------------------------------------------------------

    algorithm = (
        model.__class__.__name__
    )

    # ------------------------------------------------------
    # Unified Training Result
    # ------------------------------------------------------

    return {

        # --------------------------------------------------
        # Core model
        # --------------------------------------------------

        'model':
            model,

        # --------------------------------------------------
        # Target information
        # --------------------------------------------------

        'target_name':
            target_name,

        'target_task':
            target_task,

        'target_type':
            target_type,

        # --------------------------------------------------
        # Model information
        # --------------------------------------------------

        'model_type':
            model_type,

        'algorithm':
            algorithm,

        'class_count':
            class_count,

        'classes':
            classes,

        # --------------------------------------------------
        # Feature information
        # --------------------------------------------------

        'feature_names':
            feature_names,

        # --------------------------------------------------
        # Dataset information
        # --------------------------------------------------

        'training_rows':
            len(X_train),

        'test_rows':
            len(X_test),

        'training_data':
            training_data,

        'test_data':
            test_data,

        # --------------------------------------------------
        # Training arrays
        # --------------------------------------------------

        'X_train':
            X_train,

        'y_train':
            y_train,

        'X_test':
            X_test,

        'y_test':
            y_test,

        # --------------------------------------------------
        # Dataset validation
        # --------------------------------------------------

        'validation_report':
            validation_report,
    }


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================


def train_model():
    """
    Backward-compatible training entry point.

    The historical default target remains:

        Target_Expense_Total_1D

    New code should use:

        train_target_model(target_name)
    """

    return train_target_model(
        'Target_Expense_Total_1D'
    )


# ==========================================================
# SIMPLE TEST
# ==========================================================


if __name__ == '__main__':

    print()
    print(
        '========== TARGET MODEL TRAINING TEST =========='
    )

    target_name = (
        'Target_Expense_Total_1D'
    )

    print(
        f'Target: {target_name}'
    )

    result = train_target_model(
        target_name
    )

    print()
    print(
        '========== TRAINING SUMMARY =========='
    )

    print(
        'Target:',
        result['target_name']
    )

    print(
        'Target task:',
        result['target_task']
    )

    print(
        'Target type:',
        result['target_type']
    )

    print(
        'Model type:',
        result['model_type']
    )

    print(
        'Algorithm:',
        result['algorithm']
    )

    print(
        'Class count:',
        result['class_count']
    )

    print(
        'Classes:',
        result['classes']
    )

    print(
        'Training rows:',
        result['training_rows']
    )

    print(
        'Test rows:',
        result['test_rows']
    )

    print(
        'Feature count:',
        len(
            result['feature_names']
        )
    )

    print()
    print(
        '========== TARGET MODEL TRAINING TEST PASSED =========='
    )