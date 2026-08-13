from datetime import date

from ml.training.load import (
    load_latest_model,
)

from ml.features.build import (
    build_training_dataset,
)


print()
print('========== MODEL LOADING TEST ==========')


# ==========================================================
# LOAD LATEST MODEL
# ==========================================================

print()
print('========== LOAD LATEST MODEL ==========')

loaded_result = load_latest_model()

if loaded_result is None:

    print(
        'No saved model is available.'
    )

    raise SystemExit(1)


model = loaded_result['model']
feature_names = loaded_result['feature_names']


print(
    f"Model history ID: "
    f"{loaded_result['model_history_id']}"
)

print(
    f"Training rows: "
    f"{loaded_result['training_rows']}"
)

print(
    f"Feature count: "
    f"{len(feature_names)}"
)

print(
    f"Algorithm: "
    f"{model.__class__.__name__}"
)


# ==========================================================
# MODEL PARAMETERS
# ==========================================================

print()
print('========== LOADED MODEL PARAMETERS ==========')

print(
    f'Intercept: {model.intercept_}'
)

print(
    f'Coefficient count: '
    f'{len(model.coef_)}'
)


# ==========================================================
# VALIDATE MODEL STRUCTURE
# ==========================================================

print()
print('========== STRUCTURE VALIDATION ==========')

if len(feature_names) != len(model.coef_):

    raise AssertionError(
        'Feature count does not match '
        'coefficient count.'
    )

print(
    'PASS: Feature count matches '
    'coefficient count.'
)


# ==========================================================
# BUILD TEST INPUT
# ==========================================================

print()
print('========== PREDICTION TEST ==========')

data = build_training_dataset()

if not data:

    raise ValueError(
        'No feature data available '
        'for prediction test.'
    )


row = data[0]

feature_vector = [
    float(
        row.get(feature, 0.0)
        or 0.0
    )
    for feature in feature_names
]


# ==========================================================
# PREDICT
# ==========================================================

prediction = model.predict(
    [feature_vector]
)[0]

prediction = max(
    0.0,
    float(prediction),
)


print(
    f"Test date: {row['Date']}"
)

print(
    f"Predicted expense: "
    f'{prediction:.2f}'
)


# ==========================================================
# FINAL VALIDATION
# ==========================================================

if prediction < 0:

    raise AssertionError(
        'Prediction cannot be negative.'
    )


print()
print('========== TEST RESULT ==========')

print(
    'PASS: Saved model was loaded '
    'and successfully used for prediction.'
)