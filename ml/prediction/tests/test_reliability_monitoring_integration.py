from datetime import datetime
import unittest

from ml.prediction import monitoring
from ml.prediction import reliability
from ml.prediction import reliability_monitoring


class TestReliabilityLayer(unittest.TestCase):

    def test_regression_reliability(self):
        result = reliability.calculate_regression_reliability(
            [10.0, 20.0, 30.0, 40.0],
            [10.5, 19.5, 30.5, 39.5],
            baseline_mae=5.0,
        )
        self.assertEqual(result['status'], reliability.RELIABILITY_VALID)
        self.assertEqual(result['reliability_level'], reliability.RELIABILITY_HIGH)
        self.assertAlmostEqual(result['mae'], 0.5)
        self.assertAlmostEqual(result['reliability_score'], 0.9)
        self.assertAlmostEqual(result['improvement'], 0.9)

    def test_regression_insufficient_data(self):
        result = reliability.calculate_regression_reliability(
            [10.0], [10.5], baseline_mae=5.0
        )
        self.assertEqual(result['status'], reliability.RELIABILITY_INSUFFICIENT_DATA)
        self.assertEqual(result['reliability_score'], 0.0)
        self.assertIsNone(result['improvement'])

    def test_regression_worse_than_baseline_is_bounded(self):
        result = reliability.calculate_regression_reliability(
            [0.0, 10.0], [10.0, 20.0], baseline_mae=5.0
        )
        self.assertEqual(result['reliability_score'], 0.0)
        self.assertLess(result['improvement'], 0.0)

    def test_classification_accuracy(self):
        result = reliability.calculate_classification_reliability(
            [0, 1, 0, 1, 1], [0, 1, 0, 1, 1]
        )
        self.assertEqual(result['status'], reliability.RELIABILITY_VALID)
        self.assertEqual(result['accuracy'], 1.0)
        self.assertEqual(result['reliability_score'], 1.0)
        self.assertEqual(result['reliability_level'], reliability.RELIABILITY_HIGH)

    def test_classification_numeric_labels_only(self):
        with self.assertRaises(ValueError):
            reliability.calculate_classification_reliability(
                ['good', 'bad'], ['good', 'bad']
            )

    def test_unified_api(self):
        result = reliability.evaluate_prediction_reliability(
            ' regression ', [10, 20], [11, 19], baseline_mae=5
        )
        self.assertEqual(result['status'], reliability.RELIABILITY_VALID)

        result = reliability.evaluate_prediction_reliability(
            'classification', [0, 1], [0, 1]
        )
        self.assertEqual(result['accuracy'], 1.0)

    def test_unified_regression_requires_baseline(self):
        with self.assertRaises(ValueError):
            reliability.evaluate_prediction_reliability(
                'regression', [1, 2], [1, 2]
            )

    def test_invalid_numbers(self):
        for bad in [float('nan'), float('inf'), -float('inf'), True]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    reliability.calculate_prediction_error([1, 2], [bad, 2])

    def test_monitor_model_reliability(self):
        result = reliability.monitor_prediction_reliability(
            {
                'status': reliability.RELIABILITY_VALID,
                'reliability_level': reliability.RELIABILITY_MEDIUM,
                'reliability_score': 0.65,
            },
            {
                'status': reliability.RELIABILITY_VALID,
                'reliability_level': reliability.RELIABILITY_HIGH,
                'reliability_score': 0.90,
            },
        )
        self.assertTrue(result['degraded'])
        self.assertEqual(result['status'], reliability.RELIABILITY_UNRELIABLE)
        self.assertAlmostEqual(result['score_change'], -0.25)

    def test_monitor_model_zero_threshold_means_any_negative_change(self):
        result = reliability.monitor_prediction_reliability(
            {'reliability_score': 0.89},
            {'reliability_score': 0.90},
            degradation_threshold=0.0,
        )
        self.assertTrue(result['degraded'])


class TestPredictionMonitoring(unittest.TestCase):

    def setUp(self):
        self.prediction = {
            'status': 'valid',
            'model_history_id': 29,
            'target_name': 'Target_Expense_Total_1D',
            'target_task': 'regression',
            'prediction': 100.0,
            'model_version': 'v1.0.0',
            'Date': '2026-08-18',
        }

    def test_pending_record_has_no_reliability(self):
        record = monitoring.create_monitoring_record(self.prediction)
        self.assertEqual(record['status'], monitoring.MONITORING_PENDING_ACTUAL)
        self.assertFalse(record['actual_value_available'])
        self.assertFalse(record['reliability_available'])
        self.assertEqual(record['reliability_level'], monitoring.RELIABILITY_UNKNOWN)

    def test_evaluate_prediction(self):
        record = monitoring.evaluate_prediction(self.prediction, 110.0)
        self.assertEqual(record['status'], monitoring.MONITORING_READY)
        self.assertEqual(record['actual_value'], 110.0)
        self.assertAlmostEqual(record['signed_error'], -10.0)
        self.assertAlmostEqual(record['absolute_error'], 10.0)
        self.assertAlmostEqual(record['squared_error'], 100.0)
        self.assertAlmostEqual(record['relative_error'], 10.0 / 110.0)
        self.assertEqual(record['reliability_level'], monitoring.RELIABILITY_GOOD)

    def test_actual_zero_is_unknown_relative_reliability(self):
        record = monitoring.evaluate_prediction(self.prediction, 0.0)
        self.assertIsNone(record['relative_error'])
        self.assertFalse(record['reliability_available'])
        self.assertEqual(record['reliability_level'], monitoring.RELIABILITY_UNKNOWN)
        self.assertEqual(record['reliability_status'], 'actual_value_zero')

    def test_reliability_boundaries(self):
        self.assertEqual(monitoring.classify_reliability(0.05), monitoring.RELIABILITY_EXCELLENT)
        self.assertEqual(monitoring.classify_reliability(0.10), monitoring.RELIABILITY_GOOD)
        self.assertEqual(monitoring.classify_reliability(0.20), monitoring.RELIABILITY_MODERATE)
        self.assertEqual(monitoring.classify_reliability(0.50), monitoring.RELIABILITY_LOW)
        self.assertEqual(monitoring.classify_reliability(None), monitoring.RELIABILITY_UNKNOWN)

    def test_threshold_order_validation(self):
        with self.assertRaises(ValueError):
            monitoring.classify_reliability(
                0.1,
                excellent_max_error=0.2,
                good_max_error=0.1,
            )

    def test_batch_and_summary(self):
        predictions = [
            {**self.prediction, 'prediction': 100.0},
            {**self.prediction, 'prediction': 200.0},
            {**self.prediction, 'prediction': 300.0},
            {**self.prediction, 'prediction': 400.0},
        ]
        actuals = [110.0, 190.0, 315.0, 380.0]
        records = monitoring.evaluate_prediction_batch(predictions, actuals)
        summary = monitoring.summarize_monitoring(records)
        self.assertEqual(summary['record_count'], 4)
        self.assertEqual(summary['evaluated_count'], 4)
        self.assertEqual(summary['reliability_available_count'], 4)
        self.assertAlmostEqual(summary['mean_absolute_error'], 13.75)
        self.assertAlmostEqual(summary['mean_squared_error'], 206.25)

    def test_summary_mixed_pending_and_evaluated(self):
        pending = monitoring.create_monitoring_record(self.prediction)
        evaluated = monitoring.evaluate_prediction(self.prediction, 110.0)
        summary = monitoring.summarize_monitoring([pending, evaluated])
        self.assertEqual(summary['record_count'], 2)
        self.assertEqual(summary['evaluated_count'], 1)

    def test_score_monitoring(self):
        result = monitoring.monitor_reliability(
            {
                'reliability_score': 0.90,
                'reliability_level': 'high',
                'sample_count': 100,
            },
            {
                'reliability_score': 0.70,
                'reliability_level': 'medium',
                'sample_count': 80,
            },
        )
        self.assertTrue(result['improved'])
        self.assertFalse(result['degraded'])
        self.assertEqual(result['monitoring_state'], monitoring.MONITORING_IMPROVED)

    def test_score_monitoring_degradation(self):
        result = monitoring.monitor_reliability(
            {'reliability_score': 0.70, 'sample_count': 100},
            {'reliability_score': 0.80, 'sample_count': 80},
        )
        self.assertTrue(result['degraded'])
        self.assertEqual(result['status'], monitoring.MONITORING_DEGRADED)
        self.assertEqual(result['monitoring_state'], monitoring.MONITORING_DEGRADED)

    def test_unified_score_monitoring_routes_reliability_first(self):
        result = monitoring.monitor_prediction(
            {
                'reliability_score': 0.8,
                'calibration_score': 0.1,
                'sample_count': 10,
            }
        )
        self.assertIn('current_reliability_score', result)

    def test_unified_score_monitoring_requires_known_metric(self):
        with self.assertRaises(ValueError):
            monitoring.monitor_prediction({'sample_count': 10})

    def test_timestamp_is_utc_aware(self):
        timestamp = monitoring._current_timestamp()
        parsed = datetime.fromisoformat(timestamp)
        self.assertIsNotNone(parsed.tzinfo)
        self.assertIsNotNone(parsed.utcoffset())


class TestHighLevelFacade(unittest.TestCase):

    def setUp(self):
        self.prediction = {
            'status': 'valid',
            'target_name': 'Target_Expense_Total_1D',
            'target_task': 'regression',
            'prediction': 100.0,
        }

    def test_pending_flow(self):
        result = reliability_monitoring.monitor_prediction(self.prediction)
        self.assertEqual(
            result['status'],
            reliability_monitoring.RELIABILITY_MONITORING_PENDING,
        )
        self.assertFalse(result['reliability_available'])
        self.assertEqual(result['reliability'], monitoring.RELIABILITY_UNKNOWN)

    def test_evaluated_flow(self):
        result = reliability_monitoring.monitor_prediction(
            self.prediction, actual_value=110.0
        )
        self.assertEqual(
            result['status'],
            reliability_monitoring.RELIABILITY_MONITORING_EVALUATED,
        )
        self.assertTrue(result['reliability_available'])
        self.assertEqual(result['reliability'], monitoring.RELIABILITY_GOOD)

    def test_zero_actual_flow(self):
        result = reliability_monitoring.monitor_prediction(
            self.prediction, actual_value=0.0
        )
        self.assertEqual(
            result['status'],
            reliability_monitoring.RELIABILITY_MONITORING_EVALUATED,
        )
        self.assertFalse(result['reliability_available'])
        self.assertEqual(result['reliability'], monitoring.RELIABILITY_UNKNOWN)

    def test_read_status_does_not_recalculate(self):
        record = monitoring.evaluate_prediction(self.prediction, 110.0)
        status = reliability_monitoring.get_reliability_status(record)
        self.assertEqual(
            status['status'],
            reliability_monitoring.RELIABILITY_MONITORING_EVALUATED,
        )
        self.assertEqual(status['reliability'], monitoring.RELIABILITY_GOOD)

    def test_batch_facade(self):
        predictions = [
            {**self.prediction, 'prediction': 100.0},
            {**self.prediction, 'prediction': 200.0},
        ]
        result = reliability_monitoring.monitor_prediction_batch(
            predictions, [110.0, 190.0]
        )
        self.assertEqual(result['evaluated_count'], 2)
        self.assertEqual(len(result['records']), 2)
        self.assertEqual(result['summary']['record_count'], 2)

    def test_invalid_prediction_is_rejected(self):
        with self.assertRaises(ValueError):
            reliability_monitoring.monitor_prediction(
                {'prediction': 100.0}
            )


class TestCrossModuleContract(unittest.TestCase):

    def test_model_level_result_can_feed_score_monitoring(self):
        current = reliability.calculate_regression_reliability(
            [10, 20, 30, 40], [10.5, 19.5, 30.5, 39.5], baseline_mae=5
        )
        previous = reliability.calculate_regression_reliability(
            [10, 20, 30, 40], [12, 22, 28, 42], baseline_mae=5
        )
        monitored = monitoring.monitor_reliability(current, previous)
        self.assertEqual(monitored['current_reliability_score'], current['reliability_score'])
        self.assertEqual(monitored['previous_reliability_score'], previous['reliability_score'])

    def test_individual_prediction_monitoring_is_separate_from_model_reliability(self):
        model_result = reliability.calculate_regression_reliability(
            [10, 20], [10, 20], baseline_mae=5
        )
        prediction_record = monitoring.evaluate_prediction(
            {
                'prediction': 10,
                'target_name': 'Target_X',
                'target_task': 'regression',
            },
            11,
        )
        self.assertIn('reliability_score', model_result)
        self.assertIn('relative_error', prediction_record)
        self.assertNotEqual(model_result['reliability_level'], prediction_record['reliability_level'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
