import pytest
from math import isnan

from ml.targets.build import build_target_dataset

# =========================================================
# PYTEST FIXTURE
# =========================================================

@pytest.fixture
def dataset():
    """
    Build the target dataset used by all target-quality tests.
    
    The dataset is generated through the real target-building
    pipeline. No hard-coded target values are used here.
    """
    return build_target_dataset()


# =========================================================
# EXPECTED TARGET STRUCTURE
# =========================================================

HORIZONS = [
    '1D',
    '2D',
    '3D',
    '4D',
    '5D',
    '6D',
    '7D',
    '8_15D',
    '16_30D',
    '30D',
]

TARGET_PREFIXES = [
    'Target_Has_Activity_',
    'Target_High_Activity_',
    'Target_Long_Activity_',
    'Target_High_Stress_',
    'Target_Moderate_or_High_Stress_',
    'Target_Low_Sleep_',
    'Target_Very_Low_Sleep_',
    'Target_High_Social_Activity_',
    'Target_Moderate_or_High_Social_Activity_',
    'Target_Working_Day_',
    'Target_Difficult_Behavioral_Day_',
    'Target_Has_Event_',
    'Target_Multiple_Events_',
    'Target_Has_Special_Event_',
    'Target_Expense_Total_',
    'Target_Income_Total_',
    'Target_Balance_',
    'Target_Expense_Days_',
    'Target_Income_Days_',
    'Target_High_Expense_',
    'Target_Health_Problem_',
    'Target_High_Health_Severity_',
    'Target_Low_Energy_',
    'Target_Significant_Health_Day_',
    'Target_Has_Location_',
    'Target_Location_Changed_',
    'Target_Same_Location_',
    'Target_Location_',
    'Target_Busy_Day_',
    'Target_Financial_Activity_',
    'Target_Difficult_Day_',
    'Target_Active_Day_',
    'Target_Travel_Day_',
    'Target_Special_Day_',
]

BINARY_PREFIXES = [
    'Target_Has_Activity_',
    'Target_High_Activity_',
    'Target_Long_Activity_',
    'Target_High_Stress_',
    'Target_Moderate_or_High_Stress_',
    'Target_Low_Sleep_',
    'Target_Very_Low_Sleep_',
    'Target_High_Social_Activity_',
    'Target_Moderate_or_High_Social_Activity_',
    'Target_Working_Day_',
    'Target_Difficult_Behavioral_Day_',
    'Target_Has_Event_',
    'Target_Multiple_Events_',
    'Target_Has_Special_Event_',
    'Target_Expense_Days_',
    'Target_Income_Days_',
    'Target_High_Expense_',
    'Target_Health_Problem_',
    'Target_High_Health_Severity_',
    'Target_Low_Energy_',
    'Target_Significant_Health_Day_',
    'Target_Has_Location_',
    'Target_Location_Changed_',
    'Target_Same_Location_',
    'Target_Busy_Day_',
    'Target_Financial_Activity_',
    'Target_Difficult_Day_',
    'Target_Active_Day_',
    'Target_Travel_Day_',
    'Target_Special_Day_',
]

NUMERIC_PREFIXES = [
    'Target_Expense_Total_',
    'Target_Income_Total_',
    'Target_Balance_',
]

LOCATION_PREFIX = 'Target_Location_'


# =========================================================
# HELPERS
# =========================================================

def is_nan(value):
    """
    Safely determine whether a value is NaN.
    """
    try:
        return isnan(value)
    except (TypeError, ValueError):
        return False


def is_number(value):
    """
    Return True when value is numeric.
    """
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    )


def expected_target_names():
    """
    Build the complete expected target column set.
    """
    names = []
    
    for horizon in HORIZONS:
        for prefix in TARGET_PREFIXES:
            names.append(f'{prefix}{horizon}')
    
    return names


def target_columns(dataset):
    """
    Extract all target columns from the first row.
    """
    if not dataset:
        return []
    
    return [
        key
        for key in dataset[0].keys()
        if key.startswith('Target_')
    ]


# =========================================================
# TEST 1 - DATASET EXISTENCE
# =========================================================

def test_dataset_exists(dataset):
    assert dataset, 'FAIL: Target dataset is empty.'
    print('PASS: Target dataset contains rows.')


# =========================================================
# TEST 2 - TARGET COUNT
# =========================================================

def test_target_count(dataset):
    actual_targets = target_columns(dataset)
    expected_targets = expected_target_names()
    
    assert len(actual_targets) == len(expected_targets), (
        f'FAIL: Expected {len(expected_targets)} targets, '
        f'found {len(actual_targets)}.'
    )
    
    print(f'PASS: Target count = {len(actual_targets)}.')


# =========================================================
# TEST 3 - DUPLICATE TARGET NAMES
# =========================================================

def test_duplicate_targets(dataset):
    columns = target_columns(dataset)
    
    duplicates = {
        column
        for column in columns
        if columns.count(column) > 1
    }
    
    assert not duplicates, (
        'FAIL: Duplicate target columns found: '
        f'{sorted(duplicates)}'
    )
    
    print('PASS: No duplicate target columns.')


# =========================================================
# TEST 4 - EXPECTED TARGET NAMES
# =========================================================

def test_target_names(dataset):
    actual = set(target_columns(dataset))
    expected = set(expected_target_names())
    
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    
    assert not missing, (
        'FAIL: Missing target columns:\n'
        + '\n'.join(missing)
    )
    
    assert not unexpected, (
        'FAIL: Unexpected target columns:\n'
        + '\n'.join(unexpected)
    )
    
    print('PASS: All expected target columns exist.')


# =========================================================
# TEST 5 - TARGETS PER HORIZON
# =========================================================

def test_targets_per_horizon(dataset):
    expected_per_horizon = len(TARGET_PREFIXES)
    columns = target_columns(dataset)
    
    for horizon in HORIZONS:
        expected_columns = {
            f'{prefix}{horizon}'
            for prefix in TARGET_PREFIXES
        }
        
        actual_columns = {
            column
            for column in columns
            if column in expected_columns
        }
        
        assert actual_columns == expected_columns, (
            f'FAIL: Horizon {horizon} does not contain '
            f'the exact expected target set.'
        )
    
    print(
        'PASS: Every horizon contains '
        f'{expected_per_horizon} exact targets.'
    )


# =========================================================
# TEST 6 - BINARY TARGET VALUES
# =========================================================

def test_binary_values(dataset):
    errors = []
    columns = target_columns(dataset)
    
    binary_columns = [
        column
        for column in columns
        if any(
            column.startswith(prefix)
            for prefix in BINARY_PREFIXES
        )
    ]
    
    for row_index, row in enumerate(dataset):
        for column in binary_columns:
            value = row.get(column)
            
            if is_nan(value):
                continue
            
            if value not in {0, 1}:
                errors.append(
                    f'row={row_index}, '
                    f'{column}={value!r}'
                )
    
    assert not errors, (
        'FAIL: Invalid binary target values:\n'
        + '\n'.join(errors[:20])
    )
    
    print('PASS: All binary targets contain only 0, 1, or NaN.')


# =========================================================
# TEST 7 - NUMERIC FINANCIAL TARGETS
# =========================================================

def test_numeric_targets(dataset):
    errors = []
    columns = target_columns(dataset)
    
    numeric_columns = [
        column
        for column in columns
        if any(
            column.startswith(prefix)
            for prefix in NUMERIC_PREFIXES
        )
    ]
    
    for row_index, row in enumerate(dataset):
        for column in numeric_columns:
            value = row.get(column)
            
            if is_nan(value):
                continue
            
            if not is_number(value):
                errors.append(
                    f'row={row_index}, '
                    f'{column}={value!r}'
                )
    
    assert not errors, (
        'FAIL: Invalid numeric target values:\n'
        + '\n'.join(errors[:20])
    )
    
    print('PASS: Financial numeric targets contain only numeric values or NaN.')


# =========================================================
# TEST 8 - LOCATION TARGET VALUES
# =========================================================

def test_location_values(dataset):
    errors = []
    
    columns = [
        column
        for column in target_columns(dataset)
        if column.startswith(LOCATION_PREFIX)
        and not column.startswith('Target_Has_Location_')
        and not column.startswith('Target_Location_Changed_')
        and not column.startswith('Target_Same_Location_')
    ]
    
    for row_index, row in enumerate(dataset):
        for column in columns:
            value = row.get(column)
            
            if value is None:
                continue
            
            if is_nan(value):
                continue
            
            if not isinstance(value, str):
                errors.append(
                    f'row={row_index}, '
                    f'{column}={value!r}'
                )
    
    assert not errors, (
        'FAIL: Invalid location target values:\n'
        + '\n'.join(errors[:20])
    )
    
    print('PASS: Location targets contain text values or None/NaN.')


# =========================================================
# TEST 9 - REQUIRED DATE COLUMN
# =========================================================

def test_date_column(dataset):
    assert 'Date' in dataset[0], 'FAIL: Date column is missing.'
    print('PASS: Date column exists.')


# =========================================================
# TEST 10 - NO MISSING TARGET STRUCTURE
# =========================================================

def test_row_structure(dataset):
    expected_columns = set(target_columns(dataset))
    errors = []
    
    for row_index, row in enumerate(dataset):
        actual_columns = {
            key
            for key in row.keys()
            if key.startswith('Target_')
        }
        
        missing = expected_columns - actual_columns
        extra = actual_columns - expected_columns
        
        if missing or extra:
            errors.append(
                f'row={row_index}, '
                f'missing={sorted(missing)}, '
                f'extra={sorted(extra)}'
            )
    
    assert not errors, (
        'FAIL: Target structure differs between rows:\n'
        + '\n'.join(errors[:10])
    )
    
    print('PASS: All rows have identical target structure.')


# =========================================================
# TEST 11 - NaN DISTRIBUTION
# =========================================================

def test_nan_distribution(dataset):
    target_cols = target_columns(dataset)
    
    nan_count = 0
    total_values = 0
    
    for row in dataset:
        for column in target_cols:
            value = row.get(column)
            total_values += 1
            
            if is_nan(value):
                nan_count += 1
    
    print(f'INFO: Target values = {total_values}')
    print(f'INFO: NaN target values = {nan_count}')
    print('PASS: NaN distribution inspected.')


# =========================================================
# MAIN TEST RUNNER
# =========================================================

def main():
    print()
    print('=================================================')
    print('        TARGET QUALITY VALIDATION')
    print('=================================================')
    print()
    
    dataset = build_target_dataset()
    
    try:
        test_dataset_exists(dataset)
        test_target_count(dataset)
        test_duplicate_targets(dataset)
        test_target_names(dataset)
        test_targets_per_horizon(dataset)
        test_binary_values(dataset)
        test_numeric_targets(dataset)
        test_location_values(dataset)
        test_date_column(dataset)
        test_row_structure(dataset)
        test_nan_distribution(dataset)
        
    except AssertionError as error:
        print()
        print('=================================================')
        print('TARGET QUALITY VALIDATION: FAILED')
        print('=================================================')
        print()
        print(error)
        return
    
    print()
    print('=================================================')
    print('TARGET QUALITY VALIDATION: PASSED')
    print('=================================================')
    print()


if __name__ == '__main__':
    main()