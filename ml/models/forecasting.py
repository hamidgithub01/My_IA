from ml.models.regression import (
    create_regression_model,
)

from ml.models.classification import (
    create_classification_model,
)

from ml.models.multiclass import (
    create_multiclass_model,
)


# ==========================================================
# MODEL TYPE
# ==========================================================

def get_model_type(
    target_type,
    class_count=None,
):
    """
    Determine the appropriate model family.

    Returns:

        regression
        classification
        multiclass
    """

    if target_type == 'numeric':

        return 'regression'

    if target_type == 'categorical':

        if class_count is None:
            raise ValueError(
                'class_count is required for categorical '
                'targets.'
            )

        if class_count <= 2:
            return 'classification'

        return 'multiclass'

    raise ValueError(
        f'Unsupported target type: {target_type}'
    )


# ==========================================================
# MODEL CREATION
# ==========================================================

def create_forecasting_model(
    target_type,
    class_count=None,
):
    """
    Create the appropriate model for a target.

    Architecture:

        Target
           ↓
        Target Type
           ↓
        Model Family
           ↓
        Specialized Model
    """

    model_type = get_model_type(
        target_type,
        class_count,
    )

    if model_type == 'regression':

        return create_regression_model()

    if model_type == 'classification':

        return create_classification_model()

    if model_type == 'multiclass':

        return create_multiclass_model()

    raise ValueError(
        f'Unsupported model type: {model_type}'
    )