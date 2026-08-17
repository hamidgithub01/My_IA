import math


# ==========================================================
# CONTINUOUS LEARNING STATUS
# ==========================================================

CONTINUOUS_LEARNING_VALID = 'valid'

CONTINUOUS_LEARNING_REJECTED = 'rejected'

CONTINUOUS_LEARNING_INSUFFICIENT_DATA = (
    'insufficient_data'
)

CONTINUOUS_LEARNING_INVALID = 'invalid'


# ==========================================================
# CANDIDATE DECISIONS
# ==========================================================

CANDIDATE_ACCEPTED = 'accepted'

CANDIDATE_REJECTED = 'rejected'

CANDIDATE_NOT_EVALUATED = 'not_evaluated'


# ==========================================================
# IMPROVEMENT DIRECTIONS
# ==========================================================

IMPROVEMENT_MINIMIZE = 'minimize'

IMPROVEMENT_MAXIMIZE = 'maximize'


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _to_float(
    value,
):
    """
    Convert a value to a finite float.
    """

    try:

        converted = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            f'Value must be numeric: {value!r}'
        )

    if not math.isfinite(
        converted
    ):

        raise ValueError(
            f'Value must be finite: {value!r}'
        )

    return converted


def _validate_sample_count(
    sample_count,
    minimum_sample_count,
):
    """
    Validate sample-count configuration.
    """

    if sample_count is None:

        raise ValueError(
            'sample_count is required.'
        )

    if minimum_sample_count is None:

        raise ValueError(
            'minimum_sample_count is required.'
        )

    if not isinstance(
        sample_count,
        int,
    ):

        raise ValueError(
            'sample_count must be an integer.'
        )

    if not isinstance(
        minimum_sample_count,
        int,
    ):

        raise ValueError(
            'minimum_sample_count must be an integer.'
        )

    if sample_count < 0:

        raise ValueError(
            'sample_count cannot be negative.'
        )

    if minimum_sample_count < 1:

        raise ValueError(
            'minimum_sample_count must be greater than zero.'
        )


def _validate_metric_direction(
    direction,
):
    """
    Validate optimization direction.
    """

    if direction not in {
        IMPROVEMENT_MINIMIZE,
        IMPROVEMENT_MAXIMIZE,
    }:

        raise ValueError(
            'Unsupported improvement direction: '
            f'{direction!r}'
        )


# ==========================================================
# METRIC COMPARISON
# ==========================================================

def compare_metric(
    current_value,
    candidate_value,
    direction,
    minimum_improvement=0.0,
):
    """
    Compare a candidate metric against the current metric.

    Returns:

        current_value
        candidate_value
        improvement
        improvement_ratio
        improved
        meets_minimum_improvement

    For minimize:

        lower is better.

    For maximize:

        higher is better.
    """

    current_value = _to_float(
        current_value
    )

    candidate_value = _to_float(
        candidate_value
    )

    minimum_improvement = _to_float(
        minimum_improvement
    )

    if minimum_improvement < 0:

        raise ValueError(
            'minimum_improvement cannot be negative.'
        )

    _validate_metric_direction(
        direction
    )

    if direction == IMPROVEMENT_MINIMIZE:

        improvement = (
            current_value
            - candidate_value
        )

    else:

        improvement = (
            candidate_value
            - current_value
        )

    if current_value != 0:

        improvement_ratio = (
            improvement
            / abs(current_value)
        )

    else:

        improvement_ratio = (
            None
        )

    improved = (
        improvement > 0
    )

    meets_minimum_improvement = (
        improvement >= minimum_improvement
    )

    return {

        'current_value':
            float(current_value),

        'candidate_value':
            float(candidate_value),

        'improvement':
            float(improvement),

        'improvement_ratio':
            (
                None
                if improvement_ratio is None
                else float(improvement_ratio)
            ),

        'improved':
            bool(improved),

        'meets_minimum_improvement':
            bool(
                meets_minimum_improvement
            ),
    }


# ==========================================================
# MODEL COMPARISON
# ==========================================================

def compare_model_results(
    current_result,
    candidate_result,
    primary_metric,
    direction,
    minimum_improvement=0.0,
    minimum_sample_count=1,
):
    """
    Compare evaluation results of the current model and
    a candidate model.

    The candidate is accepted only when:

        1. Both results are valid.
        2. Both contain the primary metric.
        3. Candidate has sufficient samples.
        4. Candidate satisfies the minimum improvement.

    This function does not modify or replace any model.
    """

    if not isinstance(
        current_result,
        dict,
    ):

        raise ValueError(
            'current_result must be a dictionary.'
        )

    if not isinstance(
        candidate_result,
        dict,
    ):

        raise ValueError(
            'candidate_result must be a dictionary.'
        )

    if not primary_metric:

        raise ValueError(
            'primary_metric is required.'
        )

    _validate_metric_direction(
        direction
    )

    current_status = current_result.get(
        'status'
    )

    candidate_status = candidate_result.get(
        'status'
    )

    if current_status != 'valid':

        return {

            'status':
                CONTINUOUS_LEARNING_REJECTED,

            'decision':
                CANDIDATE_NOT_EVALUATED,

            'reason':
                'Current model evaluation is not valid.',

            'metric_comparison':
                None,
        }

    if candidate_status != 'valid':

        return {

            'status':
                CONTINUOUS_LEARNING_REJECTED,

            'decision':
                CANDIDATE_REJECTED,

            'reason':
                'Candidate model evaluation is not valid.',

            'metric_comparison':
                None,
        }

    if primary_metric not in current_result:

        raise ValueError(
            'Current result does not contain primary metric: '
            f'{primary_metric}'
        )

    if primary_metric not in candidate_result:

        raise ValueError(
            'Candidate result does not contain primary metric: '
            f'{primary_metric}'
        )

    candidate_sample_count = (
        candidate_result.get(
            'sample_count'
        )
    )

    if candidate_sample_count is None:

        candidate_sample_count = (
            candidate_result.get(
                'observation_count'
            )
        )

    if candidate_sample_count is None:

        raise ValueError(
            'Candidate result must contain sample_count '
            'or observation_count.'
        )

    _validate_sample_count(
        candidate_sample_count,
        minimum_sample_count,
    )

    if candidate_sample_count < minimum_sample_count:

        return {

            'status':
                CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

            'decision':
                CANDIDATE_REJECTED,

            'reason':
                'Candidate does not contain enough samples.',

            'metric_comparison':
                None,

            'sample_count':
                candidate_sample_count,

            'minimum_sample_count':
                minimum_sample_count,
        }

    comparison = compare_metric(
        current_result[
            primary_metric
        ],
        candidate_result[
            primary_metric
        ],
        direction,
        minimum_improvement=minimum_improvement,
    )

    if comparison[
        'meets_minimum_improvement'
    ]:

        decision = (
            CANDIDATE_ACCEPTED
        )

        status = (
            CONTINUOUS_LEARNING_VALID
        )

        reason = (
            'Candidate model meets the minimum '
            'improvement requirement.'
        )

    else:

        decision = (
            CANDIDATE_REJECTED
        )

        status = (
            CONTINUOUS_LEARNING_REJECTED
        )

        reason = (
            'Candidate model does not meet the '
            'minimum improvement requirement.'
        )

    return {

        'status':
            status,

        'decision':
            decision,

        'reason':
            reason,

        'primary_metric':
            primary_metric,

        'direction':
            direction,

        'minimum_improvement':
            float(
                _to_float(
                    minimum_improvement
                )
            ),

        'sample_count':
            candidate_sample_count,

        'minimum_sample_count':
            minimum_sample_count,

        'metric_comparison':
            comparison,
    }


# ==========================================================
# CONTINUOUS LEARNING DECISION
# ==========================================================

def evaluate_candidate(
    current_result,
    candidate_result,
    primary_metric,
    direction,
    minimum_improvement=0.0,
    minimum_sample_count=1,
):
    """
    Decide whether a newly trained candidate model should
    replace the current model.

    Important:

        This function ONLY makes the decision.

        It never modifies, deletes, saves, or replaces
        a model.
    """

    comparison = compare_model_results(
        current_result=current_result,
        candidate_result=candidate_result,
        primary_metric=primary_metric,
        direction=direction,
        minimum_improvement=minimum_improvement,
        minimum_sample_count=minimum_sample_count,
    )

    return comparison


# ==========================================================
# CONTINUOUS LEARNING CYCLE
# ==========================================================

def run_continuous_learning_cycle(
    current_result,
    candidate_result,
    primary_metric,
    direction,
    minimum_improvement=0.0,
    minimum_sample_count=1,
    current_model_version=None,
    candidate_model_version=None,
):
    """
    Execute one safe continuous-learning decision cycle.

    No model mutation is performed.

    The returned object acts as an auditable decision record.
    """

    decision = evaluate_candidate(
        current_result=current_result,
        candidate_result=candidate_result,
        primary_metric=primary_metric,
        direction=direction,
        minimum_improvement=minimum_improvement,
        minimum_sample_count=minimum_sample_count,
    )

    return {

        'status':
            decision[
                'status'
            ],

        'decision':
            decision[
                'decision'
            ],

        'reason':
            decision[
                'reason'
            ],

        'primary_metric':
            primary_metric,

        'direction':
            direction,

        'current_model_version':
            current_model_version,

        'candidate_model_version':
            candidate_model_version,

        'minimum_improvement':
            decision.get(
                'minimum_improvement'
            ),

        'sample_count':
            decision.get(
                'sample_count'
            ),

        'minimum_sample_count':
            decision.get(
                'minimum_sample_count'
            ),

        'metric_comparison':
            decision.get(
                'metric_comparison'
            ),
    }


# ==========================================================
# BATCH / HISTORY MONITORING
# ==========================================================

def summarize_learning_history(
    learning_results,
):
    """
    Summarize previous continuous-learning decisions.

    Each item should contain:

        decision
        status
    """

    if learning_results is None:

        raise ValueError(
            'learning_results is required.'
        )

    if not isinstance(
        learning_results,
        (list, tuple),
    ):

        raise ValueError(
            'learning_results must be a list or tuple.'
        )

    if len(
        learning_results
    ) == 0:

        return {

            'status':
                CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

            'total_cycles':
                0,

            'accepted':
                0,

            'rejected':
                0,

            'failed_or_invalid':
                0,

            'acceptance_rate':
                None,
        }

    accepted = 0
    rejected = 0
    failed_or_invalid = 0

    for result in learning_results:

        if not isinstance(
            result,
            dict,
        ):

            raise ValueError(
                'Each learning history item must '
                'be a dictionary.'
            )

        decision = result.get(
            'decision'
        )

        status = result.get(
            'status'
        )

        if decision == CANDIDATE_ACCEPTED:

            accepted += 1

        elif decision == CANDIDATE_REJECTED:

            rejected += 1

        else:

            failed_or_invalid += 1

        if status == CONTINUOUS_LEARNING_INVALID:

            failed_or_invalid += 1

    total_cycles = len(
        learning_results
    )

    return {

        'status':
            CONTINUOUS_LEARNING_VALID,

        'total_cycles':
            total_cycles,

        'accepted':
            accepted,

        'rejected':
            rejected,

        'failed_or_invalid':
            failed_or_invalid,

        'acceptance_rate':
            float(
                accepted
                / total_cycles
            ),
    }


# ==========================================================
# SIMPLE EXECUTION
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '========== CONTINUOUS LEARNING TEST =========='
    )

    current = {

        'status':
            'valid',

        'mae':
            20.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'mae':
            15.0,

        'sample_count':
            120,
    }

    result = run_continuous_learning_cycle(

        current_result=current,

        candidate_result=candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,

        current_model_version='v1',

        candidate_model_version='v2',
    )

    print()

    print(
        'Continuous learning result:'
    )

    print(
        result
    )

    print()

    print(
        '========== CONTINUOUS LEARNING TEST PASSED =========='
    )