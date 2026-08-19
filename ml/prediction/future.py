from datetime import date, datetime

from ml.prediction.forecast import (
    forecast_expenses,
)

from ml.training.load import (
    load_model_history,
)


# ==========================================================
# MODEL LOADING
# ==========================================================

def load_forecast_model(
    model_history_id,
):
    """
    Load a persisted model and its feature schema
    for future forecasting.
    """

    if isinstance(
        model_history_id,
        bool,
    ) or not isinstance(
        model_history_id,
        int,
    ):

        raise TypeError(
            'model_history_id must be an integer.'
        )

    if model_history_id <= 0:

        raise ValueError(
            'model_history_id must be greater than zero.'
        )

    model_result = load_model_history(
        model_history_id
    )

    if not isinstance(
        model_result,
        dict,
    ):

        raise ValueError(
            'Invalid model history result.'
        )

    if 'model' not in model_result:

        raise ValueError(
            'Model history contains no model.'
        )

    if 'feature_names' not in model_result:

        raise ValueError(
            'Model history contains no feature names.'
        )

    model = model_result[
        'model'
    ]

    feature_names = model_result[
        'feature_names'
    ]

    if model is None:

        raise ValueError(
            'Stored model is None.'
        )

    if not callable(
        getattr(
            model,
            'predict',
            None,
        )
    ):

        raise ValueError(
            'Stored model does not provide '
            'a callable predict() method.'
        )

    if not isinstance(
        feature_names,
        list,
    ) or not feature_names:

        raise ValueError(
            'Stored model contains an invalid '
            'feature schema.'
        )

    return {
        'model':
            model,

        'feature_names':
            list(feature_names),

        'model_history_id':
            model_result.get(
                'model_history_id',
                model_history_id,
            ),

        'target_name':
            model_result.get(
                'target_name'
            ),

        'target_task':
            model_result.get(
                'target_task'
            ),

        'target_type':
            model_result.get(
                'target_type'
            ),

        'model_type':
            model_result.get(
                'model_type'
            ),

        'algorithm':
            model_result.get(
                'algorithm'
            ),

        'trained_at':
            model_result.get(
                'trained_at'
            ),
    }


# ==========================================================
# DATE VALIDATION
# ==========================================================

def _validate_target_date(
    target_date,
):
    """
    Validate and normalize one forecast date.
    """

    if isinstance(
        target_date,
        datetime,
    ):

        return target_date.date()

    if not isinstance(
        target_date,
        date,
    ):

        raise TypeError(
            'target_date must be a datetime.date '
            'or datetime.datetime object.'
        )

    return target_date


# ==========================================================
# FUTURE CONTEXT VALIDATION
# ==========================================================

def _validate_future_context(
    future_context,
):
    """
    Validate future context mapping.

    Expected format:

        {
            date(...): {
                ...
            },
            date(...): {
                ...
            },
        }
    """

    if future_context is None:

        return {}

    if not isinstance(
        future_context,
        dict,
    ):

        raise TypeError(
            'future_context must be a dictionary.'
        )

    normalized_context = {}

    for context_date, context in (
        future_context.items()
    ):

        normalized_date = _validate_target_date(
            context_date
        )

        if context is None:

            normalized_context[
                normalized_date
            ] = {}

            continue

        if not isinstance(
            context,
            dict,
        ):

            raise TypeError(
                'Future context for each date '
                'must be a dictionary.'
            )

        normalized_context[
            normalized_date
        ] = dict(
            context
        )

    return normalized_context


# ==========================================================
# ONE-DAY FUTURE PREDICTION
# ==========================================================

def predict_future_expense(
    model_history_id,
    target_date,
    future_context=None,
):
    """
    Predict expense for one future date.

    The persisted model is loaded automatically.

    Returns:

        {
            'Date': date,
            'Predicted_Expense': float,
            'Features': {...},
            'Model_History_ID': int,
            'Target': str,
            'Algorithm': str,
        }
    """

    target_date = _validate_target_date(
        target_date
    )

    future_context = _validate_future_context(
        future_context
    )

    model_result = load_forecast_model(
        model_history_id
    )

    results = forecast_expenses(
        model=model_result[
            'model'
        ],

        feature_names=model_result[
            'feature_names'
        ],

        start_date=target_date,

        days=1,

        future_context=future_context,
    )

    if len(results) != 1:

        raise ValueError(
            'Future forecast returned an unexpected '
            'number of predictions.'
        )

    prediction = dict(
        results[0]
    )

    prediction[
        'Model_History_ID'
    ] = model_result[
        'model_history_id'
    ]

    prediction[
        'Target'
    ] = model_result[
        'target_name'
    ]

    prediction[
        'Target_Task'
    ] = model_result[
        'target_task'
    ]

    prediction[
        'Algorithm'
    ] = model_result[
        'algorithm'
    ]

    return prediction


# ==========================================================
# MULTI-DAY FUTURE PREDICTION
# ==========================================================

def predict_future_expenses(
    model_history_id,
    start_date,
    days=30,
    future_context=None,
):
    """
    Predict expenses for multiple future days.

    Forecasting is recursive.

    Earlier predictions become temporary historical
    information for later forecast dates.

    No predictions are written to the database.
    """

    start_date = _validate_target_date(
        start_date
    )

    if isinstance(
        days,
        bool,
    ) or not isinstance(
        days,
        int,
    ):

        raise TypeError(
            'days must be an integer.'
        )

    if days <= 0:

        raise ValueError(
            'days must be greater than zero.'
        )

    future_context = _validate_future_context(
        future_context
    )

    model_result = load_forecast_model(
        model_history_id
    )

    predictions = forecast_expenses(
        model=model_result[
            'model'
        ],

        feature_names=model_result[
            'feature_names'
        ],

        start_date=start_date,

        days=days,

        future_context=future_context,
    )

    for prediction in predictions:

        prediction[
            'Model_History_ID'
        ] = model_result[
            'model_history_id'
        ]

        prediction[
            'Target'
        ] = model_result[
            'target_name'
        ]

        prediction[
            'Target_Task'
        ] = model_result[
            'target_task'
        ]

        prediction[
            'Algorithm'
        ] = model_result[
            'algorithm'
        ]

    return predictions


# ==========================================================
# SIMPLE MANUAL TEST
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )

    print(
        '          FUTURE PREDICTION TEST'
    )

    print(
        '=================================================='
    )

    model_history_id = 29

    target_date = date(
        2026,
        8,
        18,
    )

    result = predict_future_expense(
        model_history_id=model_history_id,
        target_date=target_date,
    )

    print()
    print(
        'Model history ID:',
        result[
            'Model_History_ID'
        ]
    )

    print(
        'Target:',
        result[
            'Target'
        ]
    )

    print(
        'Algorithm:',
        result[
            'Algorithm'
        ]
    )

    print(
        'Date:',
        result[
            'Date'
        ]
    )

    print(
        'Predicted expense:',
        result[
            'Predicted_Expense'
        ]
    )

    print(
        'Feature count:',
        len(
            result[
                'Features'
            ]
        )
    )

    print()
    print(
        '=================================================='
    )

    print(
        '       FUTURE PREDICTION TEST PASSED'
    )

    print(
        '=================================================='
    )