import pytest
from copy import deepcopy
from ml.integration.interface import (
    INTEGRATION_VALID,
    build_ui_result,
    has_ui_data,
    integrate_for_ui,
    is_ui_result_available,
    prepare_analysis_output,
    prepare_prediction_input,
    prepare_prediction_output,
    prepare_report_output,
    run_ui_pipeline,
)


# ==========================================================
# TEST DATA
# ==========================================================

def _prediction_result(
    target_name='Target_Expense_Total_1D',
    target_task='regression',
):
    return {

        'status':
            'valid',

        'target_name':
            target_name,

        'target_task':
            target_task,

        'prediction':
            150.0,
    }


def _analysis_result(
    target_name='Target_Expense_Total_1D',
    target_task='regression',
):
    return {

        'status':
            'valid',

        'analysis_status':
            'valid',

        'target_name':
            target_name,

        'target_task':
            target_task,

        'summary':
            'Prediction analysis',
    }


def _reliability_result():
    return {

        'status':
            'reliable',

        'reliability_level':
            'high',

        'quality_score':
            0.95,
    }


def _monitoring_result():
    return {

        'status':
            'stable',

        'target_name':
            'Target_Expense_Total_1D',

        'error_rate':
            0.02,
    }


def _alert_result():
    return {

        'status':
            'valid',

        'alerts':
            [],
    }


def _recommendation_result():
    return {

        'status':
            'valid',

        'recommendations':
            [],
    }


def _report_result():
    return {

        'status':
            'valid',

        'target_name':
            'Target_Expense_Total_1D',

        'target_task':
            'regression',

        'report':
            {
                'status':
                    'valid',
            },
    }


# ==========================================================
# PREDICTION INPUT
# ==========================================================

def test_prepare_prediction_input():

    result = prepare_prediction_input(
        'Target_Expense_Total_1D',
        {
            'feature_a': 10,
            'feature_b': 20,
        },
    )

    assert result[
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert result[
        'features'
    ][
        'feature_a'
    ] == 10


def test_prepare_prediction_input_rejects_missing_target():

    with pytest.raises(
        ValueError,
        match='target_name is required',
    ):

        prepare_prediction_input(
            None,
            {},
        )


def test_prepare_prediction_input_rejects_invalid_target():

    with pytest.raises(
        ValueError,
        match='target_name must be a string',
    ):

        prepare_prediction_input(
            123,
            {},
        )


def test_prepare_prediction_input_rejects_empty_target():

    with pytest.raises(
        ValueError,
        match='target_name cannot be empty',
    ):

        prepare_prediction_input(
            '   ',
            {},
        )


def test_prepare_prediction_input_rejects_missing_features():

    with pytest.raises(
        ValueError,
        match='features are required',
    ):

        prepare_prediction_input(
            'Target',
            None,
        )


def test_prepare_prediction_input_rejects_invalid_features():

    with pytest.raises(
        ValueError,
        match='features must be a list, tuple, or dictionary',
    ):

        prepare_prediction_input(
            'Target',
            'invalid',
        )


# ==========================================================
# PREDICTION OUTPUT
# ==========================================================

def test_prepare_prediction_output():

    result = prepare_prediction_output(
        _prediction_result()
    )

    assert result[
        'available'
    ] is True

    assert result[
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert result[
        'target_task'
    ] == 'regression'


def test_prepare_prediction_output_rejects_invalid_input():

    with pytest.raises(
        ValueError,
        match='prediction_result is required',
    ):

        prepare_prediction_output(
            None
        )


# ==========================================================
# ANALYSIS OUTPUT
# ==========================================================

def test_prepare_analysis_output():

    result = prepare_analysis_output(
        _analysis_result()
    )

    assert result[
        'available'
    ] is True

    assert result[
        'analysis_status'
    ] == 'valid'


def test_prepare_analysis_output_rejects_invalid_input():

    with pytest.raises(
        ValueError,
        match='analysis_result is required',
    ):

        prepare_analysis_output(
            None
        )


# ==========================================================
# REPORT OUTPUT
# ==========================================================

def test_prepare_report_output():

    result = prepare_report_output(
        _report_result()
    )

    assert result[
        'available'
    ] is True

    assert result[
        'target_name'
    ] == 'Target_Expense_Total_1D'


def test_prepare_report_output_rejects_invalid_input():

    with pytest.raises(
        ValueError,
        match='report_result is required',
    ):

        prepare_report_output(
            None
        )


# ==========================================================
# COMPLETE UI RESULT
# ==========================================================

def test_build_ui_result():

    result = build_ui_result(
        prediction_result=
            _prediction_result(),
    )

    assert result[
        'status'
    ] == INTEGRATION_VALID

    assert result[
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert result[
        'prediction'
    ][
        'available'
    ] is True


def test_build_ui_result_with_all_layers():

    result = build_ui_result(
        prediction_result=
            _prediction_result(),

        analysis_result=
            _analysis_result(),

        reliability_result=
            _reliability_result(),

        monitoring_result=
            _monitoring_result(),

        alert_result=
            _alert_result(),

        recommendation_result=
            _recommendation_result(),

        report_result=
            _report_result(),
    )

    assert result[
        'status'
    ] == INTEGRATION_VALID

    assert result[
        'prediction'
    ] is not None

    assert result[
        'analysis'
    ] is not None

    assert result[
        'reliability'
    ] is not None

    assert result[
        'monitoring'
    ] is not None

    assert result[
        'alerts'
    ] is not None

    assert result[
        'recommendations'
    ] is not None

    assert result[
        'report'
    ] is not None


def test_build_ui_result_accepts_missing_optional_layers():

    result = build_ui_result(
        prediction_result=
            _prediction_result(),
    )

    assert result[
        'prediction'
    ] is not None

    assert result[
        'analysis'
    ] is None

    assert result[
        'reliability'
    ] is None

    assert result[
        'monitoring'
    ] is None

    assert result[
        'alerts'
    ] is None

    assert result[
        'recommendations'
    ] is None

    assert result[
        'report'
    ] is None


def test_build_ui_result_requires_prediction():

    with pytest.raises(
        ValueError,
        match='prediction_result is required',
    ):

        build_ui_result(
            None
        )


def test_build_ui_result_rejects_invalid_prediction():

    with pytest.raises(
        ValueError,
        match='prediction_result must be a dictionary',
    ):

        build_ui_result(
            []
        )


# ==========================================================
# TARGET IDENTITY
# ==========================================================

def test_ui_result_preserves_target_identity():

    target_name = (
        'Target_Income_Total_1D'
    )

    result = build_ui_result(
        prediction_result=
            _prediction_result(
                target_name=target_name
            ),
    )

    assert result[
        'target_name'
    ] == target_name

    assert result[
        'prediction'
    ][
        'target_name'
    ] == target_name


def test_ui_result_preserves_target_task():

    result = build_ui_result(
        prediction_result=
            _prediction_result(
                target_task='regression'
            ),
    )

    assert result[
        'target_task'
    ] == 'regression'

    assert result[
        'prediction'
    ][
        'target_task'
    ] == 'regression'


def test_ui_result_keeps_targets_isolated():

    first = build_ui_result(
        prediction_result=
            _prediction_result(
                target_name=
                    'Target_Expense_Total_1D'
            ),
    )

    second = build_ui_result(
        prediction_result=
            _prediction_result(
                target_name=
                    'Target_Income_Total_1D'
            ),
    )

    assert first[
        'target_name'
    ] != second[
        'target_name'
    ]

    assert first[
        'prediction'
    ][
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert second[
        'prediction'
    ][
        'target_name'
    ] == 'Target_Income_Total_1D'


# ==========================================================
# IMMUTABILITY
# ==========================================================

def test_build_ui_result_does_not_modify_prediction():

    prediction = _prediction_result()

    original = deepcopy(
        prediction
    )

    build_ui_result(
        prediction_result=
            prediction,
    )

    assert prediction == original


def test_prepare_prediction_input_does_not_modify_features():

    features = {
        'feature_a': 10,
        'feature_b': 20,
    }

    original = deepcopy(
        features
    )

    prepare_prediction_input(
        'Target',
        features,
    )

    assert features == original


# ==========================================================
# AVAILABILITY
# ==========================================================

def test_is_ui_result_available():

    result = build_ui_result(
        _prediction_result()
    )

    assert is_ui_result_available(
        result
    ) is True


def test_is_ui_result_available_false():

    assert is_ui_result_available(
        {
            'status':
                'invalid'
        }
    ) is False


def test_is_ui_result_available_rejects_invalid_input():

    assert is_ui_result_available(
        None
    ) is False

    assert is_ui_result_available(
        []
    ) is False


def test_has_ui_data():

    result = build_ui_result(
        _prediction_result()
    )

    assert has_ui_data(
        result
    ) is True


def test_has_ui_data_false():

    assert has_ui_data(
        {
            'status':
                INTEGRATION_VALID,

            'prediction':
                None,
        }
    ) is False


def test_has_ui_data_rejects_invalid_input():

    assert has_ui_data(
        None
    ) is False

    assert has_ui_data(
        []
    ) is False


# ==========================================================
# PIPELINE
# ==========================================================

def test_run_ui_pipeline():

    result = run_ui_pipeline(
        prediction_result=
            _prediction_result(),

        analysis_result=
            _analysis_result(),
    )

    assert result[
        'status'
    ] == INTEGRATION_VALID

    assert result[
        'prediction'
    ] is not None

    assert result[
        'analysis'
    ] is not None


def test_integrate_for_ui():

    result = integrate_for_ui(
        prediction_result=
            _prediction_result(),

        analysis_result=
            _analysis_result(),

        reliability_result=
            _reliability_result(),

        monitoring_result=
            _monitoring_result(),

        alert_result=
            _alert_result(),

        recommendation_result=
            _recommendation_result(),

        report_result=
            _report_result(),
    )

    assert result[
        'status'
    ] == INTEGRATION_VALID

    assert result[
        'report'
    ] is not None


# ==========================================================
# COMPLETE CONTRACT
# ==========================================================

def test_complete_ui_integration_contract():

    result = integrate_for_ui(
        prediction_result=
            _prediction_result(),

        analysis_result=
            _analysis_result(),

        reliability_result=
            _reliability_result(),

        monitoring_result=
            _monitoring_result(),

        alert_result=
            _alert_result(),

        recommendation_result=
            _recommendation_result(),

        report_result=
            _report_result(),
    )

    assert isinstance(
        result,
        dict,
    )

    assert result[
        'status'
    ] == INTEGRATION_VALID

    assert result[
        'target_name'
    ] == 'Target_Expense_Total_1D'

    assert result[
        'target_task'
    ] == 'regression'

    for key in (
        'prediction',
        'analysis',
        'reliability',
        'monitoring',
        'alerts',
        'recommendations',
        'report',
    ):

        assert key in result