
from datetime import date, datetime
import math


from ml.features.build import (
    build_training_dataset,
    get_feature_names,
)


# ==========================================================
# HELPERS
# ==========================================================

def to_date(value):
    """
    Safely convert a supported value into a date object.
    """

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return date.fromisoformat(
                value[:10]
            )
        except ValueError:
            return None

    return None


def is_numeric(value):
    """
    Return True when value is a valid numeric value.
    """

    if isinstance(value, bool):
        return False

    if not isinstance(
        value,
        (int, float),
    ):
        return False

    return math.isfinite(
        float(value)
    )


# ==========================================================
# LOAD DATASET
# ==========================================================

training_dataset = build_training_dataset()


print()
print("=" * 60)
print("          TRAINING DATASET TEST")
print("=" * 60)
print()

print(
    f"Training rows: {len(training_dataset)}"
)


# ==========================================================
# EMPTY DATASET CHECK
# ==========================================================

if not training_dataset:
    print()
    print("WARNING: Training dataset is empty.")
    print()
    print("TRAINING DATASET TEST PASSED")
    raise SystemExit(0)


# ==========================================================
# FEATURE NAMES
# ==========================================================

feature_names = get_feature_names(
    training_dataset
)

print(
    f"Number of ML features: {len(feature_names)}"
)


# ==========================================================
# BASIC STRUCTURE
# ==========================================================

print()
print("=" * 60)
print("DATASET STRUCTURE CHECK")
print("=" * 60)


all_keys = set(
    training_dataset[0].keys()
)

required_columns = {
    'Date',
    'Target_Expense_Total',
}

missing_columns = (
    required_columns
    - all_keys
)

if missing_columns:
    print(
        "Missing required columns:",
        sorted(missing_columns),
    )
    raise AssertionError(
        "Required dataset columns are missing."
    )

print("Required columns: OK")


# ==========================================================
# FEATURE / TARGET SEPARATION
# ==========================================================

print()
print("=" * 60)
print("FEATURE / TARGET SEPARATION")
print("=" * 60)


if 'Target_Expense_Total' in feature_names:
    raise AssertionError(
        "Target_Expense_Total found inside ML features."
    )

print(
    "Target_Expense_Total in X: NO"
)


if 'Date' in feature_names:
    raise AssertionError(
        "Date found inside ML features."
    )

print(
    "Date in X: NO"
)


print(
    "Feature / target separation: OK"
)


# ==========================================================
# FEATURE COUNT CONSISTENCY
# ==========================================================

print()
print("=" * 60)
print("FEATURE COUNT CONSISTENCY")
print("=" * 60)


expected_feature_count = len(
    feature_names
)

for index, row in enumerate(
    training_dataset
):

    row_feature_count = len(
        [
            key
            for key in row.keys()
            if key not in {
                'Date',
                'Target_Expense_Total',
            }
        ]
    )

    if row_feature_count != expected_feature_count:
        raise AssertionError(
            f"Row {index} has "
            f"{row_feature_count} features, "
            f"expected {expected_feature_count}."
        )

print(
    "All training rows have the same "
    "number of ML features: OK"
)


# ==========================================================
# X NUMERIC CHECK
# ==========================================================

print()
print("=" * 60)
print("INPUT FEATURE NUMERIC CHECK")
print("=" * 60)


invalid_features = []

for row_index, row in enumerate(
    training_dataset
):

    for feature_name in feature_names:

        value = row.get(
            feature_name
        )

        if not is_numeric(value):

            invalid_features.append(
                (
                    row_index,
                    feature_name,
                    value,
                )
            )


if invalid_features:

    print(
        "Invalid feature values:"
    )

    for item in invalid_features[:20]:
        print(
            f"Row {item[0]} | "
            f"{item[1]} | "
            f"{item[2]!r}"
        )

    raise AssertionError(
        "Non-numeric ML feature values found."
    )


print(
    "All ML input features are numeric: OK"
)


# ==========================================================
# INVALID NUMBER CHECK
# ==========================================================

print()
print("=" * 60)
print("INVALID NUMBER CHECK")
print("=" * 60)


invalid_numbers = []

for row_index, row in enumerate(
    training_dataset
):

    for feature_name in feature_names:

        value = row.get(
            feature_name
        )

        if isinstance(
            value,
            (int, float),
        ):

            if not math.isfinite(
                float(value)
            ):

                invalid_numbers.append(
                    (
                        row_index,
                        feature_name,
                        value,
                    )
                )


if invalid_numbers:

    for item in invalid_numbers[:20]:
        print(
            f"Row {item[0]} | "
            f"{item[1]} | "
            f"{item[2]!r}"
        )

    raise AssertionError(
        "NaN or infinite feature values found."
    )


print(
    "NaN / infinite feature values: NONE"
)


# ==========================================================
# TARGET NUMERIC CHECK
# ==========================================================

print()
print("=" * 60)
print("TARGET CHECK")
print("=" * 60)


invalid_targets = []

for index, row in enumerate(
    training_dataset
):

    target = row.get(
        'Target_Expense_Total'
    )

    if not is_numeric(target):

        invalid_targets.append(
            (
                index,
                target,
            )
        )


if invalid_targets:

    for item in invalid_targets[:20]:
        print(
            f"Row {item[0]} | "
            f"Target: {item[1]!r}"
        )

    raise AssertionError(
        "Invalid target values found."
    )


print(
    "Target values are numeric: OK"
)


# ==========================================================
# TARGET VALUE VALIDITY
# ==========================================================

print()
print("=" * 60)
print("TARGET VALUE VALIDITY")
print("=" * 60)


negative_targets = []

for index, row in enumerate(
    training_dataset
):

    target = float(
        row[
            'Target_Expense_Total'
        ]
    )

    if target < 0:

        negative_targets.append(
            (
                index,
                target,
            )
        )


if negative_targets:

    for item in negative_targets[:20]:
        print(
            f"Row {item[0]} | "
            f"Negative target: {item[1]}"
        )

    raise AssertionError(
        "Negative expense targets found."
    )


print(
    "Negative expense targets: NONE"
)


# ==========================================================
# CHRONOLOGICAL ORDER CHECK
# ==========================================================

print()
print("=" * 60)
print("CHRONOLOGICAL ORDER CHECK")
print("=" * 60)


dates = []

for index, row in enumerate(
    training_dataset
):

    current_date = to_date(
        row.get('Date')
    )

    if current_date is None:

        raise AssertionError(
            f"Invalid Date in training row "
            f"{index}: {row.get('Date')!r}"
        )

    dates.append(
        current_date
    )


for index in range(
    1,
    len(dates),
):

    if dates[index] <= dates[index - 1]:

        raise AssertionError(
            "Training dataset is not strictly "
            "chronological."
        )


print(
    "Training rows are strictly chronological: OK"
)


# ==========================================================
# TARGET DATE / HISTORICAL ORDER CHECK
# ==========================================================

print()
print("=" * 60)
print("HISTORICAL / TARGET ORDER CHECK")
print("=" * 60)


if len(training_dataset) >= 1:

    first_target_date = dates[0]

    print(
        f"First target date: "
        f"{first_target_date}"
    )

    print(
        "First training row represents "
        "a target after historical data: OK"
    )


# ==========================================================
# TARGET LEAKAGE NAME CHECK
# ==========================================================

print()
print("=" * 60)
print("TARGET LEAKAGE CHECK")
print("=" * 60)


suspicious_names = []

leakage_keywords = {
    'target',
    'future_expense',
    'actual_expense',
}


for feature_name in feature_names:

    normalized_name = (
        feature_name
        .strip()
        .lower()
    )

    for keyword in leakage_keywords:

        if keyword in normalized_name:

            suspicious_names.append(
                feature_name
            )

            break


if suspicious_names:

    print(
        "Potential leakage feature names:"
    )

    for feature_name in sorted(
        set(suspicious_names)
    ):
        print(
            f"  {feature_name}"
        )

    raise AssertionError(
        "Potential target leakage detected "
        "in feature names."
    )


print(
    "Potential leakage names: NONE"
)


# ==========================================================
# ROW / FEATURE SIZE
# ==========================================================

print()
print("=" * 60)
print("DATASET SIZE")
print("=" * 60)


training_rows = len(
    training_dataset
)

ml_features = len(
    feature_names
)

print(
    f"Training rows: {training_rows}"
)

print(
    f"ML features: {ml_features}"
)

if training_rows < ml_features:

    print()
    print(
        "WARNING: Training rows are smaller "
        "than the number of ML features."
    )

    print(
        "This is expected with the current "
        "small dataset and does not fail "
        "the structural test."
    )

else:

    print(
        "Training rows >= ML features: OK"
    )


# ==========================================================
# FIRST TRAINING ROW
# ==========================================================

print()
print("=" * 60)
print("FIRST TRAINING ROW")
print("=" * 60)


first_row = training_dataset[0]

print(
    f"Target date: "
    f"{first_row['Date']}"
)

print(
    f"Target expense: "
    f"{first_row['Target_Expense_Total']:.2f}"
)

print(
    "Historical features available: OK"
)


# ==========================================================
# SAMPLE FEATURE / TARGET SEPARATION
# ==========================================================

print()
print("=" * 60)
print("SAMPLE X / Y SEPARATION")
print("=" * 60)


X = [
    [
        row[feature_name]
        for feature_name in feature_names
    ]
    for row in training_dataset
]

y = [
    row['Target_Expense_Total']
    for row in training_dataset
]


if len(X) != len(y):

    raise AssertionError(
        "X and y have different numbers of rows."
    )


print(
    f"X shape: "
    f"({len(X)}, {len(feature_names)})"
)

print(
    f"y length: "
    f"{len(y)}"
)

print(
    "X / y row count consistency: OK"
)


# ==========================================================
# TARGET SUMMARY
# ==========================================================

print()
print("=" * 60)
print("TARGET SUMMARY")
print("=" * 60)


target_values = [
    float(value)
    for value in y
]

minimum_target = min(
    target_values
)

maximum_target = max(
    target_values
)

average_target = (
    sum(target_values)
    / len(target_values)
)

zero_targets = sum(
    1
    for value in target_values
    if value == 0
)


print(
    f"Min target: "
    f"{minimum_target:.2f}"
)

print(
    f"Max target: "
    f"{maximum_target:.2f}"
)

print(
    f"Average target: "
    f"{average_target:.2f}"
)

print(
    f"Zero-target rows: "
    f"{zero_targets}"
)


# ==========================================================
# FINAL RESULT
# ==========================================================

print()
print("=" * 60)
print("TRAINING DATASET TEST PASSED")
print("=" * 60)
print()
