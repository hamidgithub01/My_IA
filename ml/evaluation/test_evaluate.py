from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression

from ml.evaluation.evaluate import (
    evaluate_model,
    EVALUATION_VALID,
    EVALUATION_INSUFFICIENT_TRAINING_VARIATION,
    EVALUATION_INSUFFICIENT_CLASSES,
)


# ==========================================================
# REGRESSION TEST
# ==========================================================

def test_regression_evaluation():

    print()
    print(
        '========== REGRESSION EVALUATION TEST =========='
    )

    # ------------------------------------------------------
    # Synthetic training data
    # ------------------------------------------------------

    X_train = [
        [1.0],
        [2.0],
        [3.0],
        [4.0],
        [5.0],
        [6.0],
        [7.0],
        [8.0],
    ]

    y_train = [
        10.0,
        20.0,
        30.0,
        40.0,
        50.0,
        60.0,
        70.0,
        80.0,
    ]

    # ------------------------------------------------------
    # Synthetic unseen test data
    # ------------------------------------------------------

    X_test = [
        [9.0],
        [10.0],
    ]

    y_test = [
        90.0,
        100.0,
    ]

    # ------------------------------------------------------
    # Train synthetic model
    # ------------------------------------------------------

    model = LinearRegression()

    model.fit(
        X_train,
        y_train,
    )

    # ------------------------------------------------------
    # Unified training result
    # ------------------------------------------------------

    training_result = {

        'model':
            model,

        'target_name':
            'Target_Expense_Total_1D',

        'target_task':
            'regression',

        'target_type':
            'numeric',

        'model_type':
            'regression',

        'algorithm':
            'LinearRegression',

        'class_count':
            None,

        'classes':
            None,

        'feature_names': [
            'Feature_1',
        ],

        'training_rows':
            len(X_train),

        'test_rows':
            len(X_test),

        'X_train':
            X_train,

        'y_train':
            y_train,

        'X_test':
            X_test,

        'y_test':
            y_test,

        'training_data': [],

        'test_data': [],

        'validation_report': {},
    }

    # ------------------------------------------------------
    # Evaluate
    # ------------------------------------------------------

    result = evaluate_model(
        training_result
    )

    print()
    print(
        'Regression result:'
    )

    print(
        result
    )

    # ------------------------------------------------------
    # Assertions
    # ------------------------------------------------------

    assert (
        result['evaluation_status']
        == EVALUATION_VALID
    )

    assert (
        result['evaluation_valid']
        is True
    )

    assert (
        abs(
            result['metrics']['mae']
        )
        < 1e-9
    )

    assert (
        abs(
            result['metrics']['rmse']
        )
        < 1e-9
    )

    assert (
        abs(
            result['metrics']['r_squared']
            - 1.0
        )
        < 1e-9
    )

    assert (
        result['training_rows']
        == 8
    )

    assert (
        result['testing_rows']
        == 2
    )

    assert (
        result['actual_values']
        == [90.0, 100.0]
    )

    assert len(
        result['predicted_values']
    ) == 2

    assert all(
        abs(
            actual - expected
        ) < 1e-9
        for actual, expected in zip(
            result['predicted_values'],
            [90.0, 100.0],
        )
    )

    print()
    print(
        'Regression evaluation: PASSED'
    )


# ==========================================================
# BINARY CLASSIFICATION TEST
# ==========================================================

def test_binary_classification_evaluation():

    print()
    print(
        '========== BINARY CLASSIFICATION TEST =========='
    )

    # ------------------------------------------------------
    # Synthetic data
    # ------------------------------------------------------

    X_train = [
        [1.0],
        [2.0],
        [3.0],
        [4.0],
        [5.0],
        [6.0],
        [7.0],
        [8.0],
    ]

    y_train = [
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
    ]

    X_test = [
        [1.5],
        [3.5],
        [5.5],
        [7.5],
    ]

    y_test = [
        0,
        0,
        1,
        1,
    ]

    # ------------------------------------------------------
    # Train model
    # ------------------------------------------------------

    model = LogisticRegression()

    model.fit(
        X_train,
        y_train,
    )

    training_result = {

        'model':
            model,

        'target_name':
            'Target_Working_Day_1D',

        'target_task':
            'classification',

        'target_type':
            'categorical',

        'model_type':
            'classification',

        'algorithm':
            'LogisticRegression',

        'class_count':
            2,

        'classes':
            [0, 1],

        'feature_names': [
            'Feature_1',
        ],

        'training_rows':
            len(X_train),

        'test_rows':
            len(X_test),

        'X_train':
            X_train,

        'y_train':
            y_train,

        'X_test':
            X_test,

        'y_test':
            y_test,

        'training_data': [],

        'test_data': [],

        'validation_report': {},
    }

    # ------------------------------------------------------
    # Evaluate
    # ------------------------------------------------------

    result = evaluate_model(
        training_result
    )

    print()
    print(
        'Binary classification result:'
    )

    print(
        result
    )

    # ------------------------------------------------------
    # Assertions
    # ------------------------------------------------------

    assert (
        result['evaluation_status']
        == EVALUATION_VALID
    )

    assert (
        result['evaluation_valid']
        is True
    )

    assert (
        'accuracy'
        in result['metrics']
    )

    assert (
        'precision'
        in result['metrics']
    )

    assert (
        'recall'
        in result['metrics']
    )

    assert (
        'f1'
        in result['metrics']
    )

    assert (
        0.0
        <= result['metrics']['accuracy']
        <= 1.0
    )

    print()
    print(
        'Binary classification evaluation: PASSED'
    )


# ==========================================================
# MULTICLASS TEST
# ==========================================================

def test_multiclass_evaluation():

    print()
    print(
        '========== MULTICLASS CLASSIFICATION TEST =========='
    )

    # ------------------------------------------------------
    # Synthetic three-class data
    # ------------------------------------------------------

    X_train = [
        [1.0],
        [2.0],
        [3.0],

        [5.0],
        [6.0],
        [7.0],

        [9.0],
        [10.0],
        [11.0],
    ]

    y_train = [
        0,
        0,
        0,

        1,
        1,
        1,

        2,
        2,
        2,
    ]

    X_test = [
        [1.5],
        [5.5],
        [9.5],
    ]

    y_test = [
        0,
        1,
        2,
    ]

    # ------------------------------------------------------
    # Train multiclass LogisticRegression
    # ------------------------------------------------------

    model = LogisticRegression(
        max_iter=1000,
    )

    model.fit(
        X_train,
        y_train,
    )

    training_result = {

        'model':
            model,

        'target_name':
            'Target_Location_1D',

        'target_task':
            'categorical',

        'target_type':
            'categorical',

        'model_type':
            'multiclass',

        'algorithm':
            'LogisticRegression',

        'class_count':
            3,

        'classes':
            [0, 1, 2],

        'feature_names': [
            'Feature_1',
        ],

        'training_rows':
            len(X_train),

        'test_rows':
            len(X_test),

        'X_train':
            X_train,

        'y_train':
            y_train,

        'X_test':
            X_test,

        'y_test':
            y_test,

        'training_data': [],

        'test_data': [],

        'validation_report': {},
    }

    # ------------------------------------------------------
    # Evaluate
    # ------------------------------------------------------

    result = evaluate_model(
        training_result
    )

    print()
    print(
        'Multiclass result:'
    )

    print(
        result
    )

    # ------------------------------------------------------
    # Assertions
    # ------------------------------------------------------

    assert (
        result['evaluation_status']
        == EVALUATION_VALID
    )

    assert (
        result['evaluation_valid']
        is True
    )

    assert (
        'accuracy'
        in result['metrics']
    )

    assert (
        'precision'
        in result['metrics']
    )

    assert (
        'recall'
        in result['metrics']
    )

    assert (
        'f1'
        in result['metrics']
    )

    assert (
        0.0
        <= result['metrics']['accuracy']
        <= 1.0
    )

    print()
    print(
        'Multiclass evaluation: PASSED'
    )


# ==========================================================
# INSUFFICIENT TRAINING VARIATION
# ==========================================================

def test_insufficient_training_variation():

    print()
    print(
        '========== INSUFFICIENT VARIATION TEST =========='
    )

    X_train = [
        [1.0],
        [2.0],
        [3.0],
        [4.0],
    ]

    y_train = [
        50.0,
        50.0,
        50.0,
        50.0,
    ]

    X_test = [
        [5.0],
        [6.0],
    ]

    y_test = [
        50.0,
        50.0,
    ]

    model = LinearRegression()

    model.fit(
        X_train,
        y_train,
    )

    training_result = {

        'model':
            model,

        'target_name':
            'Target_Expense_Total_1D',

        'target_task':
            'regression',

        'target_type':
            'numeric',

        'model_type':
            'regression',

        'algorithm':
            'LinearRegression',

        'class_count':
            None,

        'classes':
            None,

        'feature_names': [
            'Feature_1',
        ],

        'training_rows':
            4,

        'test_rows':
            2,

        'X_train':
            X_train,

        'y_train':
            y_train,

        'X_test':
            X_test,

        'y_test':
            y_test,

        'training_data': [],

        'test_data': [],

        'validation_report': {},
    }

    result = evaluate_model(
        training_result
    )

    print()
    print(
        'Result:'
    )

    print(
        result
    )

    assert (
        result['evaluation_status']
        == EVALUATION_INSUFFICIENT_TRAINING_VARIATION
    )

    assert (
        result['evaluation_valid']
        is False
    )

    assert (
        result['training_target_unique_count']
        == 1
    )

    assert (
        result['training_target_has_variation']
        is False
    )

    assert (
        result['metrics']['r_squared']
        is None
    )

    print()
    print(
        'Insufficient variation handling: PASSED'
    )


# ==========================================================
# INSUFFICIENT CLASSES TEST
# ==========================================================

def test_insufficient_classes():

    print()
    print(
        '========== INSUFFICIENT CLASSES TEST =========='
    )

    X_train = [
        [1.0],
        [2.0],
        [3.0],
        [4.0],
    ]

    y_train = [
        1,
        1,
        1,
        1,
    ]

    X_test = [
        [5.0],
        [6.0],
    ]

    y_test = [
        1,
        1,
    ]

    model = LogisticRegression()

    # We intentionally DO NOT fit the model because
    # one class is insufficient for LogisticRegression.

    training_result = {

        'model':
            model,

        'target_name':
            'Target_Working_Day_1D',

        'target_task':
            'classification',

        'target_type':
            'categorical',

        'model_type':
            'classification',

        'algorithm':
            'LogisticRegression',

        'class_count':
            1,

        'classes':
            [1],

        'feature_names': [
            'Feature_1',
        ],

        'training_rows':
            4,

        'test_rows':
            2,

        'X_train':
            X_train,

        'y_train':
            y_train,

        'X_test':
            X_test,

        'y_test':
            y_test,

        'training_data': [],

        'test_data': [],

        'validation_report': {},
    }

    try:

        result = evaluate_model(
            training_result
        )

        # If evaluation does not raise, verify that
        # it reports insufficient classes.

        assert (
            result['evaluation_status']
            == EVALUATION_INSUFFICIENT_CLASSES
        )

        assert (
            result['evaluation_valid']
            is False
        )

    except ValueError:

        # This is also acceptable if the evaluation layer
        # explicitly rejects the invalid model state.

        pass

    print(
        'Insufficient class handling: PASSED'
    )


# ==========================================================
# TEST SUITE
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )

    print(
        '          EVALUATION MODULE TEST SUITE'
    )

    print(
        '=================================================='
    )

    test_regression_evaluation()

    test_binary_classification_evaluation()

    test_multiclass_evaluation()

    test_insufficient_training_variation()

    test_insufficient_classes()

    print()
    print(
        '=================================================='
    )

    print(
        '          ALL EVALUATION TESTS PASSED'
    )

    print(
        '=================================================='
    )