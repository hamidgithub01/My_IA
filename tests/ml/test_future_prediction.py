from datetime import date, timedelta

from ml.training.train import train_model
from ml.prediction.forecast import forecast_expenses


print()
print("========== FUTURE EXPENSE PREDICTION TEST ==========")


# ==========================================================
# TRAIN MODEL
# ==========================================================

print()
print("========== MODEL TRAINING ==========")

training_result = train_model()

model = training_result['model']
feature_names = training_result['feature_names']

print("Training completed successfully.")
print(f"Training rows: {training_result['training_rows']}")
print(f"Feature count: {len(feature_names)}")
print(f"Target: {training_result['target_name']}")


# ==========================================================
# FUTURE FORECAST
# ==========================================================

print()
print("========== FUTURE FORECAST ==========")

start_date = date.today() + timedelta(days=1)

forecast_days = 7

results = forecast_expenses(
    model=model,
    feature_names=feature_names,
    start_date=start_date,
    days=forecast_days,
)


# ==========================================================
# DISPLAY RESULTS
# ==========================================================

print()
print(f"Forecast period: {forecast_days} days")
print()

for result in results:

    print(
        f"{result['Date']} | "
        f"Predicted Expense: "
        f"{result['Predicted_Expense']:.2f}"
    )


# ==========================================================
# VALIDATION
# ==========================================================

print()
print("========== VALIDATION ==========")

if len(results) != forecast_days:
    raise AssertionError(
        "Forecast result count does not match requested days."
    )

for result in results:

    if 'Date' not in result:
        raise AssertionError(
            "Forecast result is missing Date."
        )

    if 'Predicted_Expense' not in result:
        raise AssertionError(
            "Forecast result is missing Predicted_Expense."
        )

    if result['Predicted_Expense'] < 0:
        raise AssertionError(
            "Predicted expense cannot be negative."
        )


print("PASS: Future expense prediction completed successfully.")