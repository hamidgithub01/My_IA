from ml.training.continuous_learning import (
    CONTINUOUS_LEARNING_VALID,
    CONTINUOUS_LEARNING_REJECTED,
    CONTINUOUS_LEARNING_INSUFFICIENT_DATA,
    CONTINUOUS_LEARNING_INVALID,

    CANDIDATE_ACCEPTED,
    CANDIDATE_REJECTED,
    CANDIDATE_NOT_EVALUATED,
    CANDIDATE_SAVED_NOT_ACTIVATED,

    IMPROVEMENT_MINIMIZE,
    IMPROVEMENT_MAXIMIZE,

    compare_metric,
    compare_model_results,
    evaluate_candidate,
    run_continuous_learning_cycle,
    summarize_learning_history,
)


# ==========================================================
# HELPERS
# ==========================================================

def assert_close(
    actual,
    expected,
    tolerance=1e-9,
):
    """
    Assert that two numeric values are approximately equal.
    """

    assert abs(
        actual - expected
    ) <= tolerance, (
        f'Expected {expected}, got {actual}'
    )


# ==========================================================
# TEST 1
# MINIMIZE METRIC
# ==========================================================

def test_compare_metric_minimize():

    result = compare_metric(
        current_value=100.0,
        candidate_value=80.0,
        direction=IMPROVEMENT_MINIMIZE,
        minimum_improvement=10.0,
    )

    assert (
        result['current_value']
        == 100.0
    )

    assert (
        result['candidate_value']
        == 80.0
    )

    assert_close(
        result['improvement'],
        20.0,
    )

    assert_close(
        result['improvement_ratio'],
        0.20,
    )

    assert (
        result['improved']
        is True
    )

    assert (
        result['meets_minimum_improvement']
        is True
    )


# ==========================================================
# TEST 2
# MAXIMIZE METRIC
# ==========================================================

def test_compare_metric_maximize():

    result = compare_metric(
        current_value=0.70,
        candidate_value=0.85,
        direction=IMPROVEMENT_MAXIMIZE,
        minimum_improvement=0.10,
    )

    assert_close(
        result['improvement'],
        0.15,
    )

    assert_close(
        result['improvement_ratio'],
        0.15 / 0.70,
    )

    assert (
        result['improved']
        is True
    )

    assert (
        result['meets_minimum_improvement']
        is True
    )


# ==========================================================
# TEST 3
# MINIMUM IMPROVEMENT NOT MET
# ==========================================================

def test_minimum_improvement_not_met():

    result = compare_metric(
        current_value=100.0,
        candidate_value=95.0,
        direction=IMPROVEMENT_MINIMIZE,
        minimum_improvement=10.0,
    )

    assert_close(
        result['improvement'],
        5.0,
    )

    assert (
        result['improved']
        is True
    )

    assert (
        result['meets_minimum_improvement']
        is False
    )


# ==========================================================
# TEST 4
# EQUAL PERFORMANCE
# ==========================================================

def test_equal_performance():

    result = compare_metric(
        current_value=100.0,
        candidate_value=100.0,
        direction=IMPROVEMENT_MINIMIZE,
        minimum_improvement=0.0,
    )

    assert (
        result['improvement']
        == 0.0
    )

    assert (
        result['improved']
        is False
    )

    assert (
        result['meets_minimum_improvement']
        is True
    )


# ==========================================================
# TEST 5
# CURRENT MODEL INVALID
# ==========================================================

def test_invalid_current_model():

    current = {

        'status':
            'invalid',

        'mae':
            100.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'mae':
            80.0,

        'sample_count':
            100,
    }

    result = compare_model_results(

        current_result=current,

        candidate_result=candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=0.0,

        minimum_sample_count=1,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_REJECTED
    )

    assert (
        result['decision']
        == CANDIDATE_NOT_EVALUATED
    )

    assert (
        result['metric_comparison']
        is None
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is False
    )


# ==========================================================
# TEST 6
# CANDIDATE INVALID
# ==========================================================

def test_invalid_candidate():

    current = {

        'status':
            'valid',

        'mae':
            100.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'invalid',

        'mae':
            50.0,

        'sample_count':
            100,
    }

    result = compare_model_results(

        current_result=current,

        candidate_result=candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=0.0,

        minimum_sample_count=1,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_INVALID
    )

    assert (
        result['decision']
        == CANDIDATE_REJECTED
    )

    assert (
        result['save_candidate']
        is False
    )

    assert (
        result['activate_candidate']
        is False
    )


# ==========================================================
# TEST 7
# REGRESSION CANDIDATE ACCEPTED
# ==========================================================

def test_regression_candidate_accepted():

    current = {

        'status':
            'valid',

        'mae':
            100.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'mae':
            80.0,

        'sample_count':
            120,
    }

    result = evaluate_candidate(

        current_result=current,

        candidate_result=candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=10.0,

        minimum_sample_count=1,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_VALID
    )

    assert (
        result['decision']
        == CANDIDATE_ACCEPTED
    )

    assert (
        result['metric_comparison']
        is not None
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is True
    )


# ==========================================================
# TEST 8
# REGRESSION CANDIDATE REJECTED
# ==========================================================

def test_regression_candidate_rejected():

    current = {

        'status':
            'valid',

        'mae':
            100.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'mae':
            95.0,

        'sample_count':
            120,
    }

    result = evaluate_candidate(

        current_result=current,

        candidate_result=candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=10.0,

        minimum_sample_count=1,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_REJECTED
    )

    assert (
        result['decision']
        == CANDIDATE_REJECTED
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is False
    )


# ==========================================================
# TEST 9
# CLASSIFICATION / MAXIMIZE
# ==========================================================

def test_classification_candidate_accepted():

    current = {

        'status':
            'valid',

        'accuracy':
            0.70,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'accuracy':
            0.85,

        'sample_count':
            120,
    }

    result = evaluate_candidate(

        current_result=current,

        candidate_result=candidate,

        primary_metric='accuracy',

        direction=IMPROVEMENT_MAXIMIZE,

        minimum_improvement=0.05,

        minimum_sample_count=1,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_VALID
    )

    assert (
        result['decision']
        == CANDIDATE_ACCEPTED
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is True
    )


# ==========================================================
# TEST 10
# MULTICLASS / MAXIMIZE
# ==========================================================

def test_multiclass_candidate_rejected():

    current = {

        'status':
            'valid',

        'accuracy':
            0.90,

        'sample_count':
            200,
    }

    candidate = {

        'status':
            'valid',

        'accuracy':
            0.89,

        'sample_count':
            220,
    }

    result = evaluate_candidate(

        current_result=current,

        candidate_result=candidate,

        primary_metric='accuracy',

        direction=IMPROVEMENT_MAXIMIZE,

        minimum_improvement=0.01,

        minimum_sample_count=1,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_REJECTED
    )

    assert (
        result['decision']
        == CANDIDATE_REJECTED
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is False
    )


# ==========================================================
# TEST 11
# LOW DATA MUST NOT BLOCK TRAINING OR SAVING
# ==========================================================

def test_insufficient_candidate_data():

    current = {

        'status':
            'valid',

        'mae':
            100.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'mae':
            80.0,

        # Intentionally very small.
        'sample_count':
            3,
    }

    result = evaluate_candidate(

        current_result=current,

        candidate_result=candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=10.0,

        # This value is intentionally larger
        # than the candidate sample count.
        minimum_sample_count=10,
    )

    # ------------------------------------------------------
    # IMPORTANT ARCHITECTURE
    #
    # Insufficient comparison data does NOT mean:
    #
    #     training failed
    #
    # The candidate may be saved.
    #
    # But because a current model already exists,
    # the candidate must NOT replace it.
    # ------------------------------------------------------

    assert (
        result['decision']
        == CANDIDATE_SAVED_NOT_ACTIVATED
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_INSUFFICIENT_DATA
    )

    assert (
        result['sample_count']
        == 3
    )

    assert (
        result['minimum_sample_count']
        == 10
    )

    assert (
        result['metric_comparison']
        is None
    )

    assert (
        result['candidate_evaluation_valid']
        is True
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is False
    )


# ==========================================================
# TEST 12
# ZERO CURRENT METRIC
# ==========================================================

def test_zero_current_metric():

    result = compare_metric(

        current_value=0.0,

        candidate_value=0.0,

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=0.0,
    )

    assert (
        result['improvement']
        == 0.0
    )

    assert (
        result['improvement_ratio']
        is None
    )

    assert (
        result['meets_minimum_improvement']
        is True
    )


# ==========================================================
# TEST 13
# CONTINUOUS LEARNING CYCLE
# ==========================================================

def test_continuous_learning_cycle():

    current = {

        'status':
            'valid',

        'mae':
            100.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

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

        minimum_improvement=10.0,

        minimum_sample_count=1,

        current_model_version='v1',

        candidate_model_version='v2',
    )

    assert result is not None

    assert (
        result['status']
        == CONTINUOUS_LEARNING_VALID
    )

    assert (
        result['decision']
        == CANDIDATE_ACCEPTED
    )

    assert (
        result['current_model_version']
        == 'v1'
    )

    assert (
        result['candidate_model_version']
        == 'v2'
    )

    assert (
        result['primary_metric']
        == 'mae'
    )

    assert (
        result['direction']
        == IMPROVEMENT_MINIMIZE
    )

    assert (
        result['metric_comparison']
        is not None
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is True
    )


# ==========================================================
# TEST 14
# LEARNING HISTORY SUMMARY
# ==========================================================

def test_learning_history_summary():

    history = [

        {
            'decision':
                CANDIDATE_ACCEPTED,

            'status':
                CONTINUOUS_LEARNING_VALID,
        },

        {
            'decision':
                CANDIDATE_REJECTED,

            'status':
                CONTINUOUS_LEARNING_REJECTED,
        },

        {
            'decision':
                CANDIDATE_ACCEPTED,

            'status':
                CONTINUOUS_LEARNING_VALID,
        },

        {
            'decision':
                CANDIDATE_NOT_EVALUATED,

            'status':
                CONTINUOUS_LEARNING_REJECTED,
        },
    ]

    result = summarize_learning_history(
        history
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_VALID
    )

    assert (
        result['total_cycles']
        == 4
    )

    assert (
        result['accepted']
        == 2
    )

    assert (
        result['rejected']
        == 1
    )

    assert (
        result['saved_not_activated']
        == 0
    )

    assert (
        result['failed_or_invalid']
        == 1
    )

    assert_close(
        result['acceptance_rate'],
        0.5,
    )


# ==========================================================
# TEST 15
# EMPTY HISTORY
# ==========================================================

def test_empty_learning_history():

    result = summarize_learning_history(
        []
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_INSUFFICIENT_DATA
    )

    assert (
        result['total_cycles']
        == 0
    )

    assert (
        result['accepted']
        == 0
    )

    assert (
        result['rejected']
        == 0
    )

    assert (
        result['saved_not_activated']
        == 0
    )

    assert (
        result['failed_or_invalid']
        == 0
    )

    assert (
        result['acceptance_rate']
        is None
    )


# ==========================================================
# TEST 16
# NO CURRENT MODEL IS VALID
# ==========================================================

def test_none_current_model_is_allowed():

    candidate = {

        'status':
            'valid',

        'evaluation_valid':
            True,

        'evaluation_status':
            CONTINUOUS_LEARNING_VALID,

        'mae':
            10.0,

        'sample_count':
            20,
    }

    result = compare_model_results(

        current_result=None,

        candidate_result=candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=0.0,

        minimum_sample_count=1,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_VALID
    )

    assert (
        result['decision']
        == CANDIDATE_ACCEPTED
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is True
    )

    assert (
        result['primary_metric']
        == 'mae'
    )


# ==========================================================
# TEST 17
# INVALID DIRECTION
# ==========================================================

def test_invalid_direction():

    try:

        compare_metric(

            current_value=100.0,

            candidate_value=90.0,

            direction='invalid',

            minimum_improvement=0.0,
        )

    except ValueError:

        return

    assert False, (
        'Expected ValueError for invalid direction.'
    )


# ==========================================================
# TEST 18
# NEGATIVE MINIMUM IMPROVEMENT
# ==========================================================

def test_negative_minimum_improvement():

    try:

        compare_metric(

            current_value=100.0,

            candidate_value=90.0,

            direction=IMPROVEMENT_MINIMIZE,

            minimum_improvement=-1.0,
        )

    except ValueError:

        return

    assert False, (
        'Expected ValueError for negative '
        'minimum_improvement.'
    )


# ==========================================================
# TEST 19
# MISSING PRIMARY METRIC
# ==========================================================

def test_missing_primary_metric():

    current = {

        'status':
            'valid',

        'mae':
            100.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'sample_count':
            100,
    }

    try:

        compare_model_results(

            current_result=current,

            candidate_result=candidate,

            primary_metric='mae',

            direction=IMPROVEMENT_MINIMIZE,
        )

    except ValueError:

        return

    assert False, (
        'Expected ValueError for missing '
        'candidate primary metric.'
    )


# ==========================================================
# TEST 20
# MISSING SAMPLE COUNT
# ==========================================================

def test_missing_sample_count():

    current = {

        'status':
            'valid',

        'mae':
            100.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'mae':
            80.0,
    }

    try:

        compare_model_results(

            current_result=current,

            candidate_result=candidate,

            primary_metric='mae',

            direction=IMPROVEMENT_MINIMIZE,
        )

    except ValueError:

        return

    assert False, (
        'Expected ValueError for missing '
        'candidate sample_count.'
    )


# ==========================================================
# TEST 21
# FIRST MODEL WITH INSUFFICIENT DATA
# ==========================================================

def test_first_model_with_insufficient_data():

    candidate = {

        'status':
            CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

        'evaluation_valid':
            False,

        'evaluation_status':
            'insufficient_training_variation',

        'sample_count':
            5,
    }

    result = run_continuous_learning_cycle(

        current_result=None,

        candidate_result=candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,

        current_model_version=None,

        candidate_model_version='v1',
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_INSUFFICIENT_DATA
    )

    assert (
        result['decision']
        == CANDIDATE_SAVED_NOT_ACTIVATED
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is True
    )


# ==========================================================
# TEST 22
# INSUFFICIENT CANDIDATE WITH CURRENT MODEL
# ==========================================================

def test_insufficient_candidate_with_current_model():

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
            CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

        'evaluation_valid':
            False,

        'evaluation_status':
            'insufficient_training_variation',

        'sample_count':
            5,
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

    assert (
        result['status']
        == CONTINUOUS_LEARNING_INSUFFICIENT_DATA
    )

    assert (
        result['decision']
        == CANDIDATE_SAVED_NOT_ACTIVATED
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is False
    )


# ==========================================================
# TEST 23
# VALID CANDIDATE WITH TOO FEW SAMPLES
# ==========================================================

def test_valid_candidate_with_too_few_samples():

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

        'evaluation_valid':
            True,

        'evaluation_status':
            CONTINUOUS_LEARNING_VALID,

        'mae':
            50.0,

        'sample_count':
            3,
    }

    result = evaluate_candidate(

        current_result=current,

        candidate_result=candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_INSUFFICIENT_DATA
    )

    assert (
        result['decision']
        == CANDIDATE_SAVED_NOT_ACTIVATED
    )

    assert (
        result['sample_count']
        == 3
    )

    assert (
        result['minimum_sample_count']
        == 10
    )

    assert (
        result['metric_comparison']
        is None
    )

    assert (
        result['save_candidate']
        is True
    )

    assert (
        result['activate_candidate']
        is False
    )


# ==========================================================
# TEST 24
# INVALID CURRENT RESULT TYPE
# ==========================================================

def test_invalid_current_result_type():

    try:

        compare_model_results(

            current_result=None,

            candidate_result={
                'status':
                    'valid',

                'mae':
                    10.0,

                'sample_count':
                    10,
            },

            primary_metric='mae',

            direction=IMPROVEMENT_MINIMIZE,
        )

    except ValueError:

        # --------------------------------------------------
        # IMPORTANT:
        #
        # current_result=None is intentionally valid.
        #
        # Therefore this test must NOT expect ValueError.
        # --------------------------------------------------

        assert False, (
            'current_result=None is a valid first-model '
            'scenario and must not raise ValueError.'
        )

    assert True


# ==========================================================
# MAIN TEST RUNNER
# ==========================================================

def test_continuous_learning():

    print()
    print(
        '=================================================='
    )

    print(
        '       CONTINUOUS LEARNING TEST SUITE'
    )

    print(
        '=================================================='
    )

    # ------------------------------------------------------
    # Run all tests
    # ------------------------------------------------------

    test_compare_metric_minimize()

    test_compare_metric_maximize()

    test_minimum_improvement_not_met()

    test_equal_performance()

    test_invalid_current_model()

    test_invalid_candidate()

    test_regression_candidate_accepted()

    test_regression_candidate_rejected()

    test_classification_candidate_accepted()

    test_multiclass_candidate_rejected()

    test_insufficient_candidate_data()

    test_zero_current_metric()

    test_continuous_learning_cycle()

    test_learning_history_summary()

    test_empty_learning_history()

    test_none_current_model_is_allowed()

    test_invalid_direction()

    test_negative_minimum_improvement()

    test_missing_primary_metric()

    test_missing_sample_count()

    test_first_model_with_insufficient_data()

    test_insufficient_candidate_with_current_model()

    test_valid_candidate_with_too_few_samples()

    test_invalid_current_result_type()

    print()
    print(
        '=================================================='
    )

    print(
        '       ALL CONTINUOUS LEARNING TESTS PASSED'
    )

    print(
        '=================================================='
    )


# ==========================================================
# EXECUTION
# ==========================================================

if __name__ == '__main__':

    test_continuous_learning()