import pytest

from ml.training.train import train_model
from ml.evaluation.evaluate import evaluate_model


# ==========================================================
# MODEL TRAINING
# ==========================================================

def test_model_training():
    """
    Verify that the complete training pipeline executes
    successfully and returns a valid training result.
    """

    training_result = train_model()

    assert training_result is not None
    assert isinstance(training_result, dict)

    assert "model" in training_result
    assert "training_rows" in training_result
    assert "feature_names" in training_result

    assert training_result["training_rows"] > 0
    assert len(training_result["feature_names"]) > 0

    model = training_result["model"]

    assert model is not None
    assert hasattr(model, "intercept_")
    assert hasattr(model, "coef_")

    print()
    print("========== MODEL TRAINING TEST ==========")
    print()
    print("Training completed successfully.")
    print(
        f"Training rows: "
        f"{training_result['training_rows']}"
    )
    print(
        f"Feature count: "
        f"{len(training_result['feature_names'])}"
    )
    print(
        f"Algorithm: "
        f"{model.__class__.__name__}"
    )

    print()
    print("========== MODEL PARAMETERS ==========")

    print(
        f"Intercept: "
        f"{float(model.intercept_)}"
    )

    print()
    print("Coefficients:")

    for feature, coefficient in zip(
        training_result["feature_names"],
        model.coef_,
    ):
        print(
            f"{feature}: "
            f"{float(coefficient)}"
        )


# ==========================================================
# CHRONOLOGICAL EVALUATION
# ==========================================================

def test_chronological_evaluation():
    """
    Verify chronological evaluation using the actual
    training result produced by the training pipeline.
    """

    training_result = train_model()

    assert training_result is not None

    print()
    print("========== CHRONOLOGICAL EVALUATION ==========")

    try:
        evaluation_result = evaluate_model(
            training_result=training_result,
            test_ratio=0.2,
            min_test_rows=2,
        )

    except ValueError as error:
        pytest.fail(
            f"Chronological evaluation failed unexpectedly: {error}"
        )

    assert evaluation_result is not None
    assert isinstance(evaluation_result, dict)

    assert "training_rows" in evaluation_result
    assert "testing_rows" in evaluation_result
    assert "metrics" in evaluation_result
    assert "testing_dates" in evaluation_result
    assert "actual_values" in evaluation_result
    assert "predicted_values" in evaluation_result

    assert evaluation_result["training_rows"] > 0
    assert evaluation_result["testing_rows"] >= 2

    metrics = evaluation_result["metrics"]

    assert "mae" in metrics
    assert "rmse" in metrics
    assert "r_squared" in metrics

    assert metrics["mae"] >= 0
    assert metrics["rmse"] >= 0

    print()
    print(
        f"Training rows: "
        f"{evaluation_result['training_rows']}"
    )

    print(
        f"Testing rows: "
        f"{evaluation_result['testing_rows']}"
    )

    print()
    print(
        f"MAE: "
        f"{metrics['mae']:.4f}"
    )

    print(
        f"RMSE: "
        f"{metrics['rmse']:.4f}"
    )

    r_squared = metrics.get("r_squared")

    if r_squared is None:
        print(
            "R²: unavailable "
            "(insufficient target variation)"
        )
    else:
        print(
            f"R²: "
            f"{r_squared:.4f}"
        )

    evaluation_status = evaluation_result.get(
        "evaluation_status"
    )

    evaluation_valid = evaluation_result.get(
        "evaluation_valid"
    )

    if evaluation_status is not None:
        print()
        print(
            f"Evaluation status: "
            f"{evaluation_status}"
        )

        print(
            f"Evaluation valid: "
            f"{evaluation_valid}"
        )


# ==========================================================
# TARGET VALIDATION
# ==========================================================

def test_training_target_information():
    """
    Verify that target information is preserved by
    chronological evaluation.
    """

    training_result = train_model()

    evaluation_result = evaluate_model(
        training_result=training_result,
        test_ratio=0.2,
        min_test_rows=2,
    )

    print()
    print("========== TRAINING TARGET ==========")

    training_target_values = evaluation_result.get(
        "training_target_values"
    )

    training_target_unique_values = evaluation_result.get(
        "training_target_unique_values"
    )

    training_target_has_variation = evaluation_result.get(
        "training_target_has_variation"
    )

    if training_target_values is not None:

        print(
            f"Training target values: "
            f"{training_target_values}"
        )

        print(
            f"Unique target values: "
            f"{training_target_unique_values}"
        )

        print(
            f"Target variation: "
            f"{training_target_has_variation}"
        )

        assert training_target_unique_values is not None
        assert isinstance(training_target_unique_values, list)
        assert len(training_target_unique_values) >= 1

        assert training_target_has_variation is False
        assert training_target_unique_values == [0.0]


# ==========================================================
# TESTING PERIOD
# ==========================================================

def test_testing_period_and_predictions():
    """
    Verify chronological testing dates and the
    actual-vs-predicted output.
    """

    training_result = train_model()

    evaluation_result = evaluate_model(
        training_result=training_result,
        test_ratio=0.2,
        min_test_rows=2,
    )

    testing_dates = evaluation_result["testing_dates"]
    actual_values = evaluation_result["actual_values"]
    predicted_values = evaluation_result["predicted_values"]

    assert len(testing_dates) > 0

    assert len(testing_dates) == len(actual_values)
    assert len(testing_dates) == len(predicted_values)

    print()
    print("========== TESTING PERIOD ==========")

    for testing_date in testing_dates:
        print(testing_date)

    print()
    print("========== ACTUAL vs PREDICTED ==========")

    for date_value, actual, predicted in zip(
        testing_dates,
        actual_values,
        predicted_values,
    ):
        print(
            f"{date_value} | "
            f"Actual: {actual:.2f} | "
            f"Predicted: {predicted:.2f}"
        )


# ==========================================================
# FINAL INTEGRATION TEST
# ==========================================================

def test_full_training_evaluation_integration():
    """
    Full integration test:

    Training
        ↓
    Training Result
        ↓
    Chronological Evaluation
        ↓
    Metrics
        ↓
    Predictions
    """

    print()
    print("========== FULL TRAINING + EVALUATION INTEGRATION ==========")

    training_result = train_model()

    assert training_result is not None
    assert training_result["training_rows"] > 0
    assert len(training_result["feature_names"]) > 0

    evaluation_result = evaluate_model(
        training_result=training_result,
        test_ratio=0.2,
        min_test_rows=2,
    )

    assert evaluation_result is not None

    assert evaluation_result["training_rows"] > 0
    assert evaluation_result["testing_rows"] >= 2

    assert len(
        evaluation_result["testing_dates"]
    ) == evaluation_result["testing_rows"]

    assert len(
        evaluation_result["actual_values"]
    ) == evaluation_result["testing_rows"]

    assert len(
        evaluation_result["predicted_values"]
    ) == evaluation_result["testing_rows"]

    metrics = evaluation_result["metrics"]

    assert metrics["mae"] >= 0
    assert metrics["rmse"] >= 0

    print()
    print("Training: PASS")
    print("Chronological evaluation: PASS")
    print("Metrics: PASS")
    print("Predictions: PASS")

    print()
    print("========== TEST RESULT ==========")
    print(
        "PASS: Full training and evaluation "
        "integration executed successfully."
    )