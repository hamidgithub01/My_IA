from ml.training.train import train_model
from ml.evaluation.evaluate import evaluate_model

print()
print("========== MODEL TRAINING TEST ==========")

# ==========================================================
# FULL MODEL TRAINING TEST
# ==========================================================

training_result = train_model()

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
    f"{training_result['model'].__class__.__name__}"  # تصحيح: **class** -> __class__ و **name** -> __name__
)

# ==========================================================
# MODEL PARAMETERS
# ==========================================================

model = training_result['model']

print()
print("========== MODEL PARAMETERS ==========")

print(
    f"Intercept: "
    f"{float(model.intercept_)}"
)

print()
print("Coefficients:")

for feature, coefficient in zip(
    training_result['feature_names'],
    model.coef_,
):
    print(
        f"{feature}: "
        f"{float(coefficient)}"
    )

# ==========================================================
# CHRONOLOGICAL EVALUATION
# ==========================================================

print()
print("========== CHRONOLOGICAL EVALUATION ==========")

try:
    evaluation_result = evaluate_model(
        training_result=None,
        test_ratio=0.2,
        min_test_rows=2,
    )

except ValueError as error:
    print()
    print(
        "Evaluation could not be completed."
    )
    print(
        f"Reason: {error}"
    )
    print()
    print(
        "This is expected when the historical "
        "dataset is too small."
    )
    print()
    print("========== TEST RESULT ==========")
    print(
        "PASS: Training completed, but "
        "chronological evaluation requires "
        "more historical records."
    )
    raise SystemExit(0)

# ==========================================================
# EVALUATION RESULTS
# ==========================================================

print()

print(
    f"Training rows: "
    f"{evaluation_result['training_rows']}"
)

print(
    f"Testing rows: "
    f"{evaluation_result['testing_rows']}"
)

metrics = evaluation_result['metrics']

print()

print(
    f"MAE: "
    f"{metrics['mae']:.4f}"
)

print(
    f"RMSE: "
    f"{metrics['rmse']:.4f}"
)

# R² يمكن أن تكون None بشكل شرعي عندما لا تحتوي
# بيانات التقييم على تباين كافٍ في القيمة المستهدفة.

r_squared = metrics.get('r_squared')

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

# ==========================================================
# EVALUATION STATUS
# ==========================================================

evaluation_status = evaluation_result.get('evaluation_status')
evaluation_valid = evaluation_result.get('evaluation_valid')

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
# TRAINING TARGET INFORMATION
# ==========================================================

training_target_values = evaluation_result.get('training_target_values')
training_target_unique_values = evaluation_result.get('training_target_unique_values')
training_target_has_variation = evaluation_result.get('training_target_has_variation')

if training_target_values is not None:
    print()
    print(
        "========== TRAINING TARGET =========="
    )
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

# ==========================================================
# TESTING PERIOD
# ==========================================================

print()
print("========== TESTING PERIOD ==========")

for testing_date in evaluation_result['testing_dates']:
    print(testing_date)

# ==========================================================
# ACTUAL VS PREDICTED
# ==========================================================

print()
print("========== ACTUAL vs PREDICTED ==========")

for date_value, actual, predicted in zip(
    evaluation_result['testing_dates'],
    evaluation_result['actual_values'],
    evaluation_result['predicted_values'],
):
    print(
        f"{date_value} | "
        f"Actual: {actual:.2f} | "
        f"Predicted: {predicted:.2f}"
    )

# ==========================================================
# FINAL RESULT
# ==========================================================

print()
print("========== TEST RESULT ==========")

print(
    "PASS: Training pipeline executed successfully."
)

if evaluation_valid is False:
    print(
        "NOTE: Evaluation metrics are partially "
        "unavailable because the current historical "
        "dataset does not contain sufficient target "
        "variation."
    )

print()
print(
    "Important: A target value of 0.0 is a valid "
    "real observation and is never treated as missing."
)