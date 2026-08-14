
from collections import Counter

from ml.features.build import (
    build_training_dataset,
    get_feature_names,
)


# ==========================================================
# CONFIGURATION
# ==========================================================

LOW_VARIANCE_THRESHOLD = 0.01


# ==========================================================
# HELPERS
# ==========================================================

def is_finite_number(value):
    """
    Check whether a value is a finite numeric value.
    """

    try:
        value = float(value)

    except (
        TypeError,
        ValueError,
    ):
        return False

    return value == value and abs(value) != float('inf')


def feature_values(
    data,
    feature_name,
):
    """
    Return all values for one feature.
    """

    return [
        row.get(
            feature_name,
            0,
        )
        for row in data
    ]


def numeric_variance(values):
    """
    Calculate population variance.

    Returns 0.0 when fewer than two values exist.
    """

    if len(values) < 2:
        return 0.0

    numeric_values = [
        float(value)
        for value in values
    ]

    mean = (
        sum(numeric_values)
        / len(numeric_values)
    )

    return sum(
        (
            value - mean
        ) ** 2
        for value in numeric_values
    ) / len(numeric_values)


# ==========================================================
# HEADER
# ==========================================================

print()
print('=' * 60)
print(
    '          FEATURE QUALITY TEST'
)
print('=' * 60)


# ==========================================================
# BUILD DATASET
# ==========================================================

data = build_training_dataset()

if not data:

    print()
    print(
        'ERROR: Training dataset is empty.'
    )

    raise SystemExit(1)


feature_names = get_feature_names(
    data
)


# ==========================================================
# BASIC INFORMATION
# ==========================================================

print()
print(
    f'Training rows: {len(data)}'
)

print(
    f'Number of ML features: '
    f'{len(feature_names)}'
)


# ==========================================================
# FEATURE NAME VALIDATION
# ==========================================================

print()
print('=' * 60)
print(
    'FEATURE NAME VALIDATION'
)
print('=' * 60)

duplicate_names = [
    name
    for name, count
    in Counter(feature_names).items()
    if count > 1
]

if duplicate_names:

    print(
        'Duplicate feature names: FOUND'
    )

    for name in duplicate_names:
        print(
            f'  {name}'
        )

    raise SystemExit(1)

print(
    'Duplicate feature names: NONE'
)


# ==========================================================
# INVALID NUMBER CHECK
# ==========================================================

print()
print('=' * 60)
print(
    'INVALID NUMBER CHECK'
)
print('=' * 60)

invalid_values = []

for row_index, row in enumerate(data):

    for feature_name in feature_names:

        value = row.get(
            feature_name,
            0,
        )

        if not is_finite_number(
            value
        ):

            invalid_values.append(
                (
                    row_index,
                    feature_name,
                    value,
                )
            )

if invalid_values:

    print(
        'Invalid numeric values: FOUND'
    )

    for (
        row_index,
        feature_name,
        value,
    ) in invalid_values[:20]:

        print(
            f'  Row {row_index} | '
            f'{feature_name} | '
            f'{value}'
        )

    raise SystemExit(1)

print(
    'NaN / infinite / non-numeric values: NONE'
)


# ==========================================================
# TARGET CHECK
# ==========================================================

print()
print('=' * 60)
print(
    'TARGET DISTRIBUTION'
)
print('=' * 60)

targets = [
    float(
        row.get(
            'Target_Expense_Total'
        ) or 0.0
    )
    for row in data
]

print(
    f'Min target: {min(targets):.2f}'
)

print(
    f'Max target: {max(targets):.2f}'
)

print(
    f'Average target: '
    f'{sum(targets) / len(targets):.2f}'
)

print(
    f'Zero-target rows: '
    f'{sum(value == 0 for value in targets)}'
)


# ==========================================================
# CONSTANT FEATURES
# ==========================================================

print()
print('=' * 60)
print(
    'CONSTANT FEATURES'
)
print('=' * 60)

constant_features = []

for feature_name in feature_names:

    values = feature_values(
        data,
        feature_name,
    )

    unique_values = set(
        values
    )

    if len(unique_values) <= 1:

        constant_features.append(
            feature_name
        )

if constant_features:

    print(
        f'Constant features: '
        f'{len(constant_features)}'
    )

    for feature_name in constant_features:

        print(
            f'  {feature_name}'
        )

else:

    print(
        'Constant features: NONE'
    )


# ==========================================================
# ALL-ZERO FEATURES
# ==========================================================

print()
print('=' * 60)
print(
    'ALL-ZERO FEATURES'
)
print('=' * 60)

zero_features = []

for feature_name in feature_names:

    values = feature_values(
        data,
        feature_name,
    )

    if all(
        float(value) == 0.0
        for value in values
    ):

        zero_features.append(
            feature_name
        )

if zero_features:

    print(
        f'All-zero features: '
        f'{len(zero_features)}'
    )

    for feature_name in zero_features:

        print(
            f'  {feature_name}'
        )

else:

    print(
        'All-zero features: NONE'
    )


# ==========================================================
# LOW VARIANCE FEATURES
# ==========================================================

print()
print('=' * 60)
print(
    'LOW VARIANCE FEATURES'
)
print('=' * 60)

low_variance_features = []

for feature_name in feature_names:

    values = feature_values(
        data,
        feature_name,
    )

    variance = numeric_variance(
        values
    )

    if (
        variance > 0.0
        and variance
        < LOW_VARIANCE_THRESHOLD
    ):

        low_variance_features.append(
            (
                feature_name,
                variance,
            )
        )

if low_variance_features:

    print(
        f'Low-variance features: '
        f'{len(low_variance_features)}'
    )

    for (
        feature_name,
        variance,
    ) in low_variance_features:

        print(
            f'  {feature_name}: '
            f'variance={variance:.8f}'
        )

else:

    print(
        'Low-variance features: NONE'
    )


# ==========================================================
# UNIQUE VALUE COUNTS
# ==========================================================

print()
print('=' * 60)
print(
    'FEATURE CARDINALITY'
)
print('=' * 60)

for feature_name in feature_names:

    values = feature_values(
        data,
        feature_name,
    )

    unique_count = len(
        set(values)
    )

    print(
        f'{feature_name}: '
        f'{unique_count} unique value(s)'
    )


# ==========================================================
# DUPLICATE FEATURE VALUES
# ==========================================================

print()
print('=' * 60)
print(
    'DUPLICATE FEATURE COLUMNS'
)
print('=' * 60)

feature_signatures = {}

for feature_name in feature_names:

    signature = tuple(
        feature_values(
            data,
            feature_name,
        )
    )

    feature_signatures.setdefault(
        signature,
        []
    ).append(
        feature_name
    )

duplicate_groups = [
    names
    for names in feature_signatures.values()
    if len(names) > 1
]

if duplicate_groups:

    print(
        f'Duplicate-value feature groups: '
        f'{len(duplicate_groups)}'
    )

    for group in duplicate_groups:

        print(
            '  ' +
            ', '.join(group)
        )

else:

    print(
        'Duplicate-value feature groups: NONE'
    )


# ==========================================================
# LEAKAGE CHECK
# ==========================================================

print()
print('=' * 60)
print(
    'LEAKAGE CHECK'
)
print('=' * 60)

leakage_names = []

for feature_name in feature_names:

    normalized = (
        feature_name
        .lower()
    )

    if (
        'target' in normalized
        or 'future' in normalized
        or 'current_day' in normalized
    ):

        leakage_names.append(
            feature_name
        )

if leakage_names:

    print(
        'Potential leakage names: FOUND'
    )

    for feature_name in leakage_names:

        print(
            f'  {feature_name}'
        )

    raise SystemExit(1)

print(
    'Potential leakage names: NONE'
)


# ==========================================================
# FEATURE / ROW RATIO
# ==========================================================

print()
print('=' * 60)
print(
    'FEATURE / DATASET SIZE'
)
print('=' * 60)

feature_count = len(
    feature_names
)

row_count = len(
    data
)

ratio = (
    feature_count
    / row_count
    if row_count
    else 0.0
)

print(
    f'Features per training row: '
    f'{ratio:.2f}'
)

if row_count < feature_count:

    print()
    print(
        'WARNING: Number of training rows '
        'is smaller than the number of ML features.'
    )

    print(
        'This is acceptable for feature validation, '
        'but the dataset is currently too small '
        'for reliable model training.'
    )


# ==========================================================
# FEATURE COVERAGE
# ==========================================================

print()
print('=' * 60)
print(
    'FEATURE COVERAGE'
)
print('=' * 60)

coverage_counts = []

for feature_name in feature_names:

    values = feature_values(
        data,
        feature_name,
    )

    non_zero_count = sum(
        float(value) != 0.0
        for value in values
    )

    coverage_counts.append(
        (
            feature_name,
            non_zero_count,
        )
    )

zero_coverage_features = [
    (
        feature_name,
        count,
    )
    for (
        feature_name,
        count,
    ) in coverage_counts
    if count == 0
]

if zero_coverage_features:

    print(
        f'Features with no observed '
        f'non-zero values: '
        f'{len(zero_coverage_features)}'
    )

    for (
        feature_name,
        _,
    ) in zero_coverage_features:

        print(
            f'  {feature_name}'
        )

else:

    print(
        'All features have at least '
        'one non-zero observation.'
    )


# ==========================================================
# SUMMARY
# ==========================================================

print()
print('=' * 60)
print(
    'QUALITY SUMMARY'
)
print('=' * 60)

print(
    f'Training rows: '
    f'{len(data)}'
)

print(
    f'ML features: '
    f'{len(feature_names)}'
)

print(
    f'Constant features: '
    f'{len(constant_features)}'
)

print(
    f'All-zero features: '
    f'{len(zero_features)}'
)

print(
    f'Low-variance features: '
    f'{len(low_variance_features)}'
)

print(
    f'Duplicate-value groups: '
    f'{len(duplicate_groups)}'
)

print(
    f'No-coverage features: '
    f'{len(zero_coverage_features)}'
)

print()
print(
    'IMPORTANT:'
)

print(
    'Constant, zero, or low-variance features are '
    'reported as observations only.'
)

print(
    'They are NOT automatically removed because '
    'the current dataset contains very few training rows.'
)

print()
print('=' * 60)
print(
    'FEATURE QUALITY TEST PASSED'
)
print('=' * 60)