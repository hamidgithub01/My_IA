from ml.training.dataset import (
    prepare_model_dataset,
)


def test_model_dataset():

    print(
        '========== MODEL DATASET TEST =========='
    )

    result = prepare_model_dataset()

    X_train = result['X_train']
    y_train = result['y_train']

    X_test = result['X_test']
    y_test = result['y_test']

    feature_names = result[
        'feature_names'
    ]

    training_data = result[
        'training_data'
    ]

    test_data = result[
        'test_data'
    ]

    # ------------------------------------------------------
    # Basic information
    # ------------------------------------------------------

    print(
        f'Total features: {len(feature_names)}'
    )

    print(
        f'Training rows: {len(X_train)}'
    )

    print(
        f'Test rows: {len(X_test)}'
    )

    print(
        f'y_train values: {len(y_train)}'
    )

    print(
        f'y_test values: {len(y_test)}'
    )

    # ------------------------------------------------------
    # X / y alignment
    # ------------------------------------------------------

    if len(X_train) != len(y_train):

        raise AssertionError(
            'X_train and y_train '
            'have different lengths.'
        )

    if len(X_test) != len(y_test):

        raise AssertionError(
            'X_test and y_test '
            'have different lengths.'
        )

    print(
        'Training X/y alignment: PASSED'
    )

    print(
        'Test X/y alignment: PASSED'
    )

    # ------------------------------------------------------
    # Feature dimensions
    # ------------------------------------------------------

    if X_train:

        if len(X_train[0]) != len(
            feature_names
        ):

            raise AssertionError(
                'Training feature count '
                'does not match feature names.'
            )

    if X_test:

        if len(X_test[0]) != len(
            feature_names
        ):

            raise AssertionError(
                'Test feature count '
                'does not match feature names.'
            )

    print(
        'Feature dimensions: PASSED'
    )

    # ------------------------------------------------------
    # Forbidden model inputs
    # ------------------------------------------------------

    forbidden = [
        name
        for name in feature_names
        if name == 'Date'
        or name.startswith('Target_')
    ]

    if forbidden:

        raise AssertionError(
            'Forbidden columns inside X: '
            f'{forbidden}'
        )

    print(
        'Feature leakage check: PASSED'
    )

    # ------------------------------------------------------
    # Temporal separation
    # ------------------------------------------------------

    if training_data and test_data:

        last_training_date = (
            training_data[-1]['Date']
        )

        first_test_date = (
            test_data[0]['Date']
        )

        print(
            f'Last training date: '
            f'{last_training_date}'
        )

        print(
            f'First test date: '
            f'{first_test_date}'
        )

        if first_test_date <= (
            last_training_date
        ):

            raise AssertionError(
                'Temporal separation failed.'
            )

    print(
        'Temporal separation: PASSED'
    )

    # ------------------------------------------------------
    # Target validation
    # ------------------------------------------------------

    if any(
        value is None
        for value in y_train
    ):

        raise AssertionError(
            'Missing values found in y_train.'
        )

    if any(
        value is None
        for value in y_test
    ):

        raise AssertionError(
            'Missing values found in y_test.'
        )

    print(
        'Target values: PASSED'
    )

    print()

    print(
        '========== MODEL DATASET TEST PASSED =========='
    )


if __name__ == '__main__':

    test_model_dataset()