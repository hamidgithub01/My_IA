from ml.training.dataset import (
    prepare_model_dataset,
)

from ml.training.validation import (
    validate_model_dataset,
)


def test_training_dataset_validation():

    print()
    print(
        '========== TRAINING DATASET VALIDATION TEST =========='
    )

    # ------------------------------------------------------
    # Build dataset
    # ------------------------------------------------------

    result = prepare_model_dataset()

    print(
        f"Target: {result['target_name']}"
    )

    print(
        f"Total rows: {len(result['dataset'])}"
    )

    print(
        f"Training rows: {result['training_rows']}"
    )

    print(
        f"Test rows: {result['test_rows']}"
    )

    print(
        f"Features: {len(result['feature_names'])}"
    )

    # ------------------------------------------------------
    # Validate complete dataset
    # ------------------------------------------------------

    validate_model_dataset(
        result
    )

    print(
        'Dataset structure: PASSED'
    )

    print(
        'Date ordering: PASSED'
    )

    print(
        'Duplicate date check: PASSED'
    )

    print(
        'Feature schema: PASSED'
    )

    print(
        'Feature numeric values: PASSED'
    )

    print(
        'X/y alignment: PASSED'
    )

    print(
        'Target validation: PASSED'
    )

    print(
        'Target leakage check: PASSED'
    )

    print(
        'Train/test temporal separation: PASSED'
    )

    print()

    print(
        '========== TRAINING DATASET VALIDATION PASSED =========='
    )


if __name__ == '__main__':

    test_training_dataset_validation()