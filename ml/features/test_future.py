
from datetime import date, datetime

from ml.features.future import (
    normalize_text,
    to_date,
    safe_float,
    safe_int,
    create_plan_features,
    recurring_applies_to_date,
    create_recurring_features,
    create_future_features,
)


# ==========================================================
# EXPECTED PLAN FEATURES
# ==========================================================

EXPECTED_PLAN_FEATURES = {
    'Plan_Count',
    'Plan_Expected_Cost_Total',
    'Plan_Duration_Total',
    'Plan_High_Importance_Count',
    'Plan_Medium_Importance_Count',
    'Plan_Low_Importance_Count',

    'Plan_Travel_Count',
    'Plan_Medical_Count',
    'Plan_Family_Count',
    'Plan_Purchase_Count',
    'Plan_Social_Count',
    'Plan_Other_Count',

    'Plan_Has_Travel',
    'Plan_Has_Medical',
    'Plan_Has_Family',
    'Plan_Has_Purchase',
    'Plan_Has_Social',
}


# ==========================================================
# EXPECTED RECURRING FEATURES
# ==========================================================

EXPECTED_RECURRING_FEATURES = {
    'Recurring_Count',
    'Recurring_Income_Total',
    'Recurring_Expense_Total',
    'Recurring_Fixed_Income_Total',
    'Recurring_Fixed_Expense_Total',

    'Recurring_Income_Count',
    'Recurring_Expense_Count',

    'Recurring_Daily_Count',
    'Recurring_Weekly_Count',
    'Recurring_Monthly_Count',

    'Recurring_Has_Income',
    'Recurring_Has_Expense',
}


# ==========================================================
# HELPERS
# ==========================================================

def assert_equal(
    actual,
    expected,
    message,
):
    if actual != expected:
        raise AssertionError(
            f"{message}\n"
            f"Expected: {expected}\n"
            f"Actual:   {actual}"
        )


def assert_almost_equal(
    actual,
    expected,
    message,
    tolerance=1e-9,
):
    if abs(actual - expected) > tolerance:
        raise AssertionError(
            f"{message}\n"
            f"Expected: {expected}\n"
            f"Actual:   {actual}"
        )


# ==========================================================
# TEST
# ==========================================================

def test_future_features():

    print(
        "========== FUTURE FEATURES TEST =========="
    )

    target_date = date(
        2026,
        8,
        15,
    )

    # ======================================================
    # Test 1:
    # Text normalization
    # ======================================================

    assert_equal(
        normalize_text(
            '  Travel  '
        ),
        'travel',
        "Text normalization failed."
    )

    assert_equal(
        normalize_text(
            None
        ),
        '',
        "None normalization failed."
    )

    assert_equal(
        normalize_text(
            ''
        ),
        '',
        "Empty string normalization failed."
    )

    print(
        "Text normalization: PASSED"
    )

    # ======================================================
    # Test 2:
    # Date conversion
    # ======================================================

    assert_equal(
        to_date(
            date(
                2026,
                8,
                15,
            )
        ),
        target_date,
        "Date conversion failed."
    )

    assert_equal(
        to_date(
            datetime(
                2026,
                8,
                15,
                12,
                30,
            )
        ),
        target_date,
        "Datetime conversion failed."
    )

    assert_equal(
        to_date(
            '2026-08-15'
        ),
        target_date,
        "ISO date conversion failed."
    )

    assert_equal(
        to_date(
            ''
        ),
        None,
        "Empty date handling failed."
    )

    assert_equal(
        to_date(
            None
        ),
        None,
        "None date handling failed."
    )

    print(
        "Date conversion: PASSED"
    )

    # ======================================================
    # Test 3:
    # Safe numeric conversion
    # ======================================================

    assert_almost_equal(
        safe_float(
            '125.50'
        ),
        125.50,
        "safe_float conversion failed."
    )

    assert_equal(
        safe_int(
            '7.9'
        ),
        7,
        "safe_int conversion failed."
    )

    assert_almost_equal(
        safe_float(
            None
        ),
        0.0,
        "safe_float None handling failed."
    )

    assert_equal(
        safe_int(
            None
        ),
        0,
        "safe_int None handling failed."
    )

    assert_almost_equal(
        safe_float(
            'invalid'
        ),
        0.0,
        "safe_float invalid value handling failed."
    )

    assert_equal(
        safe_int(
            'invalid'
        ),
        0,
        "safe_int invalid value handling failed."
    )

    print(
        "Safe numeric conversion: PASSED"
    )

    # ======================================================
    # Test 4:
    # Empty plan handling
    # ======================================================

    empty_plan_features = (
        create_plan_features(
            target_date,
            [],
        )
    )

    assert_equal(
        set(
            empty_plan_features.keys()
        ),
        EXPECTED_PLAN_FEATURES,
        "Plan feature structure mismatch."
    )

    assert_equal(
        empty_plan_features[
            'Plan_Count'
        ],
        0,
        "Empty plan count must be zero."
    )

    assert_almost_equal(
        empty_plan_features[
            'Plan_Expected_Cost_Total'
        ],
        0.0,
        "Empty plan cost must be zero."
    )

    print(
        "Empty plan handling: PASSED"
    )

    # ======================================================
    # Test 5:
    # Plan target-date filtering
    # ======================================================

    plans = [
        {
            'Plan_Date': '2026-08-15',
            'Expected_Cost': 100,
            'Duration_Days': 2,
            'Importance': 'high',
            'Plan_Type': 'travel',
            'Status': 'planned',
        },
        {
            'Plan_Date': '2026-08-16',
            'Expected_Cost': 999,
            'Duration_Days': 10,
            'Importance': 'high',
            'Plan_Type': 'travel',
            'Status': 'planned',
        },
    ]

    features = create_plan_features(
        target_date,
        plans,
    )

    assert_equal(
        features['Plan_Count'],
        1,
        "Future plan date filtering failed."
    )

    assert_almost_equal(
        features[
            'Plan_Expected_Cost_Total'
        ],
        100.0,
        "Wrong plan cost was included."
    )

    print(
        "Target-date plan filtering: PASSED"
    )

    # ======================================================
    # Test 6:
    # Cancelled plan exclusion
    # ======================================================

    cancelled_plans = [
        {
            'Plan_Date': target_date,
            'Expected_Cost': 500,
            'Duration_Days': 3,
            'Importance': 'high',
            'Plan_Type': 'travel',
            'Status': 'cancelled',
        },
        {
            'Plan_Date': target_date,
            'Expected_Cost': 200,
            'Duration_Days': 1,
            'Importance': 'medium',
            'Plan_Type': 'social',
            'Status': 'planned',
        },
    ]

    features = create_plan_features(
        target_date,
        cancelled_plans,
    )

    assert_equal(
        features['Plan_Count'],
        1,
        "Cancelled plan was not excluded."
    )

    assert_almost_equal(
        features[
            'Plan_Expected_Cost_Total'
        ],
        200.0,
        "Cancelled plan cost was included."
    )

    print(
        "Cancelled plan exclusion: PASSED"
    )

    # ======================================================
    # Test 7:
    # Plan aggregation
    # ======================================================

    plans = [
        {
            'Plan_Date': target_date,
            'Expected_Cost': 100,
            'Duration_Days': 2,
            'Importance': 'high',
            'Plan_Type': 'travel',
            'Status': 'planned',
        },
        {
            'Plan_Date': target_date,
            'Expected_Cost': 50,
            'Duration_Days': 1,
            'Importance': 'medium',
            'Plan_Type': 'medical',
            'Status': 'planned',
        },
        {
            'Plan_Date': target_date,
            'Expected_Cost': 25,
            'Duration_Days': 3,
            'Importance': 'low',
            'Plan_Type': 'social',
            'Status': 'planned',
        },
        {
            'Plan_Date': target_date,
            'Expected_Cost': 10,
            'Duration_Days': 1,
            'Importance': 'unknown',
            'Plan_Type': 'other',
            'Status': 'planned',
        },
    ]

    features = create_plan_features(
        target_date,
        plans,
    )

    assert_equal(
        features['Plan_Count'],
        4,
        "Plan aggregation count failed."
    )

    assert_almost_equal(
        features[
            'Plan_Expected_Cost_Total'
        ],
        185.0,
        "Plan expected cost aggregation failed."
    )

    assert_equal(
        features[
            'Plan_Duration_Total'
        ],
        7,
        "Plan duration aggregation failed."
    )

    assert_equal(
        features[
            'Plan_High_Importance_Count'
        ],
        1,
        "High importance count failed."
    )

    assert_equal(
        features[
            'Plan_Medium_Importance_Count'
        ],
        1,
        "Medium importance count failed."
    )

    assert_equal(
        features[
            'Plan_Low_Importance_Count'
        ],
        1,
        "Low importance count failed."
    )

    assert_equal(
        features[
            'Plan_Other_Count'
        ],
        1,
        "Other plan count failed."
    )

    print(
        "Plan aggregation: PASSED"
    )

    # ======================================================
    # Test 8:
    # Plan type flags
    # ======================================================

    assert_equal(
        features[
            'Plan_Has_Travel'
        ],
        1,
        "Travel plan flag failed."
    )

    assert_equal(
        features[
            'Plan_Has_Medical'
        ],
        1,
        "Medical plan flag failed."
    )

    assert_equal(
        features[
            'Plan_Has_Social'
        ],
        1,
        "Social plan flag failed."
    )

    assert_equal(
        features[
            'Plan_Has_Family'
        ],
        0,
        "Unexpected family plan flag."
    )

    assert_equal(
        features[
            'Plan_Has_Purchase'
        ],
        0,
        "Unexpected purchase plan flag."
    )

    print(
        "Plan type flags: PASSED"
    )

    # ======================================================
    # Test 9:
    # Recurring date applicability
    # ======================================================

    daily = {
        'Is_Active': True,
        'Start_Date': '2026-08-01',
        'End_Date': '2026-08-31',
        'Frequency': 'daily',
    }

    assert_equal(
        recurring_applies_to_date(
            daily,
            target_date,
        ),
        True,
        "Daily recurring applicability failed."
    )

    weekly = {
        'Is_Active': True,
        'Start_Date': '2026-08-01',
        'End_Date': '2026-08-31',
        'Frequency': 'weekly',
        'Day_Of_Week': target_date.weekday(),
    }

    assert_equal(
        recurring_applies_to_date(
            weekly,
            target_date,
        ),
        True,
        "Weekly recurring applicability failed."
    )

    monthly = {
        'Is_Active': True,
        'Start_Date': '2026-08-01',
        'End_Date': '2026-08-31',
        'Frequency': 'monthly',
        'Day_Of_Month': target_date.day,
    }

    assert_equal(
        recurring_applies_to_date(
            monthly,
            target_date,
        ),
        True,
        "Monthly recurring applicability failed."
    )

    print(
        "Recurring frequency applicability: PASSED"
    )

    # ======================================================
    # Test 10:
    # Recurring inactive handling
    # ======================================================

    inactive = {
        'Is_Active': False,
        'Frequency': 'daily',
    }

    assert_equal(
        recurring_applies_to_date(
            inactive,
            target_date,
        ),
        False,
        "Inactive recurring record was accepted."
    )

    print(
        "Inactive recurring handling: PASSED"
    )

    # ======================================================
    # Test 11:
    # Recurring date boundaries
    # ======================================================

    bounded = {
        'Is_Active': True,
        'Start_Date': '2026-08-20',
        'End_Date': '2026-08-30',
        'Frequency': 'daily',
    }

    assert_equal(
        recurring_applies_to_date(
            bounded,
            target_date,
        ),
        False,
        "Recurring record before start date was accepted."
    )

    assert_equal(
        recurring_applies_to_date(
            bounded,
            date(
                2026,
                8,
                25,
            ),
        ),
        True,
        "Recurring record inside date range was rejected."
    )

    assert_equal(
        recurring_applies_to_date(
            bounded,
            date(
                2026,
                8,
                31,
            ),
        ),
        False,
        "Recurring record after end date was accepted."
    )

    print(
        "Recurring date boundaries: PASSED"
    )

    # ======================================================
    # Test 12:
    # Recurring aggregation
    # ======================================================

    recurring = [
        {
            'Is_Active': True,
            'Start_Date': '2026-08-01',
            'End_Date': '2026-08-31',
            'Frequency': 'daily',
            'Type': 'income',
            'Amount': 1000,
            'Is_Fixed_Amount': True,
        },
        {
            'Is_Active': True,
            'Start_Date': '2026-08-01',
            'End_Date': '2026-08-31',
            'Frequency': 'daily',
            'Type': 'expense',
            'Amount': 200,
            'Is_Fixed_Amount': True,
        },
        {
            'Is_Active': True,
            'Start_Date': '2026-08-01',
            'End_Date': '2026-08-31',
            'Frequency': 'weekly',
            'Day_Of_Week': target_date.weekday(),
            'Type': 'expense',
            'Amount': 50,
            'Is_Fixed_Amount': False,
        },
    ]

    features = create_recurring_features(
        target_date,
        recurring,
    )

    assert_equal(
        features[
            'Recurring_Count'
        ],
        3,
        "Recurring count failed."
    )

    assert_equal(
        features[
            'Recurring_Income_Count'
        ],
        1,
        "Recurring income count failed."
    )

    assert_equal(
        features[
            'Recurring_Expense_Count'
        ],
        2,
        "Recurring expense count failed."
    )

    assert_almost_equal(
        features[
            'Recurring_Income_Total'
        ],
        1000.0,
        "Recurring income total failed."
    )

    assert_almost_equal(
        features[
            'Recurring_Expense_Total'
        ],
        250.0,
        "Recurring expense total failed."
    )

    assert_almost_equal(
        features[
            'Recurring_Fixed_Income_Total'
        ],
        1000.0,
        "Fixed recurring income total failed."
    )

    assert_almost_equal(
        features[
            'Recurring_Fixed_Expense_Total'
        ],
        200.0,
        "Fixed recurring expense total failed."
    )

    print(
        "Recurring aggregation: PASSED"
    )

    # ======================================================
    # Test 13:
    # Recurring frequency counts
    # ======================================================

    assert_equal(
        features[
            'Recurring_Daily_Count'
        ],
        2,
        "Daily recurring count failed."
    )

    assert_equal(
        features[
            'Recurring_Weekly_Count'
        ],
        1,
        "Weekly recurring count failed."
    )

    assert_equal(
        features[
            'Recurring_Monthly_Count'
        ],
        0,
        "Unexpected monthly recurring count."
    )

    print(
        "Recurring frequency counts: PASSED"
    )

    # ======================================================
    # Test 14:
    # Recurring presence flags
    # ======================================================

    assert_equal(
        features[
            'Recurring_Has_Income'
        ],
        1,
        "Recurring income flag failed."
    )

    assert_equal(
        features[
            'Recurring_Has_Expense'
        ],
        1,
        "Recurring expense flag failed."
    )

    print(
        "Recurring presence flags: PASSED"
    )

    # ======================================================
    # Test 15:
    # Future target-date independence
    #
    # Records belonging to another date must not affect
    # target-day future features.
    # ======================================================

    relevant_plan = {
        'Plan_Date': target_date,
        'Expected_Cost': 100,
        'Duration_Days': 2,
        'Importance': 'high',
        'Plan_Type': 'travel',
        'Status': 'planned',
    }

    unrelated_plan = {
        'Plan_Date': date(
            2030,
            1,
            1,
        ),
        'Expected_Cost': 999999,
        'Duration_Days': 999,
        'Importance': 'high',
        'Plan_Type': 'travel',
        'Status': 'planned',
    }

    original = create_plan_features(
        target_date,
        [relevant_plan],
    )

    modified = create_plan_features(
        target_date,
        [
            relevant_plan,
            unrelated_plan,
        ],
    )

    assert_equal(
        original,
        modified,
        "Unrelated future plan changed target-day features."
    )

    print(
        "Future target-date independence: PASSED"
    )

    # ======================================================
    # Test 16:
    # Actual outcome independence
    #
    # Adding actual outcome fields must not change
    # future features.
    # ======================================================

    plan_without_outcomes = {
        'Plan_Date': target_date,
        'Expected_Cost': 100,
        'Duration_Days': 2,
        'Importance': 'high',
        'Plan_Type': 'travel',
        'Status': 'planned',
    }

    plan_with_outcomes = dict(
        plan_without_outcomes
    )

    plan_with_outcomes[
        'Actual_Date'
    ] = '2026-08-15'

    plan_with_outcomes[
        'Actual_Cost'
    ] = 999999

    original = create_plan_features(
        target_date,
        [plan_without_outcomes],
    )

    modified = create_plan_features(
        target_date,
        [plan_with_outcomes],
    )

    assert_equal(
        original,
        modified,
        "Actual outcome fields leaked into plan features."
    )

    print(
        "Actual outcome independence: PASSED"
    )

    # ======================================================
    # Test 17:
    # Combined future features
    # ======================================================

    combined = create_future_features(
        target_date,
        plans=[
            {
                'Plan_Date': target_date,
                'Expected_Cost': 300,
                'Duration_Days': 2,
                'Importance': 'high',
                'Plan_Type': 'purchase',
                'Status': 'planned',
            }
        ],
        recurring=[
            {
                'Is_Active': True,
                'Start_Date': '2026-08-01',
                'End_Date': '2026-08-31',
                'Frequency': 'daily',
                'Type': 'expense',
                'Amount': 50,
                'Is_Fixed_Amount': True,
            }
        ],
    )

    expected_combined_keys = (
        EXPECTED_PLAN_FEATURES
        | EXPECTED_RECURRING_FEATURES
    )

    assert_equal(
        set(
            combined.keys()
        ),
        expected_combined_keys,
        "Combined future feature structure mismatch."
    )

    assert_equal(
        combined[
            'Plan_Count'
        ],
        1,
        "Combined plan feature failed."
    )

    assert_equal(
        combined[
            'Recurring_Count'
        ],
        1,
        "Combined recurring feature failed."
    )

    print(
        "Combined future features: PASSED"
    )

    # ======================================================
    # Test 18:
    # Numeric output
    # ======================================================

    for key, value in combined.items():

        if not isinstance(
            value,
            (
                int,
                float,
            ),
        ):
            raise AssertionError(
                f"Non-numeric future feature: "
                f"{key} = {value!r}"
            )

    print(
        "Numeric feature output: PASSED"
    )

    # ======================================================
    # Test 19:
    # Empty combined input
    # ======================================================

    empty_combined = create_future_features(
        target_date,
        None,
        None,
    )

    assert_equal(
        set(
            empty_combined.keys()
        ),
        expected_combined_keys,
        "Empty combined feature structure mismatch."
    )

    assert_equal(
        sum(
            value
            for value in empty_combined.values()
        ),
        0,
        "Empty combined features are not zero."
    )

    print(
        "Empty combined input handling: PASSED"
    )

    # ======================================================
    # FINAL
    # ======================================================

    print(
        "========== FUTURE FEATURES TEST PASSED =========="
    )


if __name__ == '__main__':
    test_future_features()
