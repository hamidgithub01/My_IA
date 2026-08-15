from ml.features.financial import (
    create_financial_features,
)


# ==========================================================
# TEST HELPERS
# ==========================================================

def make_row(
    expense=0.0,
    expense_count=0,
    income=0.0,
    income_count=0,
    events=0,
):
    return {
        'Expense_Total': expense,
        'Expense_Count': expense_count,
        'Income_Total': income,
        'Income_Count': income_count,
        'Event_Count': events,
    }


def assert_equal(
    actual,
    expected,
    message,
):
    if actual != expected:
        raise AssertionError(
            f'{message}\n'
            f'Expected: {expected}\n'
            f'Actual: {actual}'
        )


def assert_close(
    actual,
    expected,
    message,
    tolerance=1e-9,
):
    if abs(actual - expected) > tolerance:
        raise AssertionError(
            f'{message}\n'
            f'Expected: {expected}\n'
            f'Actual: {actual}'
        )


# ==========================================================
# EXPECTED FEATURE STRUCTURE
# ==========================================================

EXPECTED_FEATURES = {
    'Expense_Total',
    'Expense_Count',
    'Income_Total',
    'Income_Count',
    'Daily_Balance',
    'Expense_to_Income_Ratio',
    'Event_Count',
}


# ==========================================================
# TEST 1
# BASIC FINANCIAL FEATURE STRUCTURE
# ==========================================================

def test_feature_structure():

    row = make_row(
        expense=100.0,
        expense_count=3,
        income=500.0,
        income_count=1,
        events=2,
    )

    features = create_financial_features(
        row
    )

    assert_equal(
        set(features.keys()),
        EXPECTED_FEATURES,
        'Financial feature structure is incorrect.',
    )

    print(
        'Financial feature structure: PASSED'
    )


# ==========================================================
# TEST 2
# EXPENSE TOTAL
# ==========================================================

def test_expense_total():

    row = make_row(
        expense=1250.75,
    )

    features = create_financial_features(
        row
    )

    assert_close(
        features['Expense_Total'],
        1250.75,
        'Expense_Total is incorrect.',
    )

    print(
        'Expense total calculation: PASSED'
    )


# ==========================================================
# TEST 3
# EXPENSE COUNT
# ==========================================================

def test_expense_count():

    row = make_row(
        expense_count=7,
    )

    features = create_financial_features(
        row
    )

    assert_equal(
        features['Expense_Count'],
        7,
        'Expense_Count is incorrect.',
    )

    print(
        'Expense count: PASSED'
    )


# ==========================================================
# TEST 4
# INCOME TOTAL
# ==========================================================

def test_income_total():

    row = make_row(
        income=2500.50,
    )

    features = create_financial_features(
        row
    )

    assert_close(
        features['Income_Total'],
        2500.50,
        'Income_Total is incorrect.',
    )

    print(
        'Income total calculation: PASSED'
    )


# ==========================================================
# TEST 5
# INCOME COUNT
# ==========================================================

def test_income_count():

    row = make_row(
        income_count=4,
    )

    features = create_financial_features(
        row
    )

    assert_equal(
        features['Income_Count'],
        4,
        'Income_Count is incorrect.',
    )

    print(
        'Income count: PASSED'
    )


# ==========================================================
# TEST 6
# DAILY BALANCE
# ==========================================================

def test_daily_balance():

    row = make_row(
        expense=300.0,
        income=1000.0,
    )

    features = create_financial_features(
        row
    )

    assert_close(
        features['Daily_Balance'],
        700.0,
        'Daily_Balance calculation is incorrect.',
    )

    print(
        'Daily balance calculation: PASSED'
    )


# ==========================================================
# TEST 7
# NEGATIVE DAILY BALANCE
# ==========================================================

def test_negative_daily_balance():

    row = make_row(
        expense=1200.0,
        income=500.0,
    )

    features = create_financial_features(
        row
    )

    assert_close(
        features['Daily_Balance'],
        -700.0,
        'Negative Daily_Balance is incorrect.',
    )

    print(
        'Negative daily balance: PASSED'
    )


# ==========================================================
# TEST 8
# EXPENSE TO INCOME RATIO
# ==========================================================

def test_expense_to_income_ratio():

    row = make_row(
        expense=250.0,
        income=1000.0,
    )

    features = create_financial_features(
        row
    )

    assert_close(
        features['Expense_to_Income_Ratio'],
        0.25,
        'Expense_to_Income_Ratio is incorrect.',
    )

    print(
        'Expense-to-income ratio: PASSED'
    )


# ==========================================================
# TEST 9
# ZERO INCOME RATIO
# ==========================================================

def test_zero_income_ratio():

    row = make_row(
        expense=500.0,
        income=0.0,
    )

    features = create_financial_features(
        row
    )

    assert_close(
        features['Expense_to_Income_Ratio'],
        0.0,
        'Zero-income ratio handling is incorrect.',
    )

    print(
        'Zero-income ratio handling: PASSED'
    )


# ==========================================================
# TEST 10
# ZERO EXPENSE
# ==========================================================

def test_zero_expense():

    row = make_row(
        expense=0.0,
        income=1000.0,
    )

    features = create_financial_features(
        row
    )

    assert_close(
        features['Expense_Total'],
        0.0,
        'Zero Expense_Total is incorrect.',
    )

    assert_close(
        features['Daily_Balance'],
        1000.0,
        'Daily_Balance with zero expense is incorrect.',
    )

    assert_close(
        features['Expense_to_Income_Ratio'],
        0.0,
        'Expense-to-income ratio with zero expense is incorrect.',
    )

    print(
        'Zero expense handling: PASSED'
    )


# ==========================================================
# TEST 11
# ZERO INCOME AND ZERO EXPENSE
# ==========================================================

def test_zero_income_and_expense():

    row = make_row(
        expense=0.0,
        income=0.0,
    )

    features = create_financial_features(
        row
    )

    assert_close(
        features['Daily_Balance'],
        0.0,
        'Zero-income/zero-expense balance is incorrect.',
    )

    assert_close(
        features['Expense_to_Income_Ratio'],
        0.0,
        'Zero-income/zero-expense ratio is incorrect.',
    )

    print(
        'Zero income and expense handling: PASSED'
    )


# ==========================================================
# TEST 12
# EVENT COUNT
# ==========================================================

def test_event_count():

    row = make_row(
        events=8,
    )

    features = create_financial_features(
        row
    )

    assert_equal(
        features['Event_Count'],
        8,
        'Event_Count is incorrect.',
    )

    print(
        'Event count: PASSED'
    )


# ==========================================================
# TEST 13
# MISSING VALUES
# ==========================================================

def test_missing_values():

    row = {}

    features = create_financial_features(
        row
    )

    expected_zero_features = {
        'Expense_Total',
        'Expense_Count',
        'Income_Total',
        'Income_Count',
        'Daily_Balance',
        'Expense_to_Income_Ratio',
        'Event_Count',
    }

    for feature_name in expected_zero_features:

        assert_close(
            features[feature_name],
            0.0,
            f'Missing value handling failed for '
            f'{feature_name}.',
        )

    print(
        'Missing values handling: PASSED'
    )


# ==========================================================
# TEST 14
# NONE VALUES
# ==========================================================

def test_none_values():

    row = {
        'Expense_Total': None,
        'Expense_Count': None,
        'Income_Total': None,
        'Income_Count': None,
        'Event_Count': None,
    }

    features = create_financial_features(
        row
    )

    for feature_name, value in features.items():

        if value != 0.0:
            raise AssertionError(
                f'None value handling failed: '
                f'{feature_name} = {value}'
            )

    print(
        'None values handling: PASSED'
    )


# ==========================================================
# TEST 15
# STRING NUMERIC VALUES
# ==========================================================

def test_numeric_string_values():

    row = {
        'Expense_Total': '250.50',
        'Expense_Count': '3',
        'Income_Total': '1000.00',
        'Income_Count': '1',
        'Event_Count': '4',
    }

    features = create_financial_features(
        row
    )

    assert_close(
        features['Expense_Total'],
        250.50,
        'String Expense_Total conversion failed.',
    )

    assert_equal(
        features['Expense_Count'],
        3,
        'String Expense_Count conversion failed.',
    )

    assert_close(
        features['Income_Total'],
        1000.00,
        'String Income_Total conversion failed.',
    )

    assert_equal(
        features['Income_Count'],
        1,
        'String Income_Count conversion failed.',
    )

    assert_equal(
        features['Event_Count'],
        4,
        'String Event_Count conversion failed.',
    )

    print(
        'Numeric string conversion: PASSED'
    )


# ==========================================================
# TEST 16
# DECIMAL FINANCIAL CALCULATIONS
# ==========================================================

def test_decimal_calculations():

    row = make_row(
        expense=123.45,
        income=678.90,
    )

    features = create_financial_features(
        row
    )

    assert_close(
        features['Daily_Balance'],
        555.45,
        'Decimal Daily_Balance calculation is incorrect.',
    )

    assert_close(
        features['Expense_to_Income_Ratio'],
        123.45 / 678.90,
        'Decimal Expense_to_Income_Ratio is incorrect.',
    )

    print(
        'Decimal financial calculations: PASSED'
    )


# ==========================================================
# TEST 17
# INPUT IMMUTABILITY
# ==========================================================

def test_input_immutability():

    row = make_row(
        expense=500.0,
        expense_count=5,
        income=1500.0,
        income_count=2,
        events=3,
    )

    original_row = dict(
        row
    )

    create_financial_features(
        row
    )

    assert_equal(
        row,
        original_row,
        'create_financial_features modified the input row.',
    )

    print(
        'Input immutability: PASSED'
    )


# ==========================================================
# TEST 18
# OUTPUT NUMERIC TYPES
# ==========================================================

def test_numeric_output():

    row = make_row(
        expense=500.0,
        expense_count=5,
        income=1500.0,
        income_count=2,
        events=3,
    )

    features = create_financial_features(
        row
    )

    integer_features = {
        'Expense_Count',
        'Income_Count',
        'Event_Count',
    }

    for feature_name, value in features.items():

        if not isinstance(
            value,
            (int, float),
        ):
            raise AssertionError(
                f'Feature {feature_name} '
                f'is not numeric: '
                f'{type(value).__name__}'
            )

    for feature_name in integer_features:

        if not isinstance(
            features[feature_name],
            int,
        ):
            raise AssertionError(
                f'{feature_name} should be an integer.'
            )

    print(
        'Numeric feature output: PASSED'
    )


# ==========================================================
# TEST 19
# FEATURE CONSISTENCY
# ==========================================================

def test_feature_consistency():

    row_a = make_row(
        expense=100.0,
        income=500.0,
        events=2,
    )

    row_b = make_row(
        expense=900.0,
        income=2000.0,
        events=7,
    )

    features_a = create_financial_features(
        row_a
    )

    features_b = create_financial_features(
        row_b
    )

    if features_a == features_b:
        raise AssertionError(
            'Different financial inputs produced '
            'identical feature sets.'
        )

    print(
        'Financial feature consistency: PASSED'
    )


# ==========================================================
# TEST 20
# NO UNEXPECTED DEPENDENCY ON UNRELATED FIELDS
# ==========================================================

def test_unrelated_fields_do_not_change_features():

    row = make_row(
        expense=300.0,
        income=1000.0,
        events=4,
    )

    features_a = create_financial_features(
        row
    )

    modified_row = dict(
        row
    )

    modified_row.update({
        'Health_Impact': 'high',
        'Stress_Level': 10,
        'Sleep_Hours': 2,
        'Location': 'Somewhere',
        'Travel': 'yes',
        'Special_Event': 'birthday',
    })

    features_b = create_financial_features(
        modified_row
    )

    assert_equal(
        features_a,
        features_b,
        'Financial features depend on unrelated fields.',
    )

    print(
        'Unrelated field independence: PASSED'
    )


# ==========================================================
# RUN ALL TESTS
# ==========================================================

def test_financial_features():

    print(
        '========== FINANCIAL FEATURES TEST =========='
    )

    test_feature_structure()

    test_expense_total()

    test_expense_count()

    test_income_total()

    test_income_count()

    test_daily_balance()

    test_negative_daily_balance()

    test_expense_to_income_ratio()

    test_zero_income_ratio()

    test_zero_expense()

    test_zero_income_and_expense()

    test_event_count()

    test_missing_values()

    test_none_values()

    test_numeric_string_values()

    test_decimal_calculations()

    test_input_immutability()

    test_numeric_output()

    test_feature_consistency()

    test_unrelated_fields_do_not_change_features()

    print(
        '========== FINANCIAL FEATURES TEST PASSED =========='
    )


if __name__ == '__main__':
    test_financial_features()