from datetime import date

from ml.training.dataset import (
    prepare_model_dataset,
    _calculate_split_index,
)


# =========================================================
# SPLIT INDEX
# =========================================================

def test_calculate_split_index_respects_chronological_ratio():

    assert _calculate_split_index(10) == 8
    assert _calculate_split_index(5) == 4
    assert _calculate_split_index(2) == 1


# =========================================================
# MINIMUM DATA SAFETY
# =========================================================

def test_calculate_split_index_with_one_row():

    assert _calculate_split_index(1) == 1


def test_calculate_split_index_with_empty_data():

    assert _calculate_split_index(0) == 0


# =========================================================
# SUPERVISED DATASET STRUCTURE
# =========================================================

def test_prepare_model_dataset_returns_expected_structure():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    assert isinstance(result, dict)

    assert 'dataset' in result
    assert 'feature_names' in result
    assert 'target_name' in result

    assert 'training_data' in result
    assert 'test_data' in result

    assert 'X_train' in result
    assert 'y_train' in result

    assert 'X_test' in result
    assert 'y_test' in result

    assert 'validation_report' in result


# =========================================================
# TARGET SELECTION
# =========================================================

def test_selected_target_is_preserved():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    assert (
        result['target_name']
        == 'Target_Expense_Total_1D'
    )

    assert (
        result['validation_report']['target_name']
        == 'Target_Expense_Total_1D'
    )


# =========================================================
# FEATURE / TARGET SEPARATION
# =========================================================

def test_target_is_not_a_model_feature():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    feature_names = result[
        'feature_names'
    ]

    assert (
        'Target_Expense_Total_1D'
        not in feature_names
    )


# =========================================================
# DATE MUST NOT ENTER FEATURES
# =========================================================

def test_date_is_not_a_model_feature():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    feature_names = result[
        'feature_names'
    ]

    assert 'Date' not in feature_names


# =========================================================
# ALL TARGET COLUMNS MUST BE EXCLUDED
# =========================================================

def test_all_target_columns_are_excluded_from_features():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    feature_names = result[
        'feature_names'
    ]

    target_features = [
        name
        for name in feature_names
        if name.startswith('Target_')
    ]

    assert target_features == []


# =========================================================
# CHRONOLOGICAL ORDER
# =========================================================

def test_training_and_test_data_are_chronological():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    training_data = result[
        'training_data'
    ]

    test_data = result[
        'test_data'
    ]

    training_dates = [
        row['Date']
        for row in training_data
    ]

    test_dates = [
        row['Date']
        for row in test_data
    ]

    assert training_dates == sorted(
        training_dates
    )

    assert test_dates == sorted(
        test_dates
    )


# =========================================================
# TEMPORAL BOUNDARY
# =========================================================

def test_training_precedes_testing_period():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    training_data = result[
        'training_data'
    ]

    test_data = result[
        'test_data'
    ]

    if training_data and test_data:

        training_last_date = max(
            row['Date']
            for row in training_data
        )

        test_first_date = min(
            row['Date']
            for row in test_data
        )

        assert (
            training_last_date
            < test_first_date
        )


# =========================================================
# NO OVERLAP
# =========================================================

def test_training_and_testing_have_no_overlap():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    training_dates = {
        row['Date']
        for row in result['training_data']
    }

    test_dates = {
        row['Date']
        for row in result['test_data']
    }

    assert training_dates.isdisjoint(
        test_dates
    )


# =========================================================
# X / Y LENGTH CONSISTENCY
# =========================================================

def test_training_x_y_lengths_match():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    assert len(
        result['X_train']
    ) == len(
        result['y_train']
    )


def test_testing_x_y_lengths_match():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    assert len(
        result['X_test']
    ) == len(
        result['y_test']
    )


# =========================================================
# FEATURE COUNT CONSISTENCY
# =========================================================

def test_feature_count_matches_training_rows():

    result = prepare_model_dataset(
        target_name='Target_Expense_Total_1D'
    )

    feature_count = len(
        result['feature_names']
    )

    for row in result['X_train']:
        assert len(row) == feature_count

    for row in result['X_test']:
        assert len(row) == feature_count


# =========================================================
# MULTI-TARGET DATASET
# =========================================================

def test_all_target_datasets_have_structured_results():

    from ml.training.dataset import (
        prepare_all_target_datasets,
    )

    results = prepare_all_target_datasets()

    assert isinstance(
        results,
        dict
    )

    for target_name, result in results.items():

        assert (
            result['target_name']
            == target_name
        )

        assert 'dataset' in result
        assert 'feature_names' in result
        assert 'validation_report' in result


# =========================================================
# INVALID TARGET
# =========================================================

def test_invalid_target_is_rejected():

    import pytest

    with pytest.raises(
        ValueError,
        match='Unknown target',
    ):

        prepare_model_dataset(
            target_name='Target_Does_Not_Exist'
        )