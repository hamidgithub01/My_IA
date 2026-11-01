"""Manual, isolated batch training for every registered target."""

from datetime import datetime, timezone
from copy import copy

from ml.targets.build import get_target_names
from ml.targets.registry import get_target_task
from ml.training.train import train_target_model
from ml.evaluation.evaluate import evaluate_model
from ml.models.registry import (
    REGISTRY_VALID,
    load_active_model,
    get_latest_model_version,
)
from ml.training.continuous_learning_cycle import (
    _next_model_version,
    _build_candidate_metadata,
    execute_continuous_learning_cycle,
)

MINIMUM_TEST_SAMPLES_FOR_ACTIVATION = 10


def _metric_policy(task):
    if task == 'regression':
        return 'mae', 'minimize'
    return 'f1', 'maximize'


def _flatten_evaluation(result, sample_count):
    flattened = dict(result or {})
    metrics = flattened.get('metrics') or {}
    flattened.update(metrics)
    flattened['sample_count'] = sample_count
    flattened['observation_count'] = sample_count
    flattened['evaluation_valid'] = bool(
        flattened.get('evaluation_valid')
        and flattened.get('evaluation_status') == 'valid'
        and metrics
    )
    return flattened


def _process_target(target_name):
    task = get_target_task(target_name)
    primary_metric, direction = _metric_policy(task)

    training_result = train_target_model(target_name)
    try:
        candidate_evaluation = evaluate_model(training_result=training_result)
    except ValueError as exc:
        return {
            'target_name': target_name, 'task': task,
            'training_rows': training_result.get('training_rows', 0),
            'test_rows': training_result.get('test_rows', 0),
            'status': 'insufficient_data', 'saved': False, 'activated': False,
            'reason': f'Evaluation unavailable: {exc}',
        }
    sample_count = int(training_result.get('test_rows') or 0)
    candidate_result = _flatten_evaluation(candidate_evaluation, sample_count)

    base = {
        'target_name': target_name,
        'task': task,
        'training_rows': training_result.get('training_rows', 0),
        'test_rows': sample_count,
        'evaluation_status': candidate_evaluation.get('evaluation_status'),
        'metrics': candidate_evaluation.get('metrics'),
        'primary_metric': primary_metric,
        'saved': False,
        'activated': False,
        'current_model_version': None,
        'candidate_model_version': None,
    }

    if not candidate_result['evaluation_valid']:
        return {**base, 'status': 'insufficient_data',
                'reason': candidate_evaluation.get('evaluation_status', 'Evaluation unavailable.')}

    if sample_count < MINIMUM_TEST_SAMPLES_FOR_ACTIVATION:
        return {**base, 'status': 'insufficient_data',
                'reason': f'Only {sample_count} test observations; at least {MINIMUM_TEST_SAMPLES_FOR_ACTIVATION} are required before activation.'}

    active = load_active_model(target_name)
    current_version = active.get('version') if active.get('status') == REGISTRY_VALID else None
    base['current_model_version'] = current_version

    current_result = None
    if current_version:
        metadata = active.get('metadata') or {}
        active_features = metadata.get('feature_names') or []
        candidate_features = training_result.get('feature_names') or []
        if active_features == candidate_features:
            baseline_training = dict(training_result)
            baseline_training['model'] = active['model']
            try:
                baseline_evaluation = evaluate_model(training_result=baseline_training)
                current_result = _flatten_evaluation(baseline_evaluation, sample_count)
            except ValueError:
                current_result = {'evaluation_valid': False, 'evaluation_status': 'active_model_evaluation_unavailable'}
        else:
            # Save a candidate for inspection, but never activate it when
            # its feature schema cannot be compared with the active model.
            current_result = {
                'evaluation_valid': False,
                'evaluation_status': 'feature_schema_changed',
            }

    latest_version = get_latest_model_version(target_name)
    candidate_version = _next_model_version(latest_version or current_version)
    base['candidate_model_version'] = candidate_version
    metadata = _build_candidate_metadata(training_result, candidate_version)
    metadata.update({
        'primary_metric': primary_metric,
        'metric_direction': direction,
        'evaluation_metrics': candidate_evaluation.get('metrics') or {},
        'training_rows': training_result.get('training_rows', 0),
        'test_rows': sample_count,
        'trained_at': datetime.now(timezone.utc).isoformat(),
    })

    result = execute_continuous_learning_cycle(
        current_result=current_result,
        candidate_result=candidate_result,
        candidate_model=training_result['model'],
        candidate_metadata=metadata,
        primary_metric=primary_metric,
        direction=direction,
        minimum_improvement=0.0,
        minimum_sample_count=MINIMUM_TEST_SAMPLES_FOR_ACTIVATION,
        current_model_version=current_version,
    )

    decision = result.get('decision')
    status = 'failed' if result.get('status') == 'failed' else (
        'activated' if result.get('activated') else (
            'saved_not_activated' if result.get('saved') else 'rejected'
        )
    )
    return {
        **base,
        'status': status,
        'saved': bool(result.get('saved')),
        'activated': bool(result.get('activated')),
        'decision': decision,
        'reason': result.get('reason'),
        'candidate_model_version': result.get('candidate_model_version', candidate_version),
    }


def train_all_targets(progress_callback=None):
    """Train all registered targets; isolate every target failure."""
    targets = get_target_names()
    report = {
        'started_at': datetime.now(timezone.utc).isoformat(),
        'finished_at': None,
        'total': len(targets),
        'completed': 0,
        'results': [],
    }

    for index, target_name in enumerate(targets, start=1):
        try:
            result = _process_target(target_name)
        except Exception as exc:
            result = {
                'target_name': target_name,
                'status': 'failed',
                'saved': False,
                'activated': False,
                'reason': f'{type(exc).__name__}: {exc}',
            }
        report['results'].append(result)
        report['completed'] = index
        if progress_callback:
            progress_callback(index, len(targets), result)

    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    report['summary'] = {
        status: sum(1 for item in report['results'] if item.get('status') == status)
        for status in ('activated', 'saved_not_activated', 'rejected', 'insufficient_data', 'failed')
    }
    return report
