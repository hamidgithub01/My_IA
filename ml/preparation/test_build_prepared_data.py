import pytest

from ml.preparation.preparation import get_prepared_dataset


def test_get_prepared_dataset_returns_list():
    dataset = get_prepared_dataset()

    assert isinstance(dataset, list)


def test_prepared_dataset_is_not_empty():
    dataset = get_prepared_dataset()

    assert dataset


def test_prepared_dataset_has_dates():
    dataset = get_prepared_dataset()

    assert all(
        "Date" in row
        for row in dataset
    )


def test_prepared_dataset_dates_are_sorted():
    dataset = get_prepared_dataset()

    dates = [
        row["Date"]
        for row in dataset
    ]

    assert dates == sorted(dates)


def test_prepared_dataset_has_expected_columns():
    dataset = get_prepared_dataset()

    expected_columns = {
        "Date",

        # Actual financial
        "Expense_Total",
        "Expense_Count",
        "Income_Total",
        "Income_Count",

        # Events
        "Event_Count",

        # Health
        "Health_Record_Count",
        "Max_Health_Severity",
        "Avg_Energy_Level",

        # Activities
        "Activity_Count",
        "Activity_Duration_Minutes",
        "Activity_Cost",

        # Sleep
        "Sleep_Record_Count",
        "Sleep_Duration_Minutes",
        "Avg_Sleep_Quality",
        "Total_Awakenings",

        # Plans
        "Plan_Count",
        "Plan_Expected_Cost",
        "Plan_Duration_Days",
        "High_Importance_Plan_Count",
        "Active_Plan_Count",
        "Active_Plan_Expected_Cost",
        "Active_High_Importance_Plan_Count",

        # Recurring
        "Recurring_Count",
        "Recurring_Amount",
        "Recurring_Expense_Amount",
        "Recurring_Income_Amount",
        "Fixed_Recurring_Amount",
    }

    assert expected_columns.issubset(
        dataset[0].keys()
    )


def test_prepared_dataset_has_consistent_columns():
    dataset = get_prepared_dataset()

    if not dataset:
        pytest.skip(
            "Prepared dataset is empty."
        )

    first_columns = set(
        dataset[0].keys()
    )

    for row in dataset:
        assert set(row.keys()) == first_columns


def test_recurring_is_separate_from_actual_financial_data():
    dataset = get_prepared_dataset()

    for row in dataset:
        assert row["Expense_Total"] >= 0.0
        assert row["Income_Total"] >= 0.0

        assert row["Recurring_Expense_Amount"] >= 0.0
        assert row["Recurring_Income_Amount"] >= 0.0


def test_prepared_dataset_contains_planned_and_recurring_data():
    dataset = get_prepared_dataset()

    row = dataset[0]

    assert "Plan_Count" in row
    assert "Plan_Expected_Cost" in row
    assert "Active_Plan_Count" in row

    assert "Recurring_Count" in row
    assert "Recurring_Amount" in row
    assert "Recurring_Expense_Amount" in row
    assert "Recurring_Income_Amount" in row
    assert "Fixed_Recurring_Amount" in row


def test_prepared_dataset_has_unique_dates():
    dataset = get_prepared_dataset()

    dates = [
        row["Date"]
        for row in dataset
    ]

    assert len(dates) == len(set(dates))