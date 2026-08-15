from datetime import date, timedelta

from ml.features.build import build_feature_row
from ml.features.history import create_history_features
from ml.features.lags import create_lag_features
from ml.features.rolling import create_rolling_features


# =========================================================
# HELPERS
# =========================================================

TARGET_DATE = date(2026, 8, 15)


def make_row(day, **values):
    row = {
        'Date': day,
        'Expense_Total': 100.0,
        'Income_Total': 200.0,
        'Event_Count': 1,
        'Health_Record_Count': 1,
        'Max_Health_Severity': 2.0,
        'Avg_Energy_Level': 7.0,
        'Activity_Count': 1,
        'Activity_Duration_Minutes': 30.0,
        'Activity_Cost': 20.0,
        'Sleep_Duration_Minutes': 420.0,
        'Avg_Sleep_Quality': 8.0,
        'Total_Awakenings': 1,
        'Stress_Level': 3.0,
        'Sleep_Hours': 7.0,
        'Social_Activity': 'low',
        'Work_Status': 'working',
        'Day_Type': 'workday',
        'Health_Impact': 'none',
        'Travel': '',
        'Special_Event': '',
        'Location': '',
    }

    row.update(values)

    return row


# =========================================================
# HISTORY LEAKAGE
# =========================================================

def test_history_never_uses_target_day():
    target_row = make_row(
        TARGET_DATE,
        Expense_Total=999999.0,
        Income_Total=888888.0,
        Event_Count=999,
        Stress_Level=10.0,
    )

    previous_rows = [
        make_row(
            TARGET_DATE - timedelta(days=1),
            Expense_Total=100.0,
            Income_Total=200.0,
        )
    ]

    features = create_history_features(
        target_row,
        previous_rows,
    )

    assert features['Previous_Day_Expense'] == 100.0
    assert features['Previous_Day_Income'] == 200.0

    assert features['Previous_Day_Expense'] != 999999.0
    assert features['Previous_Day_Income'] != 888888.0


# =========================================================
# FUTURE HISTORY LEAKAGE
# =========================================================

def test_history_never_uses_future_rows():
    target_row = make_row(TARGET_DATE)

    previous_rows = [
        make_row(
            TARGET_DATE - timedelta(days=1),
            Expense_Total=100.0,
        ),
        make_row(
            TARGET_DATE + timedelta(days=1),
            Expense_Total=999999.0,
        ),
    ]

    features = create_history_features(
        target_row,
        previous_rows,
    )

    assert features['Previous_Day_Expense'] == 100.0


# =========================================================
# LAG LEAKAGE
# =========================================================

def test_lags_use_only_exact_calendar_dates():
    target_row = make_row(TARGET_DATE)

    previous_rows = [
        make_row(
            TARGET_DATE - timedelta(days=1),
            Expense_Total=101.0,
        ),
        make_row(
            TARGET_DATE - timedelta(days=7),
            Expense_Total=707.0,
        ),
        make_row(
            TARGET_DATE + timedelta(days=1),
            Expense_Total=999999.0,
        ),
    ]

    features = create_lag_features(
        target_row,
        previous_rows,
    )

    assert features['Lag_1_Expense'] == 101.0
    assert features['Lag_7_Expense'] == 707.0

    assert features['Lag_1_Expense'] != 999999.0
    assert features['Lag_7_Expense'] != 999999.0


# =========================================================
# LAG MUST NOT USE NEAREST ROW
# =========================================================

def test_lag_does_not_use_nearest_available_row():
    target_row = make_row(TARGET_DATE)

    previous_rows = [
        make_row(
            TARGET_DATE - timedelta(days=6),
            Expense_Total=600.0,
        ),
    ]

    features = create_lag_features(
        target_row,
        previous_rows,
    )

    # There is no exact T-7 row.
    # Therefore Lag_7 must remain zero.
    assert features['Lag_7_Expense'] == 0.0


# =========================================================
# ROLLING LEAKAGE
# =========================================================

def test_rolling_features_never_use_target_day():
    target_row = make_row(
        TARGET_DATE,
        Expense_Total=999999.0,
    )

    previous_rows = [
        make_row(
            TARGET_DATE - timedelta(days=1),
            Expense_Total=100.0,
        ),
        make_row(
            TARGET_DATE - timedelta(days=2),
            Expense_Total=200.0,
        ),
    ]

    features = create_rolling_features(
        target_row,
        previous_rows,
    )

    assert features['Rolling_3D_Avg_Expense'] == 150.0


# =========================================================
# ROLLING FUTURE EXCLUSION
# =========================================================

def test_rolling_features_never_use_future_rows():
    target_row = make_row(TARGET_DATE)

    previous_rows = [
        make_row(
            TARGET_DATE - timedelta(days=1),
            Expense_Total=100.0,
        ),
        make_row(
            TARGET_DATE + timedelta(days=1),
            Expense_Total=999999.0,
        ),
    ]

    features = create_rolling_features(
        target_row,
        previous_rows,
    )

    assert features['Rolling_3D_Avg_Expense'] == 100.0


# =========================================================
# BUILD FEATURE ROW
# =========================================================

def test_build_feature_row_does_not_contain_target_outcomes():
    target_row = make_row(
        TARGET_DATE,
        Expense_Total=999999.0,
        Income_Total=888888.0,
        Event_Count=999,
        Activity_Duration_Minutes=9999.0,
        Stress_Level=10.0,
    )

    previous_rows = [
        make_row(
            TARGET_DATE - timedelta(days=1),
            Expense_Total=100.0,
            Income_Total=200.0,
        )
    ]

    features = build_feature_row(
        target_row,
        previous_rows,
    )

    forbidden_target_fields = {
        'Expense_Total',
        'Income_Total',
        'Event_Count',
        'Activity_Duration_Minutes',
        'Stress_Level',
        'Sleep_Hours',
        'Health_Record_Count',
        'Max_Health_Severity',
    }

    assert not (
        forbidden_target_fields
        & set(features.keys())
    )


# =========================================================
# TARGET IS ADDED ONLY AFTER FEATURES
# =========================================================

def test_target_is_separate_from_feature_names():
    target_row = make_row(TARGET_DATE)

    previous_rows = [
        make_row(
            TARGET_DATE - timedelta(days=1)
        )
    ]

    features = build_feature_row(
        target_row,
        previous_rows,
    )

    assert 'Target_Expense_Total' not in features

    features['Target_Expense_Total'] = (
        target_row['Expense_Total']
    )

    assert (
        features['Target_Expense_Total']
        == target_row['Expense_Total']
    )


# =========================================================
# TARGET-DAY MUTATION TEST
# =========================================================

def test_changing_target_day_outcomes_does_not_change_historical_features():
    previous_rows = [
        make_row(
            TARGET_DATE - timedelta(days=1),
            Expense_Total=100.0,
            Income_Total=200.0,
        )
    ]

    target_a = make_row(
        TARGET_DATE,
        Expense_Total=100.0,
        Income_Total=200.0,
        Event_Count=1,
        Stress_Level=2.0,
        Activity_Duration_Minutes=30.0,
    )

    target_b = make_row(
        TARGET_DATE,
        Expense_Total=999999.0,
        Income_Total=888888.0,
        Event_Count=999,
        Stress_Level=10.0,
        Activity_Duration_Minutes=9999.0,
    )

    features_a = build_feature_row(
        target_a,
        previous_rows,
    )

    features_b = build_feature_row(
        target_b,
        previous_rows,
    )

    # Remove metadata that is intentionally identical.
    assert features_a == features_b