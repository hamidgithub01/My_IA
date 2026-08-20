import math
import os

from ml.training.train import train_target_model

from ml.models.registry import (
    REGISTRY_VALID,
    save_registered_model,
    load_registered_model,
)


# ==========================================================
# REGISTRY PERSISTENCE TEST
# ==========================================================

def test_registry_persistence():
    """
    Verify that a trained model can be registered,
    persisted, loaded, and used for identical predictions.

    Pytest test functions intentionally return None.
    """

    target_name = 'Target_Expense_Total_1D'
    version = 'v1.0.0'

    # ------------------------------------------------------
    # TRAIN
    # ------------------------------------------------------

    print()
    print('========== TRAINING ==========')

    training_result = train_target_model(target_name)

    model = training_result['model']
    X_test = training_result['X_test']
    feature_names = training_result['feature_names']

    if model is None:
        raise ValueError(
            'Training returned no model.'
        )

    if X_test is None:
        raise ValueError(
            'Training returned no test features.'
        )

    if len(X_test) == 0:
        raise ValueError(
            'No test features are available.'
        )

    print(
        'Target:',
        training_result['target_name'],
    )

    print(
        'Algorithm:',
        training_result['algorithm'],
    )

    print(
        'Training rows:',
        training_result['training_rows'],
    )

    print(
        'Test rows:',
        training_result['test_rows'],
    )

    print(
        'Feature count:',
        len(feature_names),
    )

    # ------------------------------------------------------
    # BUILD REGISTRY METADATA
    # ------------------------------------------------------

    metadata = {
        'target_name': target_name,
        'target_task': 'regression',
        'target_type': 'numeric',
        'model_type': training_result.get(
            'model_type',
            'regression',
        ),
        'algorithm': training_result['algorithm'],
        'feature_names': list(feature_names),
        'version': version,
    }

    # ------------------------------------------------------
    # ORIGINAL PREDICTIONS
    # ------------------------------------------------------

    print()
    print('========== ORIGINAL MODEL ==========')

    original_predictions = model.predict(X_test)

    original_predictions = [
        float(value)
        for value in original_predictions
    ]

    print(
        'Original predictions:',
        original_predictions,
    )

    # ------------------------------------------------------
    # REGISTER MODEL
    # ------------------------------------------------------

    print()
    print('========== REGISTER MODEL ==========')

    registry_result = save_registered_model(
        model=model,
        metadata=metadata,
    )

    print(
        'Registry status:',
        registry_result['status'],
    )

    print(
        'Model path:',
        registry_result['model_path'],
    )

    print(
        'Metadata path:',
        registry_result['metadata_path'],
    )

    if registry_result['status'] != REGISTRY_VALID:
        raise AssertionError(
            'Model registration failed.'
        )

    # ------------------------------------------------------
    # VERIFY FILES
    # ------------------------------------------------------

    model_path = registry_result['model_path']
    metadata_path = registry_result['metadata_path']

    if not os.path.isfile(model_path):
        raise AssertionError(
            'Registered model file does not exist.'
        )

    if not os.path.isfile(metadata_path):
        raise AssertionError(
            'Registered metadata file does not exist.'
        )

    # ------------------------------------------------------
    # LOAD REGISTERED MODEL
    # ------------------------------------------------------

    print()
    print('========== LOAD REGISTERED MODEL ==========')

    loaded_result = load_registered_model(
        target_name=target_name,
        version=version,
    )

    print(
        'Load status:',
        loaded_result['status'],
    )

    if loaded_result['status'] != REGISTRY_VALID:
        raise AssertionError(
            'Registered model could not be loaded.'
        )

    loaded_model = loaded_result['model']
    loaded_metadata = loaded_result['metadata']

    if loaded_model is None:
        raise AssertionError(
            'Loaded model is None.'
        )

    if loaded_metadata is None:
        raise AssertionError(
            'Loaded metadata is None.'
        )

    # ------------------------------------------------------
    # RESTORED PREDICTIONS
    # ------------------------------------------------------

    print()
    print('========== RESTORED MODEL ==========')

    restored_predictions = loaded_model.predict(X_test)

    restored_predictions = [
        float(value)
        for value in restored_predictions
    ]

    print(
        'Restored predictions:',
        restored_predictions,
    )

    # ------------------------------------------------------
    # PREDICTION COUNT
    # ------------------------------------------------------

    if len(original_predictions) != len(restored_predictions):
        raise AssertionError(
            'Original and restored models produced '
            'different numbers of predictions.'
        )

    # ------------------------------------------------------
    # PREDICTION EQUIVALENCE
    # ------------------------------------------------------

    differences = []

    for index, (original, restored) in enumerate(
        zip(
            original_predictions,
            restored_predictions,
        )
    ):
        if not math.isclose(
            original,
            restored,
            rel_tol=1e-12,
            abs_tol=1e-12,
        ):
            differences.append(
                {
                    'index': index,
                    'original': original,
                    'restored': restored,
                    'difference': abs(
                        original - restored
                    ),
                }
            )

    if differences:
        raise AssertionError(
            'Registry persistence changed predictions:\n'
            f'{differences}'
        )

    # ------------------------------------------------------
    # METADATA VALIDATION
    # ------------------------------------------------------

    if loaded_metadata['target_name'] != target_name:
        raise AssertionError(
            'Loaded metadata target name is incorrect.'
        )

    if loaded_metadata['version'] != version:
        raise AssertionError(
            'Loaded metadata version is incorrect.'
        )

    if loaded_metadata['feature_names'] != feature_names:
        raise AssertionError(
            'Feature schema changed during registry persistence.'
        )

    # ------------------------------------------------------
    # MODEL PATH
    # ------------------------------------------------------

    if loaded_result['model_path'] != model_path:
        raise AssertionError(
            'Loaded model path does not match '
            'registered model path.'
        )

    # ------------------------------------------------------
    # METADATA PATH
    # ------------------------------------------------------

    if loaded_result['metadata_path'] != metadata_path:
        raise AssertionError(
            'Loaded metadata path does not match '
            'registered metadata path.'
        )

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    print()
    print('Registry persistence verification: PASSED')


# ==========================================================
# SIMPLE TEST
# ==========================================================

if __name__ == '__main__':

    print()
    print('==================================================')
    print('       MODEL REGISTRY PERSISTENCE TEST')
    print('==================================================')

    test_registry_persistence()

    print()
    print('Predictions identical: YES')
    print('Model file verified: YES')
    print('Metadata file verified: YES')

    print()
    print('==================================================')
    print('    MODEL REGISTRY PERSISTENCE TEST PASSED')
    print('==================================================')