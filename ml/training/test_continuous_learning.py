from ml.training.continuous_learning import (
    CONTINUOUS_LEARNING_VALID,
    CONTINUOUS_LEARNING_REJECTED,
    CONTINUOUS_LEARNING_INSUFFICIENT_DATA,
    CANDIDATE_ACCEPTED,
    CANDIDATE_REJECTED,
    IMPROVEMENT_MINIMIZE,
    IMPROVEMENT_MAXIMIZE,
    compare_metric,
    compare_model_results,
    evaluate_candidate,
    run_continuous_learning_cycle,
    summarize_learning_history,
)


# ==========================================================
# TEST HELPERS
# ==========================================================

def assert_close(
    actual,
    expected,
    tolerance=1e-9,
):
    """
    Assert approximate numeric equality.
    """

    assert abs(
        actual - expected
    ) < tolerance, (
        f'Expected {expected}, got {actual}'
    )


# ==========================================================
# MINIMIZE METRIC
# ==========================================================

def test_compare_metric_minimize():
    """
    Lower metric value is better.
    """

    result = compare_metric(
        current_value=20.0,
        candidate_value=15.0,
        direction=IMPROVEMENT_MINIMIZE,
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
        is True
    )


# ==========================================================
# MAXIMIZE METRIC
# ==========================================================

def test_compare_metric_maximize():
    """
    Higher metric value is better.
    """

    result = compare_metric(
        current_value=0.70,
        candidate_value=0.80,
        direction=IMPROVEMENT_MAXIMIZE,
    )

    assert_close(
        result['improvement'],
        0.10,
    )

    assert (
        result['improved']
        is True
    )


# ==========================================================
# MINIMUM IMPROVEMENT
# ==========================================================

def test_minimum_improvement():
    """
    Small improvements can be rejected when they do not
    reach the configured threshold.
    """

    result = compare_metric(
        current_value=20.0,
        candidate_value=19.5,
        direction=IMPROVEMENT_MINIMIZE,
        minimum_improvement=1.0,
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
# REGRESSION CANDIDATE ACCEPTED
# ==========================================================

def test_regression_candidate_accepted():
    """
    Candidate with lower MAE should be accepted.
    """

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

    result = compare_model_results(

        current,

        candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_VALID
    )

    assert (
        result['decision']
        == CANDIDATE_ACCEPTED
    )


# ==========================================================
# REGRESSION CANDIDATE REJECTED
# ==========================================================

def test_regression_candidate_rejected():
    """
    Candidate with worse MAE must be rejected.
    """

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
            25.0,

        'sample_count':
            120,
    }

    result = compare_model_results(

        current,

        candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_sample_count=10,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_REJECTED
    )

    assert (
        result['decision']
        == CANDIDATE_REJECTED
    )


# ==========================================================
# CLASSIFICATION CANDIDATE ACCEPTED
# ==========================================================

def test_classification_candidate_accepted():
    """
    Candidate with higher accuracy should be accepted.
    """

    current = {

        'status':
            'valid',

        'accuracy':
            0.75,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'accuracy':
            0.82,

        'sample_count':
            120,
    }

    result = evaluate_candidate(

        current,

        candidate,

        primary_metric='accuracy',

        direction=IMPROVEMENT_MAXIMIZE,

        minimum_improvement=0.01,

        minimum_sample_count=10,
    )

    assert (
        result['decision']
        == CANDIDATE_ACCEPTED
    )


# ==========================================================
# MULTICLASS CLASSIFICATION
# ==========================================================

def test_multiclass_candidate():
    """
    Continuous learning must not assume binary
    classification.
    """

    current = {

        'status':
            'valid',

        'accuracy':
            0.60,

        'sample_count':
            200,
    }

    candidate = {

        'status':
            'valid',

        'accuracy':
            0.68,

        'sample_count':
            220,
    }

    result = evaluate_candidate(

        current,

        candidate,

        primary_metric='accuracy',

        direction=IMPROVEMENT_MAXIMIZE,

        minimum_improvement=0.02,

        minimum_sample_count=10,
    )

    assert (
        result['decision']
        == CANDIDATE_ACCEPTED
    )


# ==========================================================
# INSUFFICIENT DATA
# ==========================================================

def test_insufficient_candidate_data():
    """
    Candidate with insufficient data must not be accepted.
    """

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
            10.0,

        'sample_count':
            3,
    }

    result = compare_model_results(

        current,

        candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_sample_count=10,
    )

    assert (
        result['status']
        == CONTINUOUS_LEARNING_INSUFFICIENT_DATA
    )

    assert (
        result['decision']
        == CANDIDATE_REJECTED
    )


# ==========================================================
# INVALID CURRENT MODEL
# ==========================================================

def test_invalid_current_model():
    """
    Invalid current evaluation must prevent a learning
    decision.
    """

    current = {

        'status':
            'invalid',

        'mae':
            20.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'mae':
            10.0,

        'sample_count':
            100,
    }

    result = compare_model_results(

        current,

        candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,
    )

    assert (
        result['decision']
        != CANDIDATE_ACCEPTED
    )


# ==========================================================
# INVALID CANDIDATE
# ==========================================================

def test_invalid_candidate():
    """
    Invalid candidate must never replace the current model.
    """

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
            'invalid',

        'mae':
            1.0,

        'sample_count':
            100,
    }

    result = compare_model_results(

        current,

        candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,
    )

    assert (
        result['decision']
        == CANDIDATE_REJECTED
    )


# ==========================================================
# EQUAL PERFORMANCE
# ==========================================================

def test_equal_performance():
    """
    Equal performance must not count as improvement when
    a positive improvement is required.
    """

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
            20.0,

        'sample_count':
            100,
    }

    result = evaluate_candidate(

        current,

        candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=0.1,
    )

    assert (
        result['decision']
        == CANDIDATE_REJECTED
    )


# ==========================================================
# CONTINUOUS LEARNING CYCLE
# ==========================================================

def test_continuous_learning_cycle():
    """
    Verify complete decision record.
    """

    current = {

        'status':
            'valid',

        'mae':
            30.0,

        'sample_count':
            100,
    }

    candidate = {

        'status':
            'valid',

        'mae':
            20.0,

        'sample_count':
            150,
    }

    result = run_continuous_learning_cycle(

        current_result=current,

        candidate_result=candidate,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=2.0,

        minimum_sample_count=10,

        current_model_version='v1',

        candidate_model_version='v2',
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
        result['current_model_version']
        == 'v1'
    )

    assert (
        result['candidate_model_version']
        == 'v2'
    )


# ==========================================================
# HISTORY SUMMARY
# ==========================================================

def test_learning_history():
    """
    Test continuous-learning history summary.
    """

    history = [

        {
            'status':
                CONTINUOUS_LEARNING_VALID,

            'decision':
                CANDIDATE_ACCEPTED,
        },

        {
            'status':
                CONTINUOUS_LEARNING_REJECTED,

            'decision':
                CANDIDATE_REJECTED,
        },

        {
            'status':
                CONTINUOUS_LEARNING_VALID,

            'decision':
                CANDIDATE_ACCEPTED,
        },
    ]

    result = summarize_learning_history(
        history
    )

    assert (
        result['total_cycles']
        == 3
    )

    assert (
        result['accepted']
        == 2
    )

    assert (
        result['rejected']
        == 1
    )

    assert_close(
        result['acceptance_rate'],
        2.0 / 3.0,
    )


# ==========================================================
# EMPTY HISTORY
# ==========================================================

def test_empty_learning_history():
    """
    Empty history must be reported as insufficient data.
    """

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
        result['acceptance_rate']
        is None
    )


# ==========================================================
# INVALID INPUTS
# ==========================================================

def test_invalid_inputs():
    """
    Verify safe rejection of invalid inputs.
    """

    # ------------------------------------------------------
    # Invalid metric direction
    # ------------------------------------------------------

    try:

        compare_metric(
            10,
            5,
            'invalid',
        )

        assert False

    except ValueError:

        pass

    # ------------------------------------------------------
    # Negative improvement
    # ------------------------------------------------------

    try:

        compare_metric(
            10,
            5,
            IMPROVEMENT_MINIMIZE,
            minimum_improvement=-1,
        )

        assert False

    except ValueError:

        pass

    # ------------------------------------------------------
    # Invalid current result
    # ------------------------------------------------------

    try:

        compare_model_results(
            None,
            {},
            'mae',
            IMPROVEMENT_MINIMIZE,
        )

        assert False

    except ValueError:

        pass

    # ------------------------------------------------------
    # Missing metric
    # ------------------------------------------------------

    try:

        compare_model_results(
            {
                'status':
                    'valid',
            },
            {
                'status':
                    'valid',
                'sample_count':
                    10,
            },
            'mae',
            IMPROVEMENT_MINIMIZE,
        )

        assert False

    except ValueError:

        pass

    # ------------------------------------------------------
    # Invalid history
    # ------------------------------------------------------

    try:

        summarize_learning_history(
            None
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# MAIN TEST SUITE
# ==========================================================

if __name__ == '__main__':

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

    test_compare_metric_minimize()

    test_compare_metric_maximize()

    test_minimum_improvement()

    test_regression_candidate_accepted()

    test_regression_candidate_rejected()

    test_classification_candidate_accepted()

    test_multiclass_candidate()

    test_insufficient_candidate_data()

    test_invalid_current_model()

    test_invalid_candidate()

    test_equal_performance()

    test_continuous_learning_cycle()

    test_learning_history()

    test_empty_learning_history()

    test_invalid_inputs()

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