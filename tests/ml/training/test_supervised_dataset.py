from datetime import date, timedelta

from ml.training.dataset import (
    temporal_train_test_split,
    split_features_and_target,
)


# =========================================================
# HELPERS
# =========================================================

def make_row(day, **values):
    row = {
        'Date': day,
        'Previous_Day_Expense': 100.0,
        'Rolling_7D_Avg_Expense': 120.0,
        'Day_of_Week': 5,
        'Known_Future_Plan_Count': 0,
        'Target_Expense_Total': 500.0,
    }

    row.update(values)

    return row


# =========================================================
# TEMPORAL ORDER
# =========================================================

def test_temporal_split_orders_data_chronologically():

    rows = [
        make_row(date(2026, 8, 15)),
        make_row(date(2026, 8, 10)),
        make_row(date(2026, 8, 20)),
        make_row(date(2026, 8, 12)),
    ]

    training, test = temporal_train_test_split(
        rows,
        test_ratio=0.25,
    )

    training_dates = [
        row['Date']
        for row in training
    ]

    test_dates = [
        row['Date']
        for row in test
    ]

    assert training_dates == [
        date(2026, 8, 10),
        date(2026, 8, 12),
        date(2026, 8, 15),
    ]

    assert test_dates == [
        date(2026, 8, 20),
    ]


# =========================================================
# NO SHUFFLING / TEMPORAL BOUNDARY
# =========================================================

def test_temporal_split_has_strict_chronological_boundary():

    rows = [
        make_row(
            date(2026, 8, 1)
        ),
        make_row(
            date(2026, 8, 2)
        ),
        make_row(
            date(2026, 8, 3)
        ),
        make_row(
            date(2026, 8, 4)
        ),
        make_row(
            date(2026, 8, 5)
        ),
    ]

    training, test = temporal_train_test_split(
        rows,
        test_ratio=0.2,
    )

    assert training
    assert test

    assert max(
        row['Date']
        for row in training
    ) < min(
        row['Date']
        for row in test
    )


# =========================================================
# NO OVERLAP
# =========================================================

def test_temporal_split_has_no_row_overlap():

    rows = [
        make_row(
            date(2026, 8, day)
        )
        for day in range(1, 11)
    ]

    training, test = temporal_train_test_split(
        rows,
        test_ratio=0.2,
    )

    training_dates = {
        row['Date']
        for row in training
    }

    test_dates = {
        row['Date']
        for row in test
    }

    assert training_dates.isdisjoint(
        test_dates
    )


# =========================================================
# EXPECTED TEST SIZE
# =========================================================

def test_temporal_split_respects_test_ratio():

    rows = [
        make_row(
            date(2026, 8, day)
        )
        for day in range(1, 11)
    ]

    training, test = temporal_train_test_split(
        rows,
        test_ratio=0.2,
    )

    assert len(training) == 8
    assert len(test) == 2


# =========================================================
# MINIMUM DATA SAFETY
# =========================================================

def test_temporal_split_with_one_row():

    rows = [
        make_row(
            date(2026, 8, 1)
        )
    ]

    training, test = temporal_train_test_split(
        rows
    )

    assert len(training) == 1
    assert test == []


# =========================================================
# EMPTY DATA SAFETY
# =========================================================

def test_temporal_split_with_empty_data():

    training, test = temporal_train_test_split(
        []
    )

    assert training == []
    assert test == []


# =========================================================
# X / Y SEPARATION
# =========================================================

def test_split_features_and_target_separates_x_and_y():

    rows = [
        make_row(
            date(2026, 8, 1),
            Target_Expense_Total=500.0,
        ),
        make_row(
            date(2026, 8, 2),
            Target_Expense_Total=700.0,
        ),
    ]

    X, y = split_features_and_target(
        rows
    )

    assert len(X) == 2
    assert len(y) == 2

    assert y == [
        500.0,
        700.0,
    ]


# =========================================================
# DATE MUST NOT ENTER X
# =========================================================

def test_date_is_not_a_model_feature():

    rows = [
        make_row(
            date(2026, 8, 1)
        )
    ]

    X, y = split_features_and_target(
        rows
    )

    assert X

    # Date must not appear as a feature.
    assert date(2026, 8, 1) not in X[0]


# =========================================================
# TARGET MUST NOT ENTER X
# =========================================================

def test_target_is_not_a_model_feature():

    rows = [
        make_row(
            date(2026, 8, 1),
            Target_Expense_Total=999999.0,
        )
    ]

    X, y = split_features_and_target(
        rows
    )

    assert y == [999999.0]

    # Target value must not appear as X.
    assert 999999.0 not in X[0]


# =========================================================
# MULTI-TARGET SAFETY
# =========================================================

def test_all_target_columns_must_be_excluded_from_x():

    rows = [
        make_row(
            date(2026, 8, 1),
            Target_Expense_Total=500.0,
            Target_High_Expense_1D=1,
            Target_Working_Day_1D=1,
            Target_High_Stress_1D=0,
        )
    ]

    X, y = split_features_and_target(
        rows,
        target_name='Target_Expense_Total',
    )

    # Current implementation is expected to fail here
    # if other Target_* columns are included as features.
    #
    # This test protects the future Multi-Target architecture.

    assert 1 not in X[0]