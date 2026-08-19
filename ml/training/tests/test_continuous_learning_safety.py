# ==========================================================
# CONTINUOUS LEARNING SAFETY TESTS
# ==========================================================

import tempfile

import pytest

from sklearn.linear_model import LinearRegression

from ml.training.continuous_learning import (
    CONTINUOUS_LEARNING_VALID,
    CANDIDATE_ACCEPTED,
    CANDIDATE_REJECTED,
    CANDIDATE_SAVED_NOT_ACTIVATED,
    IMPROVEMENT_MINIMIZE,
)

from ml.training.continuous_learning_cycle import (
    CYCLE_VALID,
    CYCLE_FAILED,
    execute_continuous_learning_cycle,
)

from ml.models.registry import (
    REGISTRY_VALID,
    save_registered_model,
    activate_registered_model,
    get_active_model_version,
    list_model_versions,
)


# ==========================================================
# HELPERS
# ==========================================================

TARGET_NAME = 'Target_Expense_Total_1D'

FEATURE_NAMES = [
    'feature_a',
    'feature_b',
]


def create_model():

    model = LinearRegression()

    model.fit(
        [
            [1.0, 2.0],
            [2.0, 3.0],
            [3.0, 4.0],
        ],
        [
            3.0,
            5.0,
            7.0,
        ],
    )

    return model


def create_metadata(version):

    return {
        'target_name': TARGET_NAME,
        'target_task': 'regression',
        'target_type': 'numeric',
        'model_type': 'regression',
        'algorithm': 'LinearRegression',
        'feature_names': FEATURE_NAMES,
        'version': version,
    }


def create_current_result(
    mae=100.0,
    sample_count=100,
):

    return {
        'status': CONTINUOUS_LEARNING_VALID,
        'evaluation_valid': True,
        'evaluation_status': CONTINUOUS_LEARNING_VALID,
        'mae': mae,
        'sample_count': sample_count,
    }


def create_candidate_result(
    mae=80.0,
    sample_count=120,
):

    return {
        'status': CONTINUOUS_LEARNING_VALID,
        'evaluation_valid': True,
        'evaluation_status': CONTINUOUS_LEARNING_VALID,
        'mae': mae,
        'sample_count': sample_count,
    }


def prepare_active_v1(registry_dir):

    model = create_model()

    metadata = create_metadata('v1.0.0')

    save_result = save_registered_model(
        model,
        metadata,
        registry_dir,
    )

    assert save_result['status'] == REGISTRY_VALID

    activation_result = activate_registered_model(
        TARGET_NAME,
        'v1.0.0',
        registry_dir,
    )

    assert activation_result['active'] is True

    assert get_active_model_version(
        TARGET_NAME,
        registry_dir,
    ) == 'v1.0.0'


# ==========================================================
# 1. BETTER CANDIDATE
# ==========================================================

def test_better_candidate_is_saved_and_activated():

    registry_dir = tempfile.mkdtemp()

    prepare_active_v1(registry_dir)

    candidate_model = create_model()

    candidate_metadata = create_metadata('v2.0.0')

    result = execute_continuous_learning_cycle(
        current_result=create_current_result(
            mae=100.0
        ),
        candidate_result=create_candidate_result(
            mae=80.0
        ),
        candidate_model=candidate_model,
        candidate_metadata=candidate_metadata,
        primary_metric='mae',
        direction=IMPROVEMENT_MINIMIZE,
        minimum_improvement=1.0,
        minimum_sample_count=10,
        current_model_version='v1.0.0',
        registry_dir=registry_dir,
    )

    assert result['status'] == CYCLE_VALID
    assert result['decision'] == CANDIDATE_ACCEPTED
    assert result['saved'] is True
    assert result['activated'] is True
    assert result['active_version'] == 'v2.0.0'

    assert get_active_model_version(
        TARGET_NAME,
        registry_dir,
    ) == 'v2.0.0'

    assert list_model_versions(
        TARGET_NAME,
        registry_dir,
    ) == [
        'v1.0.0',
        'v2.0.0',
    ]


# ==========================================================
# 2. WORSE CANDIDATE
# ==========================================================

def test_worse_candidate_is_rejected_but_saved():

    registry_dir = tempfile.mkdtemp()

    prepare_active_v1(registry_dir)

    candidate_model = create_model()

    candidate_metadata = create_metadata('v2.0.0')

    result = execute_continuous_learning_cycle(
        current_result=create_current_result(
            mae=80.0
        ),
        candidate_result=create_candidate_result(
            mae=100.0
        ),
        candidate_model=candidate_model,
        candidate_metadata=candidate_metadata,
        primary_metric='mae',
        direction=IMPROVEMENT_MINIMIZE,
        minimum_improvement=1.0,
        minimum_sample_count=10,
        current_model_version='v1.0.0',
        registry_dir=registry_dir,
    )

    assert result['decision'] == CANDIDATE_REJECTED

    # Rejected from activation, but preserved in registry history.
    assert result['saved'] is True
    assert result['activated'] is False

    assert get_active_model_version(
        TARGET_NAME,
        registry_dir,
    ) == 'v1.0.0'

    assert list_model_versions(
        TARGET_NAME,
        registry_dir,
    ) == [
        'v1.0.0',
        'v2.0.0',
    ]


# ==========================================================
# 3. IMPROVEMENT BELOW MINIMUM
# ==========================================================

def test_insufficient_improvement_is_rejected_but_saved():

    registry_dir = tempfile.mkdtemp()

    prepare_active_v1(registry_dir)

    candidate_model = create_model()

    candidate_metadata = create_metadata('v2.0.0')

    result = execute_continuous_learning_cycle(
        current_result=create_current_result(
            mae=100.0
        ),
        candidate_result=create_candidate_result(
            mae=99.5
        ),
        candidate_model=candidate_model,
        candidate_metadata=candidate_metadata,
        primary_metric='mae',
        direction=IMPROVEMENT_MINIMIZE,
        minimum_improvement=1.0,
        minimum_sample_count=10,
        current_model_version='v1.0.0',
        registry_dir=registry_dir,
    )

    assert result['decision'] == CANDIDATE_REJECTED

    # Improvement is below the required threshold.
    # Candidate remains available in registry history.
    assert result['saved'] is True
    assert result['activated'] is False

    assert get_active_model_version(
        TARGET_NAME,
        registry_dir,
    ) == 'v1.0.0'

    assert list_model_versions(
        TARGET_NAME,
        registry_dir,
    ) == [
        'v1.0.0',
        'v2.0.0',
    ]


# ==========================================================
# 4. INSUFFICIENT DATA
# ==========================================================

def test_insufficient_data_is_saved_but_not_activated():

    registry_dir = tempfile.mkdtemp()

    prepare_active_v1(registry_dir)

    candidate_model = create_model()

    candidate_metadata = create_metadata('v2.0.0')

    result = execute_continuous_learning_cycle(
        current_result=create_current_result(
            mae=100.0,
            sample_count=100,
        ),
        candidate_result=create_candidate_result(
            mae=80.0,
            sample_count=5,
        ),
        candidate_model=candidate_model,
        candidate_metadata=candidate_metadata,
        primary_metric='mae',
        direction=IMPROVEMENT_MINIMIZE,
        minimum_improvement=1.0,
        minimum_sample_count=10,
        current_model_version='v1.0.0',
        registry_dir=registry_dir,
    )

    assert result['decision'] == CANDIDATE_SAVED_NOT_ACTIVATED
    assert result['saved'] is True
    assert result['activated'] is False

    assert get_active_model_version(
        TARGET_NAME,
        registry_dir,
    ) == 'v1.0.0'

    assert list_model_versions(
        TARGET_NAME,
        registry_dir,
    ) == [
        'v1.0.0',
        'v2.0.0',
    ]


# ==========================================================
# 5. INVALID CANDIDATE MODEL
# ==========================================================

def test_invalid_candidate_model_is_rejected_before_registry_change():

    registry_dir = tempfile.mkdtemp()

    prepare_active_v1(registry_dir)

    candidate_metadata = create_metadata('v2.0.0')

    with pytest.raises(ValueError):

        execute_continuous_learning_cycle(
            current_result=create_current_result(),
            candidate_result=create_candidate_result(),
            candidate_model=None,
            candidate_metadata=candidate_metadata,
            primary_metric='mae',
            direction=IMPROVEMENT_MINIMIZE,
            minimum_improvement=1.0,
            minimum_sample_count=10,
            current_model_version='v1.0.0',
            registry_dir=registry_dir,
        )

    # Registry must remain completely unchanged.
    assert get_active_model_version(
        TARGET_NAME,
        registry_dir,
    ) == 'v1.0.0'

    assert list_model_versions(
        TARGET_NAME,
        registry_dir,
    ) == [
        'v1.0.0'
    ]


# ==========================================================
# 6. ACTIVATION FAILURE PROTECTION
# ==========================================================

def test_activation_failure_does_not_replace_active_model(
    monkeypatch,
):

    registry_dir = tempfile.mkdtemp()

    prepare_active_v1(registry_dir)

    candidate_model = create_model()

    candidate_metadata = create_metadata('v2.0.0')

    def failing_activation(
        target_name,
        version,
        registry_dir=None,
    ):

        raise RuntimeError(
            'Simulated activation failure.'
        )

    monkeypatch.setattr(
        'ml.training.continuous_learning_cycle.activate_registered_model',
        failing_activation,
    )

    result = execute_continuous_learning_cycle(
        current_result=create_current_result(
            mae=100.0
        ),
        candidate_result=create_candidate_result(
            mae=80.0
        ),
        candidate_model=candidate_model,
        candidate_metadata=candidate_metadata,
        primary_metric='mae',
        direction=IMPROVEMENT_MINIMIZE,
        minimum_improvement=1.0,
        minimum_sample_count=10,
        current_model_version='v1.0.0',
        registry_dir=registry_dir,
    )

    assert result['status'] == CYCLE_FAILED
    assert result['saved'] is True
    assert result['activated'] is False

    # Activation failed, therefore v1 remains active.
    assert get_active_model_version(
        TARGET_NAME,
        registry_dir,
    ) == 'v1.0.0'

    # Candidate was saved before activation was attempted.
    assert list_model_versions(
        TARGET_NAME,
        registry_dir,
    ) == [
        'v1.0.0',
        'v2.0.0',
    ]