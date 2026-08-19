from datetime import date, timedelta

import numpy as np
from sklearn.linear_model import LinearRegression

from ml.evaluation.evaluate import (
    evaluate_model,
)

from ml.training.continuous_learning import (
    run_continuous_learning_cycle,
    IMPROVEMENT_MINIMIZE,
)


# ==========================================================
# TEST CONFIGURATION
# ==========================================================

TARGET_NAME = (
    'Target_Expense_Total_1D'
)

SYNTHETIC_TOTAL_ROWS = 40

TRAINING_RATIO = 0.80


# ==========================================================
# SYNTHETIC DATASET
# ==========================================================

def build_synthetic_dataset():
    """
    Build a completely synthetic supervised dataset.

    IMPORTANT:

        This dataset does NOT use the database.

        It exists only to verify that the training and
        evaluation architecture can operate correctly when
        real user data becomes available in the future.

    Structure:

        Date
        Feature_Income
        Feature_Previous_Expense
        Feature_Weekend
        Target_Expense_Total_1D
    """

    dataset = []

    start_date = date(
        2026,
        1,
        1,
    )

    for index in range(
        SYNTHETIC_TOTAL_ROWS
    ):

        current_date = (
            start_date
            +
            timedelta(
                days=index
            )
        )

        # --------------------------------------------------
        # Synthetic features
        # --------------------------------------------------

        income = (
            3000.0
            +
            (
                index * 25.0
            )
        )

        previous_expense = (
            500.0
            +
            (
                (index % 7)
                * 35.0
            )
        )

        weekend = (
            1
            if current_date.weekday() >= 5
            else 0
        )

        # --------------------------------------------------
        # Synthetic target
        #
        # The target is deliberately generated from the
        # features with a deterministic relationship.
        #
        # This gives the model something learnable.
        # --------------------------------------------------

        target = (
            0.10 * income
            +
            0.60 * previous_expense
            +
            75.0 * weekend
        )

        # --------------------------------------------------
        # Add deterministic variation.
        #
        # This prevents the test from becoming unrealistically
        # perfect while keeping the relationship learnable.
        # --------------------------------------------------

        variation = (
            ((index % 5) - 2)
            * 12.5
        )

        target += variation

        dataset.append({

            'Date':
                current_date,

            'Feature_Income':
                income,

            'Feature_Previous_Expense':
                previous_expense,

            'Feature_Weekend':
                weekend,

            TARGET_NAME:
                target,
        })

    return dataset


# ==========================================================
# DATASET VALIDATION
# ==========================================================

def validate_synthetic_dataset(
    dataset,
):
    """
    Validate the synthetic supervised dataset.
    """

    assert dataset is not None
    assert len(dataset) == (
        SYNTHETIC_TOTAL_ROWS
    )

    assert all(
        TARGET_NAME in row
        for row in dataset
    )

    assert all(
        'Date' in row
        for row in dataset
    )

    dates = [
        row['Date']
        for row in dataset
    ]

    assert dates == sorted(
        dates
    )

    assert len(dates) == len(
        set(dates)
    )

    feature_names = [
        'Feature_Income',
        'Feature_Previous_Expense',
        'Feature_Weekend',
    ]

    for row in dataset:

        for feature_name in feature_names:

            assert isinstance(
                row[feature_name],
                (
                    int,
                    float,
                ),
            )

        assert isinstance(
            row[TARGET_NAME],
            (
                int,
                float,
            ),
        )


# ==========================================================
# BUILD TRAIN / TEST DATA
# ==========================================================

def prepare_synthetic_training_data(
    dataset,
):
    """
    Prepare chronological X/y train/test arrays.

    No shuffle is performed.
    """

    feature_names = [
        'Feature_Income',
        'Feature_Previous_Expense',
        'Feature_Weekend',
    ]

    split_index = int(
        len(dataset)
        *
        TRAINING_RATIO
    )

    split_index = max(
        1,
        split_index,
    )

    split_index = min(
        len(dataset) - 1,
        split_index,
    )

    training_data = dataset[
        :split_index
    ]

    test_data = dataset[
        split_index:
    ]

    X_train = [
        [
            row[feature]
            for feature in feature_names
        ]
        for row in training_data
    ]

    y_train = [
        row[TARGET_NAME]
        for row in training_data
    ]

    X_test = [
        [
            row[feature]
            for feature in feature_names
        ]
        for row in test_data
    ]

    y_test = [
        row[TARGET_NAME]
        for row in test_data
    ]

    return {

        'dataset':
            dataset,

        'feature_names':
            feature_names,

        'target_name':
            TARGET_NAME,

        'training_data':
            training_data,

        'test_data':
            test_data,

        'X_train':
            X_train,

        'y_train':
            y_train,

        'X_test':
            X_test,

        'y_test':
            y_test,

        'training_rows':
            len(training_data),

        'test_rows':
            len(test_data),
    }


# ==========================================================
# BUILD TRAINING RESULT
# ==========================================================

def train_synthetic_model(
    prepared_data,
):
    """
    Train a real LinearRegression model using only the
    synthetic dataset.

    The returned structure intentionally matches the
    training_result contract expected by evaluate_model().
    """

    model = LinearRegression()

    model.fit(
        prepared_data['X_train'],
        prepared_data['y_train'],
    )

    return {

        'model':
            model,

        'target_name':
            prepared_data[
                'target_name'
            ],

        'target_task':
            'regression',

        'target_type':
            'numeric',

        'model_type':
            'regression',

        'algorithm':
            model.__class__.__name__,

        'class_count':
            None,

        'classes':
            None,

        'feature_names':
            prepared_data[
                'feature_names'
            ],

        'training_rows':
            prepared_data[
                'training_rows'
            ],

        'test_rows':
            prepared_data[
                'test_rows'
            ],

        'training_data':
            prepared_data[
                'training_data'
            ],

        'test_data':
            prepared_data[
                'test_data'
            ],

        'X_train':
            prepared_data[
                'X_train'
            ],

        'y_train':
            prepared_data[
                'y_train'
            ],

        'X_test':
            prepared_data[
                'X_test'
            ],

        'y_test':
            prepared_data[
                'y_test'
            ],

        'validation_report': {

            'target_name':
                prepared_data[
                    'target_name'
                ],

            'target_type':
                'numeric',

            'total_rows':
                len(
                    prepared_data[
                        'dataset'
                    ]
                ),

            'training_rows':
                prepared_data[
                    'training_rows'
                ],

            'test_rows':
                prepared_data[
                    'test_rows'
                ],

            'feature_count':
                len(
                    prepared_data[
                        'feature_names'
                    ]
                ),
        },
    }


# ==========================================================
# MAIN INTEGRATION TEST
# ==========================================================

def test_continuous_learning_integration():

    print()
    print(
        '=================================================='
    )

    print(
        '       CONTINUOUS LEARNING INTEGRATION TEST'
    )

    print(
        '=================================================='
    )

    print()

    print(
        'Using SYNTHETIC dataset.'
    )

    print(
        'Real database data is NOT used for training.'
    )

    print()

    # ======================================================
    # 1. Build synthetic dataset
    # ======================================================

    dataset = (
        build_synthetic_dataset()
    )

    validate_synthetic_dataset(
        dataset
    )

    print(
        'Synthetic dataset: PASS'
    )

    # ======================================================
    # 2. Prepare chronological training/test data
    # ======================================================

    prepared_data = (
        prepare_synthetic_training_data(
            dataset
        )
    )

    assert prepared_data[
        'training_rows'
    ] == 32

    assert prepared_data[
        'test_rows'
    ] == 8

    assert (
        prepared_data[
            'training_rows'
        ]
        +
        prepared_data[
            'test_rows'
        ]
        ==
        len(dataset)
    )

    print(
        'Training rows:',
        prepared_data[
            'training_rows'
        ]
    )

    print(
        'Test rows:',
        prepared_data[
            'test_rows'
        ]
    )

    # ======================================================
    # 3. Verify chronological split
    # ======================================================

    training_dates = [
        row['Date']
        for row in prepared_data[
            'training_data'
        ]
    ]

    test_dates = [
        row['Date']
        for row in prepared_data[
            'test_data'
        ]
    ]

    assert training_dates
    assert test_dates

    assert max(
        training_dates
    ) < min(
        test_dates
    )

    print()
    print(
        'Chronological split: PASS'
    )

    # ======================================================
    # 4. Train candidate model
    # ======================================================

    training_result = (
        train_synthetic_model(
            prepared_data
        )
    )

    assert training_result is not None

    assert training_result[
        'model'
    ] is not None

    assert (
        training_result[
            'target_name'
        ]
        ==
        TARGET_NAME
    )

    assert (
        training_result[
            'model_type'
        ]
        ==
        'regression'
    )

    assert (
        training_result[
            'algorithm'
        ]
        ==
        'LinearRegression'
    )

    print()
    print(
        'Model training: PASS'
    )

    print(
        'Algorithm:',
        training_result[
            'algorithm'
        ]
    )

    # ======================================================
    # 5. Evaluate candidate model
    # ======================================================

    evaluation_result = evaluate_model(
        training_result
    )

    assert evaluation_result is not None

    print()
    print(
        '========== DEBUG EVALUATION =========='
    )

    print(
        'evaluation_status:',
        evaluation_result[
            'evaluation_status'
        ]
    )

    print(
        'evaluation_valid:',
        evaluation_result[
            'evaluation_valid'
        ]
    )

    print(
        'training_rows:',
        evaluation_result[
            'training_rows'
        ]
    )

    print(
        'test_rows:',
        evaluation_result[
            'testing_rows'
        ]
    )

    print(
        'y_train:',
        training_result[
            'y_train'
        ]
    )

    print(
        'unique y_train:',
        set(
            training_result[
                'y_train'
            ]
        )
    )

    print(
        'y_test:',
        training_result[
            'y_test'
        ]
    )

    print(
        'metrics:',
        evaluation_result[
            'metrics'
        ]
    )

    print(
        '======================================'
    )

    # ======================================================
    # 6. Evaluation must be valid
    # ======================================================

    assert (
        evaluation_result[
            'evaluation_valid'
        ]
        is True
    )

    metrics = evaluation_result.get(
        'metrics'
    )

    assert isinstance(
        metrics,
        dict,
    )

    assert 'mae' in metrics
    assert 'rmse' in metrics
    assert 'r_squared' in metrics

    candidate_mae = metrics[
        'mae'
    ]

    candidate_rmse = metrics[
        'rmse'
    ]

    candidate_r_squared = metrics[
        'r_squared'
    ]

    assert candidate_mae is not None
    assert candidate_rmse is not None
    assert candidate_r_squared is not None

    assert np.isfinite(
        candidate_mae
    )

    assert np.isfinite(
        candidate_rmse
    )

    assert np.isfinite(
        candidate_r_squared
    )

    print()
    print(
        'Model evaluation: PASS'
    )

    print(
        'MAE:',
        candidate_mae
    )

    print(
        'RMSE:',
        candidate_rmse
    )

    print(
        'R²:',
        candidate_r_squared
    )

    # ======================================================
    # 7. Verify chronological evaluation
    # ======================================================

    assert (
        evaluation_result[
            'chronological_evaluation'
        ]
        is True
    )

    assert (
        evaluation_result[
            'chronological_boundary_valid'
        ]
        is True
    )

    print()
    print(
        'Chronological evaluation: PASS'
    )

    # ======================================================
    # 8. Create synthetic current model
    #
    # IMPORTANT:
    #
    # This is deliberately NOT loaded from model_history.
    #
    # The integration test must remain independent from
    # the current database contents.
    # ======================================================

    current_result = {

        'status':
            'valid',

        # Synthetic baseline performance.
        #
        # Candidate MAE is expected to be lower than this.
        'mae':
            100.0,

        'sample_count':
            prepared_data[
                'training_rows'
            ],
    }

    assert current_result[
        'status'
    ] == 'valid'

    assert current_result[
        'mae'
    ] is not None

    print()
    print(
        'Synthetic current model: PASS'
    )

    print(
        'Current MAE:',
        current_result[
            'mae'
        ]
    )

    # ======================================================
    # 9. Create candidate result
    # ======================================================

    candidate_result = {

        'status':
            'valid',

        'mae':
            float(
                candidate_mae
            ),

        'sample_count':
            training_result[
                'training_rows'
            ],
    }

    assert candidate_result[
        'status'
    ] == 'valid'

    assert candidate_result[
        'mae'
    ] is not None

    print()
    print(
        'Candidate model: PASS'
    )

    print(
        'Candidate MAE:',
        candidate_result[
            'mae'
        ]
    )

    # ======================================================
    # 10. Continuous learning decision
    # ======================================================

    decision = (
        run_continuous_learning_cycle(

            current_result=
                current_result,

            candidate_result=
                candidate_result,

            primary_metric=
                'mae',

            direction=
                IMPROVEMENT_MINIMIZE,

            minimum_improvement=
                0.0,

            minimum_sample_count=
                1,

            current_model_version=
                'synthetic-current',

            candidate_model_version=
                'synthetic-candidate',
        )
    )

    assert decision is not None

    assert decision[
        'decision'
    ] in (
        'accepted',
        'rejected',
        'not_evaluated',
    )

    # ======================================================
    # 11. Candidate should be accepted
    #
    # Current MAE = 100
    #
    # Candidate MAE should be approximately 86.42
    #
    # Lower MAE = better.
    # ======================================================

    assert candidate_result[
        'mae'
    ] < current_result[
        'mae'
    ]

    assert decision[
        'decision'
    ] == 'accepted'

    print()
    print(
        'Continuous learning decision: PASS'
    )

    print(
        'Decision:',
        decision[
            'decision'
        ]
    )

    # ======================================================
    # 12. Confirm no database dependency
    # ======================================================

    print()
    print(
        'Database dependency: NOT USED'
    )

    print(
        'model_history was NOT read.'
    )

    print(
        'model_history was NOT modified.'
    )

    # ======================================================
    # FINAL SUCCESS
    # ======================================================

    print()
    print(
        '=================================================='
    )

    print(
        'CONTINUOUS LEARNING INTEGRATION TEST PASSED'
    )

    print(
        '=================================================='
    )

    print()


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    test_continuous_learning_integration()