from ml.models.forecasting import (
    create_forecasting_model,
    get_model_type,
)


def test_model_architecture():

    print(
        '========== MODEL ARCHITECTURE TEST =========='
    )

    # ======================================================
    # 1. Regression
    # ======================================================

    model_type = get_model_type(
        'numeric'
    )

    if model_type != 'regression':
        raise AssertionError(
            'Numeric target did not map to regression.'
        )

    model = create_forecasting_model(
        'numeric'
    )

    if type(model).__name__ != 'LinearRegression':
        raise AssertionError(
            'Numeric target did not create '
            'LinearRegression.'
        )

    print(
        'Numeric → Regression: PASSED'
    )

    # ======================================================
    # 2. Binary Classification
    # ======================================================

    model_type = get_model_type(
        'categorical',
        2,
    )

    if model_type != 'classification':
        raise AssertionError(
            'Binary categorical target did not map '
            'to classification.'
        )

    model = create_forecasting_model(
        'categorical',
        2,
    )

    if type(model).__name__ != 'LogisticRegression':
        raise AssertionError(
            'Binary target did not create '
            'LogisticRegression.'
        )

    print(
        'Binary classification: PASSED'
    )

    # ======================================================
    # 3. Multiclass Classification
    # ======================================================

    model_type = get_model_type(
        'categorical',
        3,
    )

    if model_type != 'multiclass':
        raise AssertionError(
            '3+ class target did not map to multiclass.'
        )

    model = create_forecasting_model(
        'categorical',
        3,
    )

    if type(model).__name__ != 'LogisticRegression':
        raise AssertionError(
            'Multiclass target did not create '
            'LogisticRegression.'
        )

    print(
        'Multiclass classification: PASSED'
    )

    # ======================================================
    # 4. Missing class count
    # ======================================================

    try:

        create_forecasting_model(
            'categorical'
        )

    except ValueError:

        print(
            'Missing class count validation: PASSED'
        )

    else:

        raise AssertionError(
            'Categorical target without class_count '
            'did not raise ValueError.'
        )

    # ======================================================
    # 5. Unsupported target type
    # ======================================================

    try:

        create_forecasting_model(
            'unknown'
        )

    except ValueError:

        print(
            'Unsupported target type validation: PASSED'
        )

    else:

        raise AssertionError(
            'Unsupported target type did not '
            'raise ValueError.'
        )

    # ======================================================
    # FINAL
    # ======================================================

    print()

    print(
        '========== MODEL ARCHITECTURE TEST PASSED =========='
    )


if __name__ == '__main__':

    test_model_architecture()