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

CANDIDATE_SAVED_NOT_ACTIVATED = (
    'saved_not_activated'
)


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
    ) as exc:

        raise ValueError(
            f'Value must be numeric: {value!r}'
        ) from exc

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

    IMPORTANT:

        minimum_sample_count is NOT a training restriction.

        A model may be trained and saved with fewer samples.

        This value only controls whether there is enough
        evidence to make a reliable comparison against an
        existing model.
    """

    if sample_count is None:

        raise ValueError(
            'sample_count is required.'
        )

    if minimum_sample_count is None:

        raise ValueError(
            'minimum_sample_count is required.'
        )

    if isinstance(
        sample_count,
        bool,
    ):

        raise ValueError(
            'sample_count must be an integer.'
        )

    if isinstance(
        minimum_sample_count,
        bool,
    ):

        raise ValueError(
            'minimum_sample_count must be an integer.'
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
# EVALUATION STATUS HELPERS
# ==========================================================

def _is_evaluation_valid(
    result,
):
    """
    Return True when the evaluation contains enough
    information for metric comparison.
    """

    if not isinstance(
        result,
        dict,
    ):

        return False

    if result.get(
        'status'
    ) == CONTINUOUS_LEARNING_VALID:

        return True

    if result.get(
        'evaluation_valid'
    ) is True:

        return True

    if result.get(
        'evaluation_status'
    ) == CONTINUOUS_LEARNING_VALID:

        return True

    return False



def _is_evaluation_insufficient(
    result,
):
    """
    Return True only when the evaluation explicitly indicates
    that the available data is insufficient.

    IMPORTANT:

        evaluation_valid=False by itself does NOT mean
        insufficient data.

        An explicitly invalid evaluation must remain invalid.
    """

    if not isinstance(
        result,
        dict,
    ):

        return False

    status = result.get(
        'status'
    )

    evaluation_status = result.get(
        'evaluation_status'
    )

    # ------------------------------------------------------
    # Explicit insufficient-data statuses
    # ------------------------------------------------------

    if status == CONTINUOUS_LEARNING_INSUFFICIENT_DATA:

        return True

    if evaluation_status == CONTINUOUS_LEARNING_INSUFFICIENT_DATA:

        return True

    if evaluation_status in (
        'insufficient_training_variation',
        'insufficient_test_data',
        'insufficient_data',
    ):

        return True

    # ------------------------------------------------------
    # IMPORTANT:
    #
    # Do NOT treat evaluation_valid=False as insufficient
    # data.
    #
    # It may mean the evaluation itself is invalid.
    # ------------------------------------------------------

    return False



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

        improvement_ratio = None

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
    Compare a candidate model against the current model.

    DESIGN:

        Training success
            !=
        Evaluation reliability
            !=
        Activation decision

    A trained model can therefore be saved even when its
    evaluation is insufficient.

    Rules:

        1. Invalid candidate
           -> reject and do not save.

        2. Insufficient candidate evaluation
           -> save candidate.

           If current model exists:
               do not activate.

           If no current model exists:
               activate candidate.

        3. Valid candidate + no current model
           -> accept and activate.

        4. Valid candidate + current model
           -> compare metrics.

        5. Better candidate
           -> save and activate.

        6. Valid but worse candidate
           -> save but do not activate.

    This function never changes the database.
    """

    # ------------------------------------------------------
    # Validate arguments
    # ------------------------------------------------------

    if not isinstance(
        candidate_result,
        dict,
    ):

        raise ValueError(
            'candidate_result must be a dictionary.'
        )

    if current_result is not None:

        if not isinstance(
            current_result,
            dict,
        ):

            raise ValueError(
                'current_result must be a dictionary or None.'
            )

    if not primary_metric:

        raise ValueError(
            'primary_metric is required.'
        )

    _validate_metric_direction(
        direction
    )

    # ======================================================
    # 1. INVALID CANDIDATE
    # ======================================================

    # An invalid candidate means that the candidate itself
    # cannot be trusted as a trained/evaluable model.
    #
    # This is different from insufficient data.

    candidate_is_insufficient = (
        _is_evaluation_insufficient(
            candidate_result
        )
    )

    candidate_is_valid = (
        _is_evaluation_valid(
            candidate_result
        )
    )

    if (
        not candidate_is_valid
        and
        not candidate_is_insufficient
    ):

        return {

            'status':
                CONTINUOUS_LEARNING_INVALID,

            'decision':
                CANDIDATE_REJECTED,

            'reason':
                (
                    'Candidate model evaluation is invalid. '
                    'The candidate should not be saved or '
                    'activated.'
                ),

            'metric_comparison':
                None,

            'candidate_evaluation_valid':
                False,

            'save_candidate':
                False,

            'activate_candidate':
                False,
        }

    # ======================================================
    # 2. INSUFFICIENT EVALUATION
    # ======================================================

    if candidate_is_insufficient:

        # --------------------------------------------------
        # No current model
        # --------------------------------------------------
        #
        # There is nothing better to protect.
        #
        # The candidate becomes the initial model even though
        # its quality cannot yet be measured reliably.
        #
        # This implements the agreed principle:
        #
        #     "A little light is better than darkness."
        #

        if current_result is None:

            return {

                'status':
                    CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

                'decision':
                    CANDIDATE_SAVED_NOT_ACTIVATED,

                'reason':
                    (
                        'Candidate model was trained successfully, '
                        'but available data is insufficient for a '
                        'reliable evaluation. No current model '
                        'exists, so the candidate will be saved and '
                        'activated as the initial model.'
                    ),

                'metric_comparison':
                    None,

                'candidate_evaluation_valid':
                    False,

                'save_candidate':
                    True,

                'activate_candidate':
                    True,
            }

        # --------------------------------------------------
        # Current model exists
        # --------------------------------------------------
        #
        # Save the candidate for historical purposes, but do
        # not replace a model whose quality is already known.
        #

        return {

            'status':
                CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

            'decision':
                CANDIDATE_SAVED_NOT_ACTIVATED,

            'reason':
                (
                    'Candidate model was trained successfully, '
                    'but available data is insufficient for a '
                    'reliable comparison. The candidate will be '
                    'saved to history but will not replace the '
                    'current model.'
                ),

            'metric_comparison':
                None,

            'candidate_evaluation_valid':
                False,

            'save_candidate':
                True,

            'activate_candidate':
                False,
        }

    # ======================================================
    # 3. VALID CANDIDATE + NO CURRENT MODEL
    # ======================================================

    if current_result is None:

        if primary_metric not in candidate_result:

            return {

                'status':
                    CONTINUOUS_LEARNING_INVALID,

                'decision':
                    CANDIDATE_REJECTED,

                'reason':
                    (
                        'Candidate evaluation is valid but '
                        'does not contain the required primary '
                        f'metric: {primary_metric}'
                    ),

                'metric_comparison':
                    None,

                'candidate_evaluation_valid':
                    True,

                'save_candidate':
                    False,

                'activate_candidate':
                    False,
            }

        # --------------------------------------------------
        # First reliable model
        # --------------------------------------------------

        return {

            'status':
                CONTINUOUS_LEARNING_VALID,

            'decision':
                CANDIDATE_ACCEPTED,

            'reason':
                (
                    'No current model exists. The successfully '
                    'evaluated candidate is accepted as the '
                    'initial model.'
                ),

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
                candidate_result.get(
                    'sample_count',
                    candidate_result.get(
                        'observation_count'
                    ),
                ),

            'minimum_sample_count':
                minimum_sample_count,

            'metric_comparison':
                None,

            'candidate_evaluation_valid':
                True,

            'save_candidate':
                True,

            'activate_candidate':
                True,
        }

    # ======================================================
    # 4. CURRENT MODEL EVALUATION
    # ======================================================

    if not _is_evaluation_valid(
        current_result
    ):

        return {

            'status':
                CONTINUOUS_LEARNING_REJECTED,

            'decision':
                CANDIDATE_NOT_EVALUATED,

            'reason':
                (
                    'Current model evaluation is not valid. '
                    'The candidate cannot be reliably compared '
                    'against the current model.'
                ),

            'metric_comparison':
                None,

            'candidate_evaluation_valid':
                True,

            'save_candidate':
                True,

            'activate_candidate':
                False,
        }

    # ======================================================
    # 5. METRIC EXISTENCE
    # ======================================================

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

    # ======================================================
    # 6. SAMPLE COUNT
    # ======================================================

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

    # ------------------------------------------------------
    # Not enough samples for comparison
    #
    # Again:
    #
    #     TRAINING IS ALLOWED.
    #     SAVING IS ALLOWED.
    #     ACTIVATION IS NOT ALLOWED.
    # ------------------------------------------------------

    if candidate_sample_count < minimum_sample_count:

        return {

            'status':
                CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

            'decision':
                CANDIDATE_SAVED_NOT_ACTIVATED,

            'reason':
                (
                    'Candidate model was trained and may be '
                    'saved, but it does not contain enough '
                    'samples for reliable comparison with '
                    'the current model.'
                ),

            'metric_comparison':
                None,

            'sample_count':
                candidate_sample_count,

            'minimum_sample_count':
                minimum_sample_count,

            'candidate_evaluation_valid':
                True,

            'save_candidate':
                True,

            'activate_candidate':
                False,
        }

    # ======================================================
    # 7. COMPARE METRICS
    # ======================================================

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

    # ======================================================
    # 8. CANDIDATE BETTER
    # ======================================================

    if comparison[
        'meets_minimum_improvement'
    ]:

        return {

            'status':
                CONTINUOUS_LEARNING_VALID,

            'decision':
                CANDIDATE_ACCEPTED,

            'reason':
                (
                    'Candidate model meets the minimum '
                    'improvement requirement and may replace '
                    'the current model.'
                ),

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

            'candidate_evaluation_valid':
                True,

            'save_candidate':
                True,

            'activate_candidate':
                True,
        }

    # ======================================================
    # 9. CANDIDATE NOT BETTER
    # ======================================================

    return {

        'status':
            CONTINUOUS_LEARNING_REJECTED,

        'decision':
            CANDIDATE_REJECTED,

        'reason':
            (
                'Candidate model is valid but does not meet '
                'the minimum improvement requirement. It '
                'will be saved to history but will not '
                'replace the current model.'
            ),

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

        'candidate_evaluation_valid':
            True,

        'save_candidate':
            True,

        'activate_candidate':
            False,
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
    Decide what should happen with a newly trained model.

    This function never modifies the model or database.
    """

    return compare_model_results(

        current_result=current_result,

        candidate_result=candidate_result,

        primary_metric=primary_metric,

        direction=direction,

        minimum_improvement=minimum_improvement,

        minimum_sample_count=minimum_sample_count,
    )


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
    Execute one continuous-learning decision cycle.

    No database operation is performed here.

    The returned object tells the caller explicitly:

        save_candidate
        activate_candidate
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
            decision.get(
                'status'
            ),

        'decision':
            decision.get(
                'decision'
            ),

        'reason':
            decision.get(
                'reason'
            ),

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

        'candidate_evaluation_valid':
            decision.get(
                'candidate_evaluation_valid',
                False,
            ),

        'save_candidate':
            decision.get(
                'save_candidate',
                False,
            ),

        'activate_candidate':
            decision.get(
                'activate_candidate',
                False,
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

            'saved_not_activated':
                0,

            'failed_or_invalid':
                0,

            'acceptance_rate':
                None,
        }

    accepted = 0
    rejected = 0
    saved_not_activated = 0
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

        elif decision == CANDIDATE_SAVED_NOT_ACTIVATED:

            saved_not_activated += 1

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

        'saved_not_activated':
            saved_not_activated,

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
        '=================================================='
    )

    print(
        '          CONTINUOUS LEARNING TEST'
    )

    print(
        '=================================================='
    )

    # ======================================================
    # TEST 1
    # Valid and better candidate
    # ======================================================

    current = {

        'status':
            CONTINUOUS_LEARNING_VALID,

        'mae':
            100.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            CONTINUOUS_LEARNING_VALID,

        'mae':
            80.0,

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
        'Valid better candidate:'
    )

    print(
        result
    )

    assert result[
        'decision'
    ] == CANDIDATE_ACCEPTED

    assert result[
        'save_candidate'
    ] is True

    assert result[
        'activate_candidate'
    ] is True

    # ======================================================
    # TEST 2
    # Insufficient candidate with current model
    # ======================================================

    weak_candidate = {

        'status':
            CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

        'evaluation_valid':
            False,

        'evaluation_status':
            'insufficient_training_variation',

        'sample_count':
            5,
    }

    weak_result = run_continuous_learning_cycle(

        current_result=current,

        candidate_result=weak_candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,

        current_model_version='v1',

        candidate_model_version='v3',
    )

    print()
    print(
        'Insufficient-data candidate with current model:'
    )

    print(
        weak_result
    )

    assert weak_result[
        'decision'
    ] == CANDIDATE_SAVED_NOT_ACTIVATED

    assert weak_result[
        'save_candidate'
    ] is True

    assert weak_result[
        'activate_candidate'
    ] is False

    # ======================================================
    # TEST 3
    # First model with insufficient data
    # ======================================================

    first_model = {

        'status':
            CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

        'evaluation_valid':
            False,

        'evaluation_status':
            'insufficient_training_variation',

        'sample_count':
            5,
    }

    first_result = run_continuous_learning_cycle(

        current_result=None,

        candidate_result=first_model,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,

        current_model_version=None,

        candidate_model_version='v1',
    )

    print()
    print(
        'First model with insufficient data:'
    )

    print(
        first_result
    )

    assert first_result[
        'decision'
    ] == CANDIDATE_SAVED_NOT_ACTIVATED

    assert first_result[
        'save_candidate'
    ] is True

    assert first_result[
        'activate_candidate'
    ] is True

    # ======================================================
    # TEST 4
    # Invalid candidate
    # ======================================================

    invalid_candidate = {

        'status':
            CONTINUOUS_LEARNING_INVALID,

        'evaluation_valid':
            False,

        'evaluation_status':
            'invalid',
    }

    invalid_result = run_continuous_learning_cycle(

        current_result=current,

        candidate_result=invalid_candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,

        current_model_version='v1',

        candidate_model_version='v4',
    )

    print()
    print(
        'Invalid candidate:'
    )

    print(
        invalid_result
    )

    assert invalid_result[
        'decision'
    ] == CANDIDATE_REJECTED

    assert invalid_result[
        'save_candidate'
    ] is False

    assert invalid_result[
        'activate_candidate'
    ] is False

    # ======================================================
    # TEST 5
    # Valid candidate but worse than current
    # ======================================================

    worse_candidate = {

        'status':
            CONTINUOUS_LEARNING_VALID,

        'evaluation_valid':
            True,

        'evaluation_status':
            CONTINUOUS_LEARNING_VALID,

        'mae':
            120.0,

        'sample_count':
            120,
    }

    worse_result = run_continuous_learning_cycle(

        current_result=current,

        candidate_result=worse_candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,

        current_model_version='v1',

        candidate_model_version='v5',
    )

    print()
    print(
        'Valid but worse candidate:'
    )

    print(
        worse_result
    )

    assert worse_result[
        'decision'
    ] == CANDIDATE_REJECTED

    assert worse_result[
        'save_candidate'
    ] is True

    assert worse_result[
        'activate_candidate'
    ] is False

    # ======================================================
    # TEST 6
    # Valid candidate with too few samples
    # ======================================================

    low_sample_candidate = {

        'status':
            CONTINUOUS_LEARNING_VALID,

        'evaluation_valid':
            True,

        'evaluation_status':
            CONTINUOUS_LEARNING_VALID,

        'mae':
            50.0,

        'sample_count':
            3,
    }

    low_sample_result = run_continuous_learning_cycle(

        current_result=current,

        candidate_result=low_sample_candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,

        current_model_version='v1',

        candidate_model_version='v6',
    )

    print()
    print(
        'Valid candidate with too few comparison samples:'
    )

    print(
        low_sample_result
    )

    assert low_sample_result[
        'decision'
    ] == CANDIDATE_SAVED_NOT_ACTIVATED

    assert low_sample_result[
        'save_candidate'
    ] is True

    assert low_sample_result[
        'activate_candidate'
    ] is False

    # ======================================================
    # TEST 7
    # Valid first model
    # ======================================================

    valid_first_model = {

        'status':
            CONTINUOUS_LEARNING_VALID,

        'evaluation_valid':
            True,

        'evaluation_status':
            CONTINUOUS_LEARNING_VALID,

        'mae':
            75.0,

        'sample_count':
            20,
    }

    valid_first_result = run_continuous_learning_cycle(

        current_result=None,

        candidate_result=valid_first_model,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,

        current_model_version=None,

        candidate_model_version='v1',
    )

    print()
    print(
        'Valid first model:'
    )

    print(
        valid_first_result
    )

    assert valid_first_result[
        'decision'
    ] == CANDIDATE_ACCEPTED

    assert valid_first_result[
        'save_candidate'
    ] is True

    assert valid_first_result[
        'activate_candidate'
    ] is True

    # ======================================================
    # TEST 8
    # Missing primary metric
    # ======================================================

    missing_metric_candidate = {

        'status':
            CONTINUOUS_LEARNING_VALID,

        'evaluation_valid':
            True,

        'evaluation_status':
            CONTINUOUS_LEARNING_VALID,

        'sample_count':
            20,
    }

    missing_metric_result = (
        run_continuous_learning_cycle(

            current_result=None,

            candidate_result=missing_metric_candidate,

            primary_metric='mae',

            direction=IMPROVEMENT_MINIMIZE,

            minimum_improvement=1.0,

            minimum_sample_count=10,

            current_model_version=None,

            candidate_model_version='v7',
        )
    )

    print()
    print(
        'Candidate missing primary metric:'
    )

    print(
        missing_metric_result
    )

    assert missing_metric_result[
        'decision'
    ] == CANDIDATE_REJECTED

    assert missing_metric_result[
        'save_candidate'
    ] is False

    assert missing_metric_result[
        'activate_candidate'
    ] is False

    # ======================================================
    # TEST 9
    # Metric comparison
    # ======================================================

    metric_result = compare_metric(

        current_value=100.0,

        candidate_value=80.0,

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=10.0,
    )

    print()
    print(
        'Metric comparison:'
    )

    print(
        metric_result
    )

    assert metric_result[
        'improved'
    ] is True

    assert metric_result[
        'meets_minimum_improvement'
    ] is True

    assert metric_result[
        'improvement'
    ] == 20.0

    # ======================================================
    # TEST 10
    # History summary
    # ======================================================

    history = [

        result,

        weak_result,

        first_result,

        invalid_result,

        worse_result,

        low_sample_result,

        valid_first_result,
    ]

    summary = summarize_learning_history(
        history
    )

    print()
    print(
        'Learning history summary:'
    )

    print(
        summary
    )

    assert summary[
        'total_cycles'
    ] == 7

    assert summary[
        'accepted'
    ] == 2

    assert summary[
        'rejected'
    ] == 2

    assert summary[
        'saved_not_activated'
    ] == 3

    print()
    print(
        '=================================================='
    )

    print(
        '     CONTINUOUS LEARNING TEST SUITE PASSED'
    )

    print(
        '=================================================='
    )