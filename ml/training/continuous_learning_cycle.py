# ==========================================================
# CONTINUOUS LEARNING CYCLE
# ==========================================================

from ml.training.continuous_learning import (
    CONTINUOUS_LEARNING_VALID,
    CONTINUOUS_LEARNING_REJECTED,
    CONTINUOUS_LEARNING_INSUFFICIENT_DATA,
    CANDIDATE_ACCEPTED,
    CANDIDATE_REJECTED,
    CANDIDATE_NOT_EVALUATED,
    CANDIDATE_SAVED_NOT_ACTIVATED,
    IMPROVEMENT_MINIMIZE,
    IMPROVEMENT_MAXIMIZE,
    run_continuous_learning_cycle,
)

from ml.training.train import (
    train_target_model,
)

from ml.evaluation.evaluate import (
    evaluate_model,
)

from ml.models.registry import (
    REGISTRY_VALID,
    save_registered_model,
    activate_registered_model,
    get_active_model_version,
)


# ==========================================================
# CYCLE STATUS
# ==========================================================

CYCLE_VALID = 'valid'

CYCLE_REJECTED = 'rejected'

CYCLE_FAILED = 'failed'


# ==========================================================
# BASIC VALIDATION
# ==========================================================

def _validate_model(
    model,
):
    """
    Validate that a candidate model can be persisted.
    """

    if model is None:

        raise ValueError(
            'candidate_model is required.'
        )

    if not hasattr(
        model,
        'predict',
    ):

        raise ValueError(
            'candidate_model must provide '
            'a predict() method.'
        )


def _validate_metadata(
    metadata,
):
    """
    Validate candidate model metadata.
    """

    if not isinstance(
        metadata,
        dict,
    ):

        raise ValueError(
            'candidate_metadata must be a dictionary.'
        )

    required_fields = [
        'target_name',
        'version',
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in metadata
    ]

    if missing_fields:

        raise ValueError(
            'candidate_metadata is missing required '
            f'fields: {missing_fields}'
        )


def _validate_registry_result(
    result,
    operation,
):
    """
    Ensure a registry operation succeeded.
    """

    if not isinstance(
        result,
        dict,
    ):

        raise ValueError(
            f'{operation} returned an invalid result.'
        )

    if result.get(
        'status'
    ) != REGISTRY_VALID:

        raise ValueError(
            f'{operation} failed: {result}'
        )


# ==========================================================
# VERSION GENERATION
# ==========================================================

def _next_model_version(
    current_model_version,
):
    """
    Generate the next patch version for a candidate model.

    Examples:

        v1.0.0 -> v1.0.1
        v1.2.3 -> v1.2.4

    The existing major/minor version is preserved.
    """

    if current_model_version is None:

        return 'v1.0.0'

    version = str(
        current_model_version
    )

    if not version.startswith(
        'v'
    ):

        raise ValueError(
            'current_model_version must start with "v".'
        )

    parts = version[1:].split(
        '.'
    )

    if len(parts) != 3:

        raise ValueError(
            'current_model_version must use '
            'semantic version format: vX.Y.Z'
        )

    try:

        major = int(
            parts[0]
        )

        minor = int(
            parts[1]
        )

        patch = int(
            parts[2]
        )

    except ValueError as exc:

        raise ValueError(
            'current_model_version must use '
            'semantic version format: vX.Y.Z'
        ) from exc

    if (
        major < 0
        or minor < 0
        or patch < 0
    ):

        raise ValueError(
            'current_model_version cannot contain '
            'negative version numbers.'
        )

    return (
        f'v{major}.'
        f'{minor}.'
        f'{patch + 1}'
    )


# ==========================================================
# BUILD CANDIDATE METADATA
# ==========================================================

def _build_candidate_metadata(
    training_result,
    candidate_version,
):
    """
    Build registry metadata directly from the real
    training result.

    No model configuration is recreated manually here.
    """

    required_fields = [
        'target_name',
        'target_task',
        'target_type',
        'model_type',
        'algorithm',
        'feature_names',
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in training_result
    ]

    if missing_fields:

        raise ValueError(
            'Training result is missing required metadata '
            f'fields: {missing_fields}'
        )

    return {

        'target_name':
            training_result[
                'target_name'
            ],

        'target_task':
            training_result[
                'target_task'
            ],

        'target_type':
            training_result[
                'target_type'
            ],

        'model_type':
            training_result[
                'model_type'
            ],

        'algorithm':
            training_result[
                'algorithm'
            ],

        'feature_names':
            training_result[
                'feature_names'
            ],

        'version':
            candidate_version,
    }


# ==========================================================
# TRAIN + EVALUATE + EXECUTE ONE REAL CYCLE
# ==========================================================

def run_continuous_learning_training_cycle(
    target_name,
    current_result,
    primary_metric,
    direction,
    minimum_improvement=0.0,
    minimum_sample_count=1,
    current_model_version=None,
    registry_dir=None,
):
    """
    Execute one real continuous-learning training cycle.

    Architecture:

        train_target_model()
                ↓
        candidate training_result
                ↓
        evaluate_model()
                ↓
        candidate evaluation
                ↓
        execute_continuous_learning_cycle()
                ↓
        save / activate

    IMPORTANT:

        This function does NOT recreate the training pipeline.

        It reuses the existing training and evaluation
        components.

        It also does NOT make the accept/reject decision
        itself.

        The decision remains owned by
        run_continuous_learning_cycle().
    """

    if not target_name:

        raise ValueError(
            'target_name is required.'
        )

    if not primary_metric:

        raise ValueError(
            'primary_metric is required.'
        )

    # ======================================================
    # 1. TRAIN CANDIDATE
    # ======================================================

    training_result = train_target_model(
        target_name
    )

    if not isinstance(
        training_result,
        dict,
    ):

        raise ValueError(
            'train_target_model() returned an invalid result.'
        )

    if 'model' not in training_result:

        raise ValueError(
            'Training result does not contain a model.'
        )

    candidate_model = training_result[
        'model'
    ]

    _validate_model(
        candidate_model
    )

    # ======================================================
    # 2. EVALUATE CANDIDATE
    # ======================================================

    candidate_result = None

    try:

        candidate_result = evaluate_model(
            training_result=training_result,
        )

    except ValueError as exc:

        message = str(
            exc
        )

        evaluation_unavailable_messages = (
            'No test features are available',
            'No test targets are available',
            'Test dataset contains fewer rows',
        )

        if not message.startswith(
            evaluation_unavailable_messages
        ):

            raise

        # --------------------------------------------------
        # Evaluation is unavailable.
        #
        # This is intentionally represented as an explicit
        # insufficient-data result rather than being treated
        # as an invalid candidate.
        # --------------------------------------------------

        candidate_result = {

            'status':
                CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

            'evaluation_valid':
                False,

            'evaluation_status':
                CONTINUOUS_LEARNING_INSUFFICIENT_DATA,

            'sample_count':
                training_result.get(
                    'test_rows',
                    0,
                ),
        }

    # ======================================================
    # 3. DETERMINE CANDIDATE VERSION
    # ======================================================

    candidate_model_version = _next_model_version(
        current_model_version
    )

    # ======================================================
    # 4. BUILD CANDIDATE METADATA
    # ======================================================

    candidate_metadata = _build_candidate_metadata(
        training_result=training_result,
        candidate_version=candidate_model_version,
    )

    # ======================================================
    # 5. EXECUTE DECISION + REGISTRY OPERATIONS
    # ======================================================

    return execute_continuous_learning_cycle(

        current_result=current_result,

        candidate_result=candidate_result,

        candidate_model=candidate_model,

        candidate_metadata=candidate_metadata,

        primary_metric=primary_metric,

        direction=direction,

        minimum_improvement=minimum_improvement,

        minimum_sample_count=minimum_sample_count,

        current_model_version=current_model_version,

        registry_dir=registry_dir,
    )


# ==========================================================
# EXECUTE ONE CONTINUOUS-LEARNING CYCLE
# ==========================================================

def execute_continuous_learning_cycle(
    current_result,
    candidate_result,
    candidate_model,
    candidate_metadata,
    primary_metric,
    direction,
    minimum_improvement=0.0,
    minimum_sample_count=1,
    current_model_version=None,
    registry_dir=None,
):
    """
    Execute one complete continuous-learning cycle.

    Responsibilities:

        1. Evaluate the candidate.
        2. Decide whether it should be saved.
        3. Save it when allowed.
        4. Activate it only when explicitly allowed.
        5. Never activate a candidate that was rejected.

    IMPORTANT:

        The decision is made BEFORE any registry mutation.

        This function does not train models.

        This function does not evaluate model quality itself.

        It only orchestrates the existing components.
    """

    _validate_model(
        candidate_model
    )

    _validate_metadata(
        candidate_metadata
    )

    target_name = candidate_metadata[
        'target_name'
    ]

    candidate_model_version = candidate_metadata[
        'version'
    ]

    # ======================================================
    # 1. MAKE CONTINUOUS-LEARNING DECISION
    # ======================================================

    decision = run_continuous_learning_cycle(

        current_result=current_result,

        candidate_result=candidate_result,

        primary_metric=primary_metric,

        direction=direction,

        minimum_improvement=minimum_improvement,

        minimum_sample_count=minimum_sample_count,

        current_model_version=current_model_version,

        candidate_model_version=candidate_model_version,
    )

    save_candidate = decision.get(
        'save_candidate',
        False,
    )

    activate_candidate = decision.get(
        'activate_candidate',
        False,
    )

    # ======================================================
    # 2. NOTHING TO SAVE
    # ======================================================

    if not save_candidate:

        return {

            'status':
                decision.get(
                    'status',
                    CYCLE_REJECTED,
                ),

            'decision':
                decision.get(
                    'decision',
                    CANDIDATE_REJECTED,
                ),

            'reason':
                decision.get(
                    'reason'
                ),

            'target_name':
                target_name,

            'candidate_model_version':
                candidate_model_version,

            'current_model_version':
                current_model_version,

            'saved':
                False,

            'activated':
                False,

            'save_result':
                None,

            'activation_result':
                None,

            'learning_decision':
                decision,
        }

    # ======================================================
    # 3. SAVE CANDIDATE
    # ======================================================

    try:

        save_result = save_registered_model(

            model=candidate_model,

            metadata=candidate_metadata,

            registry_dir=registry_dir,
        )

        _validate_registry_result(
            save_result,
            'save_registered_model',
        )

    except Exception as exc:

        return {

            'status':
                CYCLE_FAILED,

            'decision':
                decision.get(
                    'decision'
                ),

            'reason':
                (
                    'Continuous-learning decision succeeded, '
                    'but candidate model could not be saved '
                    'to the registry.'
                ),

            'error':
                str(exc),

            'target_name':
                target_name,

            'candidate_model_version':
                candidate_model_version,

            'current_model_version':
                current_model_version,

            'saved':
                False,

            'activated':
                False,

            'save_result':
                None,

            'activation_result':
                None,

            'learning_decision':
                decision,
        }

    # ======================================================
    # 4. SAVE ONLY
    # ======================================================

    if not activate_candidate:

        return {

            'status':
                decision.get(
                    'status',
                    CYCLE_VALID,
                ),

            'decision':
                decision.get(
                    'decision'
                ),

            'reason':
                decision.get(
                    'reason'
                ),

            'target_name':
                target_name,

            'candidate_model_version':
                candidate_model_version,

            'current_model_version':
                current_model_version,

            'saved':
                True,

            'activated':
                False,

            'save_result':
                save_result,

            'activation_result':
                None,

            'learning_decision':
                decision,
        }

    # ======================================================
    # 5. ACTIVATE CANDIDATE
    # ======================================================

    try:

        activation_result = activate_registered_model(

            target_name=target_name,

            version=candidate_model_version,

            registry_dir=registry_dir,
        )

        _validate_registry_result(
            activation_result,
            'activate_registered_model',
        )

    except Exception as exc:

        return {

            'status':
                CYCLE_FAILED,

            'decision':
                decision.get(
                    'decision'
                ),

            'reason':
                (
                    'Candidate model was successfully saved, '
                    'but activation failed. The previously '
                    'active model remains protected.'
                ),

            'error':
                str(exc),

            'target_name':
                target_name,

            'candidate_model_version':
                candidate_model_version,

            'current_model_version':
                current_model_version,

            'saved':
                True,

            'activated':
                False,

            'save_result':
                save_result,

            'activation_result':
                None,

            'learning_decision':
                decision,
        }

    # ======================================================
    # 6. VERIFY ACTIVE VERSION
    # ======================================================

    active_version = get_active_model_version(

        target_name=target_name,

        registry_dir=registry_dir,
    )

    if active_version != candidate_model_version:

        return {

            'status':
                CYCLE_FAILED,

            'decision':
                decision.get(
                    'decision'
                ),

            'reason':
                (
                    'Candidate activation returned success, '
                    'but registry verification did not confirm '
                    'the candidate as the active model.'
                ),

            'target_name':
                target_name,

            'candidate_model_version':
                candidate_model_version,

            'current_model_version':
                current_model_version,

            'saved':
                True,

            'activated':
                False,

            'active_version':
                active_version,

            'save_result':
                save_result,

            'activation_result':
                activation_result,

            'learning_decision':
                decision,
        }

    # ======================================================
    # 7. SUCCESS
    # ======================================================

    return {

        'status':
            CYCLE_VALID,

        'decision':
            decision.get(
                'decision'
            ),

        'reason':
            decision.get(
                'reason'
            ),

        'target_name':
            target_name,

        'candidate_model_version':
            candidate_model_version,

        'current_model_version':
            current_model_version,

        'saved':
            True,

        'activated':
            True,

        'active_version':
            active_version,

        'save_result':
            save_result,

        'activation_result':
            activation_result,

        'learning_decision':
            decision,
    }


# ==========================================================
# SIMPLE MANUAL TEST
# ==========================================================

if __name__ == '__main__':

    import tempfile

    from sklearn.linear_model import LinearRegression

    print()
    print(
        '=================================================='
    )

    print(
        '       CONTINUOUS LEARNING CYCLE TEST'
    )

    print(
        '=================================================='
    )

    registry_dir = tempfile.mkdtemp()

    target_name = (
        'Target_Expense_Total_1D'
    )

    feature_names = [
        'feature_a',
        'feature_b',
    ]

    # ======================================================
    # CREATE CURRENT MODEL
    # ======================================================

    current_model = LinearRegression()

    current_model.fit(
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

    current_metadata = {

        'target_name':
            target_name,

        'target_task':
            'regression',

        'target_type':
            'numeric',

        'model_type':
            'regression',

        'algorithm':
            'LinearRegression',

        'feature_names':
            feature_names,

        'version':
            'v1.0.0',
    }

    from ml.models.registry import (
        save_registered_model,
        activate_registered_model,
    )

    save_registered_model(
        current_model,
        current_metadata,
        registry_dir,
    )

    activate_registered_model(
        target_name,
        'v1.0.0',
        registry_dir,
    )

    # ======================================================
    # CREATE BETTER CANDIDATE
    # ======================================================

    candidate_model = LinearRegression()

    candidate_model.fit(
        [
            [1.0, 2.0],
            [2.0, 3.0],
            [3.0, 4.0],
            [4.0, 5.0],
        ],
        [
            3.0,
            5.0,
            7.0,
            9.0,
        ],
    )

    candidate_metadata = {

        'target_name':
            target_name,

        'target_task':
            'regression',

        'target_type':
            'numeric',

        'model_type':
            'regression',

        'algorithm':
            'LinearRegression',

        'feature_names':
            feature_names,

        'version':
            'v2.0.0',
    }

    current_result = {

        'status':
            CONTINUOUS_LEARNING_VALID,

        'evaluation_valid':
            True,

        'evaluation_status':
            CONTINUOUS_LEARNING_VALID,

        'mae':
            100.0,

        'sample_count':
            100,
    }

    candidate_result = {

        'status':
            CONTINUOUS_LEARNING_VALID,

        'evaluation_valid':
            True,

        'evaluation_status':
            CONTINUOUS_LEARNING_VALID,

        'mae':
            80.0,

        'sample_count':
            120,
    }

    # ======================================================
    # EXECUTE
    # ======================================================

    result = execute_continuous_learning_cycle(

        current_result=current_result,

        candidate_result=candidate_result,

        candidate_model=candidate_model,

        candidate_metadata=candidate_metadata,

        primary_metric='mae',

        direction=IMPROVEMENT_MINIMIZE,

        minimum_improvement=1.0,

        minimum_sample_count=10,

        current_model_version='v1.0.0',

        registry_dir=registry_dir,
    )

    print()
    print(
        '========== CYCLE RESULT =========='
    )

    print(
        result
    )

    # ======================================================
    # ASSERTIONS
    # ======================================================

    assert result[
        'status'
    ] == CYCLE_VALID

    assert result[
        'decision'
    ] == CANDIDATE_ACCEPTED

    assert result[
        'saved'
    ] is True

    assert result[
        'activated'
    ] is True

    assert result[
        'active_version'
    ] == 'v2.0.0'

    assert result[
        'save_result'
    ] is not None

    assert result[
        'activation_result'
    ] is not None

    print()
    print(
        '=================================================='
    )

    print(
        '   CONTINUOUS LEARNING CYCLE TEST PASSED'
    )

    print(
        '=================================================='
    )