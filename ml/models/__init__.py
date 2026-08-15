from ml.models.regression import (
    create_regression_model,
)

from ml.models.classification import (
    create_classification_model,
)

from ml.models.multiclass import (
    create_multiclass_model,
)

from ml.models.forecasting import (
    create_forecasting_model,
    get_model_type,
)


__all__ = [
    'create_regression_model',
    'create_classification_model',
    'create_multiclass_model',
    'create_forecasting_model',
    'get_model_type',
]