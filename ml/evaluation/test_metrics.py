from ml.evaluation.metrics import (
    calculate_metrics,
    calculate_classification_metrics,
)


# ==========================================================
# REGRESSION TEST
# ==========================================================

def test_regression_metrics():

    print()
    print('========== REGRESSION METRICS TEST ==========')

    # Synthetic regression data
    y_true = [
        100.0,
        200.0,
        300.0,
        400.0,
        500.0,
    ]

    y_pred = [
        110.0,
        190.0,
        310.0,
        380.0,
        520.0,
    ]

    result = calculate_metrics(
        y_true,
        y_pred,
    )

    print()
    print('Regression result:')
    print(result)

    # ------------------------------------------------------
    # Structural validation
    # ------------------------------------------------------

    assert 'mae' in result
    assert 'rmse' in result
    assert 'r_squared' in result

    # ------------------------------------------------------
    # Basic validity
    # ------------------------------------------------------

    assert result['mae'] >= 0
    assert result['rmse'] >= 0

    assert result['r_squared'] is not None

    # ------------------------------------------------------
    # Known values
    # ------------------------------------------------------

    expected_mae = 14.0
    expected_rmse = (
        (
            10 ** 2
            + 10 ** 2
            + 10 ** 2
            + 20 ** 2
            + 20 ** 2
        ) / 5
    ) ** 0.5

    assert abs(
        result['mae']
        - expected_mae
    ) < 1e-9

    assert abs(
        result['rmse']
        - expected_rmse
    ) < 1e-9

    print()
    print('Regression metrics: PASSED')


# ==========================================================
# BINARY CLASSIFICATION TEST
# ==========================================================

def test_binary_classification_metrics():

    print()
    print(
        '========== BINARY CLASSIFICATION TEST =========='
    )

    # Synthetic binary classification data
    #
    # 0 = negative
    # 1 = positive
    #
    # Actual:
    #
    # 0  0  0  0  1  1  1  1
    #
    # Predicted:
    #
    # 0  0  1  0  1  1  0  1
    #
    # Therefore:
    #
    # TN = 3
    # FP = 1
    # FN = 1
    # TP = 3

    y_true = [
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
    ]

    y_pred = [
        0,
        0,
        1,
        0,
        1,
        1,
        0,
        1,
    ]

    result = calculate_classification_metrics(
        y_true,
        y_pred,
        average='binary',
    )

    print()
    print('Binary classification result:')
    print(result)

    # ------------------------------------------------------
    # Structural validation
    # ------------------------------------------------------

    assert 'accuracy' in result
    assert 'precision' in result
    assert 'recall' in result
    assert 'f1' in result

    # ------------------------------------------------------
    # Expected values
    # ------------------------------------------------------

    expected_accuracy = 6 / 8
    expected_precision = 3 / 4
    expected_recall = 3 / 4
    expected_f1 = 0.75

    assert abs(
        result['accuracy']
        - expected_accuracy
    ) < 1e-9

    assert abs(
        result['precision']
        - expected_precision
    ) < 1e-9

    assert abs(
        result['recall']
        - expected_recall
    ) < 1e-9

    assert abs(
        result['f1']
        - expected_f1
    ) < 1e-9

    print()
    print(
        'Binary classification metrics: PASSED'
    )


# ==========================================================
# MULTICLASS CLASSIFICATION TEST
# ==========================================================

def test_multiclass_metrics():

    print()
    print(
        '========== MULTICLASS CLASSIFICATION TEST =========='
    )

    # Synthetic multiclass data
    #
    # Classes:
    #
    # 0 = Low
    # 1 = Medium
    # 2 = High

    y_true = [
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

    y_pred = [
        0,
        0,
        1,
        1,
        1,
        2,
        2,
        0,
        2,
    ]

    result = calculate_classification_metrics(
        y_true,
        y_pred,
        average='weighted',
    )

    print()
    print('Multiclass result:')
    print(result)

    # ------------------------------------------------------
    # Structural validation
    # ------------------------------------------------------

    assert 'accuracy' in result
    assert 'precision' in result
    assert 'recall' in result
    assert 'f1' in result

    # ------------------------------------------------------
    # Basic validity
    # ------------------------------------------------------

    assert 0 <= result['accuracy'] <= 1
    assert 0 <= result['precision'] <= 1
    assert 0 <= result['recall'] <= 1
    assert 0 <= result['f1'] <= 1

    # ------------------------------------------------------
    # Expected accuracy
    #
    # Correct:
    #
    # 0 -> 0
    # 0 -> 0
    # 1 -> 1
    # 1 -> 1
    # 2 -> 2
    # 2 -> 2
    #
    # Total = 6 / 9
    # ------------------------------------------------------

    expected_accuracy = 6 / 9

    assert abs(
        result['accuracy']
        - expected_accuracy
    ) < 1e-9

    print()
    print(
        'Multiclass metrics: PASSED'
    )


# ==========================================================
# INVALID INPUT TESTS
# ==========================================================

def test_invalid_inputs():

    print()
    print(
        '========== INVALID INPUT TEST =========='
    )

    # ------------------------------------------------------
    # Empty regression data
    # ------------------------------------------------------

    try:

        calculate_metrics(
            [],
            [],
        )

        raise AssertionError(
            'Empty regression data should fail.'
        )

    except ValueError:

        pass

    # ------------------------------------------------------
    # Different lengths
    # ------------------------------------------------------

    try:

        calculate_metrics(
            [1, 2, 3],
            [1, 2],
        )

        raise AssertionError(
            'Different lengths should fail.'
        )

    except ValueError:

        pass

    # ------------------------------------------------------
    # Classification with only one class
    # ------------------------------------------------------

    try:

        calculate_classification_metrics(
            [0, 0, 0],
            [0, 0, 0],
            average='binary',
        )

        raise AssertionError(
            'Single-class target should fail.'
        )

    except ValueError:

        pass

    # ------------------------------------------------------
    # Different classification lengths
    # ------------------------------------------------------

    try:

        calculate_classification_metrics(
            [0, 1, 0],
            [0, 1],
            average='binary',
        )

        raise AssertionError(
            'Different lengths should fail.'
        )

    except ValueError:

        pass

    print()
    print(
        'Invalid input handling: PASSED'
    )


# ==========================================================
# MAIN TEST
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )
    print(
        '          METRICS MODULE TEST SUITE'
    )
    print(
        '=================================================='
    )

    test_regression_metrics()

    test_binary_classification_metrics()

    test_multiclass_metrics()

    test_invalid_inputs()

    print()
    print(
        '=================================================='
    )
    print(
        '          ALL METRICS TESTS PASSED'
    )
    print(
        '=================================================='
    )