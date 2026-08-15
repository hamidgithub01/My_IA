from sklearn.linear_model import LinearRegression


# ==========================================================
# REGRESSION MODEL
# ==========================================================

def create_regression_model():
    """
    Create the default regression model.

    Used for numeric targets such as:

        Target_Expense_Total_1D
        Target_Income_Total_1D
        Target_Balance_1D

    The model is intentionally simple at this stage.

    Model optimization will be handled later after enough
    real historical data becomes available.
    """

    return LinearRegression()