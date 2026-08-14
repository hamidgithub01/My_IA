from datetime import date, timedelta
import math

from ml.features.build import (
    build_training_dataset,
    get_feature_names,
)


# =========================================================
# HELPERS
# =========================================================

def is_numeric(value):
    """
    Check whether a value is a valid numeric value.
    """

    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


# =========================================================
# TEST DATASET
# =========================================================

print()
print("=" * 60)
print("          FEATURE ENGINEERING TEST")
print("=" * 60)


data = build_training_dataset()


print()
print("Training rows:", len(data))


if not data:
    raise AssertionError(
        "Feature Engineering returned an empty dataset."
    )


# =========================================================
# FEATURE NAMES
# =========================================================

feature_names = get_feature_names(
    data
)


print(
    "Number of ML features:",
    len(feature_names),
)


if not feature_names:
    raise AssertionError(
        "No ML features were generated."
    )


# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_columns = {
    'Date',
    'Target_Expense_Total',
}


first_row = data[0]


missing_columns = (
    required_columns
    - set(first_row.keys())
)


if missing_columns:

    raise AssertionError(
        "Missing required columns: "
        + str(
            sorted(
                missing_columns
            )
        )
    )


print()
print("Required columns: OK")


# =========================================================
# TARGET LEAKAGE CHECK
# =========================================================

print()
print("=" * 60)
print("TARGET LEAKAGE CHECK")
print("=" * 60)


if 'Target_Expense_Total' in feature_names:

    raise AssertionError(
        "Target_Expense_Total is present "
        "inside ML features."
    )


print(
    "Target_Expense_Total in features: NO"
)


# =========================================================
# DATE CHECK
# =========================================================

if 'Date' in feature_names:

    raise AssertionError(
        "Date must not be included in ML features."
    )


print(
    "Date in ML features: NO"
)


# =========================================================
# FEATURE CONSISTENCY
# =========================================================

expected_feature_count = len(
    feature_names
)


for index, row in enumerate(data):

    current_features = [
        key
        for key in row.keys()
        if key not in {
            'Date',
            'Target_Expense_Total',
        }
    ]

    if len(current_features) != expected_feature_count:

        raise AssertionError(
            f"Feature count mismatch "
            f"at row {index}. "
            f"Expected "
            f"{expected_feature_count}, "
            f"got "
            f"{len(current_features)}."
        )


print(
    "Feature count consistency: OK"
)


# =========================================================
# NUMERIC FEATURE CHECK
# =========================================================

print()
print("=" * 60)
print("NUMERIC FEATURE CHECK")
print("=" * 60)


non_numeric = []


for row_index, row in enumerate(data):

    for feature_name in feature_names:

        value = row.get(
            feature_name
        )

        if not is_numeric(value):

            non_numeric.append(
                (
                    row_index,
                    feature_name,
                    value,
                )
            )


if non_numeric:

    print()

    for item in non_numeric[:20]:

        print(
            "Row:",
            item[0],
            "| Feature:",
            item[1],
            "| Value:",
            repr(item[2]),
        )

    raise AssertionError(
        "Non-numeric ML features detected."
    )


print(
    "All ML features are numeric: OK"
)


# =========================================================
# INVALID NUMBER CHECK
# =========================================================

print()
print("=" * 60)
print("INVALID NUMBER CHECK")
print("=" * 60)


invalid_values = []


for row_index, row in enumerate(data):

    for feature_name in feature_names:

        value = row.get(
            feature_name
        )

        if not math.isfinite(
            float(value)
        ):

            invalid_values.append(
                (
                    row_index,
                    feature_name,
                    value,
                )
            )


if invalid_values:

    raise AssertionError(
        "NaN or infinite values detected: "
        + str(
            invalid_values[:20]
        )
    )


print(
    "NaN / infinite values: NONE"
)


# =========================================================
# TARGET CHECK
# =========================================================

print()
print("=" * 60)
print("TARGET CHECK")
print("=" * 60)


for row_index, row in enumerate(data):

    target = row.get(
        'Target_Expense_Total'
    )

    if not is_numeric(target):

        raise AssertionError(
            f"Invalid target value "
            f"at row {row_index}: "
            f"{target!r}"
        )


print(
    "Target values are numeric: OK"
)


# =========================================================
# CHRONOLOGICAL ORDER CHECK
# =========================================================

print()
print("=" * 60)
print("CHRONOLOGICAL ORDER CHECK")
print("=" * 60)


dates = [
    row['Date']
    for row in data
]


for index in range(
    1,
    len(dates),
):

    if dates[index] <= dates[index - 1]:

        raise AssertionError(
            "Training dataset is not "
            "strictly chronological."
        )


print(
    "Training rows are chronological: OK"
)


# =========================================================
# FIRST ROW CHECK
# =========================================================

print()
print("=" * 60)
print("FIRST TRAINING ROW CHECK")
print("=" * 60)


first_date = data[0]['Date']


print(
    "First target date:",
    first_date,
)


if not isinstance(
    first_date,
    date,
):

    raise AssertionError(
        "Training Date is not a date object."
    )


print(
    "First training row starts after "
    "historical data: OK"
)


# =========================================================
# LAG STRUCTURE CHECK
# =========================================================

print()
print("=" * 60)
print("LAG FEATURE CHECK")
print("=" * 60)


expected_lag_features = {
    'Lag_1_Expense',
    'Lag_2_Expense',
    'Lag_3_Expense',
    'Lag_7_Expense',
    'Lag_14_Expense',
    'Lag_28_Expense',

    'Lag_1_Income',
    'Lag_2_Income',
    'Lag_7_Income',
    'Lag_14_Income',
    'Lag_28_Income',

    'Lag_1_Events',
    'Lag_2_Events',
    'Lag_7_Events',
    'Lag_14_Events',
    'Lag_28_Events',

    'Lag_1_Health_Severity',
    'Lag_7_Health_Severity',
    'Lag_14_Health_Severity',

    'Lag_1_Activity_Duration',
    'Lag_7_Activity_Duration',
    'Lag_14_Activity_Duration',

    'Lag_1_Sleep_Duration',
    'Lag_7_Sleep_Duration',
    'Lag_14_Sleep_Duration',
}


missing_lag_features = (
    expected_lag_features
    - set(feature_names)
)


if missing_lag_features:

    raise AssertionError(
        "Missing lag features: "
        + str(
            sorted(
                missing_lag_features
            )
        )
    )


print(
    "Expected lag features: OK"
)


# =========================================================
# ROLLING STRUCTURE CHECK
# =========================================================

print()
print("=" * 60)
print("ROLLING FEATURE CHECK")
print("=" * 60)


expected_rolling_features = {
    'Rolling_3D_Avg_Expense',
    'Rolling_7D_Avg_Expense',
    'Rolling_14D_Avg_Expense',
    'Rolling_30D_Avg_Expense',

    'Rolling_3D_Avg_Income',
    'Rolling_7D_Avg_Income',
    'Rolling_14D_Avg_Income',
    'Rolling_30D_Avg_Income',

    'Rolling_3D_Avg_Balance',
    'Rolling_7D_Avg_Balance',
    'Rolling_14D_Avg_Balance',
    'Rolling_30D_Avg_Balance',

    'Rolling_3D_Avg_Health_Severity',
    'Rolling_7D_Avg_Health_Severity',
    'Rolling_14D_Avg_Health_Severity',
    'Rolling_30D_Avg_Health_Severity',

    'Rolling_3D_Avg_Energy',
    'Rolling_7D_Avg_Energy',
    'Rolling_14D_Avg_Energy',

    'Rolling_3D_Avg_Activity_Duration',
    'Rolling_7D_Avg_Activity_Duration',
    'Rolling_14D_Avg_Activity_Duration',
    'Rolling_30D_Avg_Activity_Duration',

    'Rolling_3D_Avg_Sleep_Duration',
    'Rolling_7D_Avg_Sleep_Duration',
    'Rolling_14D_Avg_Sleep_Duration',
    'Rolling_30D_Avg_Sleep_Duration',

    'Rolling_3D_Avg_Sleep_Quality',
    'Rolling_7D_Avg_Sleep_Quality',
    'Rolling_14D_Avg_Sleep_Quality',
    'Rolling_30D_Avg_Sleep_Quality',
}


missing_rolling_features = (
    expected_rolling_features
    - set(feature_names)
)


if missing_rolling_features:

    raise AssertionError(
        "Missing rolling features: "
        + str(
            sorted(
                missing_rolling_features
            )
        )
    )


print(
    "Expected rolling features: OK"
)


# =========================================================
# FEATURE SAMPLE
# =========================================================

print()
print("=" * 60)
print("FIRST FEATURE ROW")
print("=" * 60)


for feature_name in feature_names:

    print(
        f"{feature_name}: "
        f"{first_row[feature_name]}"
    )


print()
print(
    "Target_Expense_Total:",
    first_row[
        'Target_Expense_Total'
    ],
)


# =========================================================
# FINAL RESULT
# =========================================================

print()
print("=" * 60)
print("FEATURE ENGINEERING TEST PASSED")
print("=" * 60)
print()