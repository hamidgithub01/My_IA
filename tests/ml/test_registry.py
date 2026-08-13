from ml.training.registry import (
    get_latest_model_history,
    get_model_history_by_id,
)


print()
print('========== MODEL REGISTRY TEST ==========')

# ----------------------------------------------------------
# Latest model
# ----------------------------------------------------------

latest_model = get_latest_model_history()

if latest_model is None:

    raise AssertionError(
        'No model history found.'
    )

print()
print('========== LATEST MODEL ==========')

print(
    f"ID: "
    f"{latest_model['id']}"
)

print(
    f"Algorithm: "
    f"{latest_model['algorithm']}"
)

print(
    f"Training rows: "
    f"{latest_model['training_rows']}"
)

print(
    f"Feature count: "
    f"{len(latest_model['feature_names'])}"
)

print(
    f"Coefficient count: "
    f"{len(latest_model['coefficients'])}"
)

print(
    f"Intercept: "
    f"{latest_model['intercept']}"
)

print(
    f"MAE: "
    f"{latest_model['mae']}"
)

print(
    f"RMSE: "
    f"{latest_model['rmse']}"
)

print(
    f"R²: "
    f"{latest_model['r_squared']}"
)

# ----------------------------------------------------------
# Specific model
# ----------------------------------------------------------

model_id = latest_model['id']

model = get_model_history_by_id(
    model_id
)

if model is None:

    raise AssertionError(
        'Could not retrieve model by ID.'
    )

print()
print('========== MODEL BY ID ==========')

print(
    f"Requested ID: "
    f"{model_id}"
)

print(
    f"Returned ID: "
    f"{model['id']}"
)

print(
    f"Feature count: "
    f"{len(model['feature_names'])}"
)

# ----------------------------------------------------------
# Validation
# ----------------------------------------------------------

assert (
    model['id']
    == latest_model['id']
)

assert (
    model['algorithm']
    == 'LinearRegression'
)

assert (
    len(model['feature_names'])
    == len(model['coefficients'])
)

print()
print('========== TEST RESULT ==========')

print(
    'PASS: Model registry can retrieve '
    'the latest and specific model history.'
)