from sklearn.linear_model import LogisticRegression


# ==========================================================
# MULTICLASS CLASSIFICATION MODEL
# ==========================================================

def create_multiclass_model():
    """
    Create the default multiclass classification model.

    Used when a categorical target contains more than two
    possible classes.

    LogisticRegression automatically handles multiclass
    classification in the installed scikit-learn version.
    """

    return LogisticRegression(
        max_iter=1000,
    )