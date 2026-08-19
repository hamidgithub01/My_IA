# Final Prediction Reliability / Monitoring Layer

## Separation of responsibilities

- `ml.prediction.reliability`: **model-level reliability**. Evaluates a model on a batch of actual/predicted values and compares regression performance with a baseline.
- `ml.prediction.monitoring`: **prediction-level monitoring**. Creates pending records, evaluates individual predictions after actual values arrive, aggregates errors, and monitors score changes.
- `ml.prediction.reliability_monitoring`: **high-level facade** over prediction-level monitoring.
- `ml.prediction.tests.test_reliability_monitoring_integration`: cross-module and edge-case tests.

## Important semantic distinction

`reliability_score` from `reliability.py` is a model-level score relative to a baseline. `reliability_level` from `monitoring.py` is the quality of one observed prediction based on relative error. They intentionally measure different things.

## Test

From the project root:

```bash
python -m unittest discover -s ml/prediction/tests -p "test_*.py" -v
```
