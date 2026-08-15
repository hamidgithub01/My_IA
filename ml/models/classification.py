from sklearn.linear_model import LogisticRegression


# ==========================================================
# BINARY CLASSIFICATION MODEL
# ==========================================================

def create_classification_model():
    """
    Create the default binary classification model.

    Used for targets containing two classes, for example:

        0 / 1

    Examples:

        Target_Has_Activity_1D
        Target_Working_Day_1D
        Target_Travel_Day_1D
        Target_Has_Event_1D
    """

    return LogisticRegression(
        max_iter=1000,
    )