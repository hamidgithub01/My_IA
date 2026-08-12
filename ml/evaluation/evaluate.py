from ml.features.build import build_feature_dataset
from ml.training.train import train_model
from ml.evaluation.metrics import calculate_metrics


def evaluate_model():
    """
    Evaluate the trained financial model.

    Note:
        The current project dataset is very small.
        Therefore, evaluation is performed on the same
        dataset used for training.

        This is suitable for pipeline verification,
        but not for measuring real-world generalization.
    """

    data = build_feature_dataset()

    if not data:
        raise ValueError(
            'No feature data available for evaluation.'
        )

    training_result = train_model()

    model = training_result['model']
    feature_names = training_result['feature_names']

    # ------------------------------------------------------
    # Build feature matrix and target
    # ------------------------------------------------------

    X = []

    y_true = []

    for row in data:

        X.append([
            float(row[feature])
            for feature in feature_names
        ])

        y_true.append(
            float(row['Expense_Total'])
        )

    # ------------------------------------------------------
    # Predictions
    # ------------------------------------------------------

    y_pred = model.predict(X)

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    metrics = calculate_metrics(
        y_true,
        y_pred,
    )

    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    return {
        'metrics': metrics,
        'training_rows': len(data),
        'feature_names': feature_names,
        'actual_values': y_true,
        'predicted_values': [
            float(value)
            for value in y_pred
        ],
    }