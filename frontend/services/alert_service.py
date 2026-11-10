
"""
Alerts & Recommendations Service
=================================

Collects evaluation and registry issues for the frontend.

This service does not:
- evaluate model quality using invented thresholds;
- treat unknown evaluation validity as invalid;
- claim that a recommendation has been executed;
- generate production reliability alerts without monitoring data.
"""

from frontend.services.evaluation_service import (
    load_evaluation_page_data,
)


# ==========================================================
# PAGE STATUS
# ==========================================================

STATUS_ISSUES_FOUND = 'issues_found'
STATUS_CLEAR = 'clear'
STATUS_SOURCE_ERROR = 'source_error'


# ==========================================================
# ALERT SEVERITY
# ==========================================================

SEVERITY_WARNING = 'warning'
SEVERITY_HIGH = 'high'


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _create_issue(
    issue_type,
    severity,
    title,
    message,
    source,
    target_name=None,
    version=None,
    details=None,
):
    return {
        'issue_type': issue_type,
        'severity': severity,
        'title': title,
        'message': message,
        'source': source,
        'target_name': target_name,
        'version': version,
        'details': details or {},
    }


def _get_records(
    evaluation_data,
):
    """
    Combine registry versions and legacy history.

    Both sources are kept separate through their
    source field.
    """

    records = []

    versions = evaluation_data.get(
        'versions',
        [],
    )

    legacy_history = evaluation_data.get(
        'legacy_history',
        [],
    )

    if isinstance(versions, list):
        records.extend(versions)

    if isinstance(legacy_history, list):
        records.extend(legacy_history)

    return [
        record
        for record in records
        if isinstance(record, dict)
    ]


def _record_details(
    record,
):
    return {
        'target_name': record.get('target_name'),
        'version': record.get('version'),
        'algorithm': record.get('algorithm'),
        'evaluation_status': record.get('evaluation_status'),
        'evaluation_validity_status': (
            record.get('evaluation_validity_status')
        ),
        'evaluation_data_status': (
            record.get('evaluation_data_status')
        ),
        'metadata_path': record.get('metadata_path'),
    }


# ==========================================================
# EVALUATION ISSUES
# ==========================================================

def _analyze_evaluation_records(
    records,
):
    alerts = []
    information = []

    unknown_validity_count = 0

    for record in records:

        target_name = record.get(
            'target_name'
        )

        version = record.get(
            'version'
        )

        source = record.get(
            'source',
            'evaluation',
        )

        details = _record_details(
            record
        )

        validity_status = record.get(
            'evaluation_validity_status'
        )

        data_status = record.get(
            'evaluation_data_status'
        )

        # --------------------------------------------------
        # Invalid evaluation
        # --------------------------------------------------

        if validity_status == 'invalid':

            alerts.append(
                _create_issue(
                    issue_type='invalid_evaluation',
                    severity=SEVERITY_HIGH,
                    title='Evaluation is invalid',
                    message=(
                        'The evaluation record is marked '
                        'as invalid and should be reviewed.'
                    ),
                    source=source,
                    target_name=target_name,
                    version=version,
                    details=details,
                )
            )

        elif validity_status == 'unknown':

            unknown_validity_count += 1

        # --------------------------------------------------
        # Missing evaluation metrics
        # --------------------------------------------------

        if data_status == 'metrics_missing':

            alerts.append(
                _create_issue(
                    issue_type='missing_evaluation_metrics',
                    severity=SEVERITY_WARNING,
                    title='Evaluation metrics are missing',
                    message=(
                        'No evaluation metrics are recorded '
                        'for this model version.'
                    ),
                    source=source,
                    target_name=target_name,
                    version=version,
                    details=details,
                )
            )

        # --------------------------------------------------
        # Invalid chronological boundary
        # --------------------------------------------------

        if (
            record.get(
                'chronological_boundary_valid'
            ) is False
        ):

            alerts.append(
                _create_issue(
                    issue_type='invalid_chronological_boundary',
                    severity=SEVERITY_HIGH,
                    title='Chronological evaluation boundary is invalid',
                    message=(
                        'The recorded chronological evaluation '
                        'boundary is invalid and should be reviewed.'
                    ),
                    source=source,
                    target_name=target_name,
                    version=version,
                    details=details,
                )
            )

    # ------------------------------------------------------
    # Aggregate unknown evaluation validity
    # ------------------------------------------------------

    if unknown_validity_count:

        information.append(
            {
                'information_type': (
                    'evaluation_validity_unknown'
                ),
                'title': 'Evaluation validity is unknown',
                'message': (
                    f'{unknown_validity_count} model version(s) '
                    'do not have a confirmed evaluation validity '
                    'status. Unknown does not mean invalid.'
                ),
                'count': unknown_validity_count,
            }
        )

    return alerts, information


# ==========================================================
# SOURCE ERRORS
# ==========================================================

def _analyze_source_errors(
    errors,
):
    alerts = []

    if not isinstance(errors, list):
        return alerts

    for error in errors:

        if not isinstance(error, dict):
            continue

        source = error.get(
            'source',
            'unknown',
        )

        message = error.get(
            'message',
            'An unknown source error occurred.',
        )

        alerts.append(
            _create_issue(
                issue_type='source_unavailable',
                severity=SEVERITY_WARNING,
                title='Data source is unavailable',
                message=str(message),
                source=source,
                details={
                    'source': source,
                },
            )
        )

    return alerts


# ==========================================================
# RECOMMENDATIONS
# ==========================================================

def _build_recommendation(
    alert,
):
    """
    Convert a known issue into a suggested action.

    Recommendations are informational only.
    No action is executed here.
    """

    issue_type = alert.get(
        'issue_type'
    )

    recommendation_map = {

        'invalid_evaluation': {
            'recommendation_type': 'review_evaluation',
            'priority': 'high',
            'title': 'Review the model evaluation',
            'message': (
                'Inspect the evaluation validity details '
                'before relying on these metrics.'
            ),
        },

        'missing_evaluation_metrics': {
            'recommendation_type': 'investigate_evaluation_metrics',
            'priority': 'medium',
            'title': 'Investigate missing evaluation metrics',
            'message': (
                'Inspect the evaluation record to determine '
                'why metrics are not available for this model version.'
            ),
        },

        'invalid_chronological_boundary': {
            'recommendation_type': 'review_temporal_split',
            'priority': 'high',
            'title': 'Review the chronological data split',
            'message': (
                'Inspect the training and testing time boundaries '
                'to identify the source of the invalid boundary.'
            ),
        },

        'source_unavailable': {
            'recommendation_type': 'restore_data_source',
            'priority': 'medium',
            'title': 'Restore the unavailable data source',
            'message': (
                'Check the affected database or registry source '
                'and restore access before relying on its records.'
            ),
        },
    }

    recommendation = recommendation_map.get(
        issue_type
    )

    if recommendation is None:
        return None

    return {
        **recommendation,
        'issue_type': issue_type,
        'target_name': alert.get('target_name'),
        'version': alert.get('version'),
        'source': alert.get('source'),
    }


def _build_recommendations(
    alerts,
):
    recommendations = []

    seen = set()

    for alert in alerts:

        recommendation = _build_recommendation(
            alert
        )

        if recommendation is None:
            continue

        key = (
            recommendation['recommendation_type'],
            recommendation.get('target_name'),
            recommendation.get('version'),
            recommendation.get('source'),
        )

        if key in seen:
            continue

        seen.add(key)

        recommendations.append(
            recommendation
        )

    return recommendations


# ==========================================================
# PUBLIC SERVICE
# ==========================================================

def load_alerts_page_data():
    """
    Load and prepare data for the Alerts page.

    Evaluation and registry issues are analyzed separately
    from production prediction monitoring.
    """

    try:

        evaluation_data = (
            load_evaluation_page_data()
        )

    except Exception as exc:

        return {
            'status': STATUS_SOURCE_ERROR,
            'overview': {},
            'alerts': [],
            'recommendations': [],
            'information': [],
            'source_errors': [
                {
                    'source': 'evaluation_service',
                    'message': str(exc),
                }
            ],
            'monitoring_status': 'not_connected',
        }

    if not isinstance(
        evaluation_data,
        dict,
    ):

        return {
            'status': STATUS_SOURCE_ERROR,
            'overview': {},
            'alerts': [],
            'recommendations': [],
            'information': [],
            'source_errors': [
                {
                    'source': 'evaluation_service',
                    'message': (
                        'Evaluation service returned '
                        'an invalid result.'
                    ),
                }
            ],
            'monitoring_status': 'not_connected',
        }

    records = _get_records(
        evaluation_data
    )

    evaluation_alerts, information = (
        _analyze_evaluation_records(
            records
        )
    )

    source_errors = evaluation_data.get(
        'errors',
        [],
    )

    source_alerts = _analyze_source_errors(
        source_errors
    )

    alerts = (
        evaluation_alerts
        + source_alerts
    )

    recommendations = _build_recommendations(
        alerts
    )

    status = (
        STATUS_ISSUES_FOUND
        if alerts
        else STATUS_CLEAR
    )

    return {
        'status': status,

        'overview': evaluation_data.get(
            'overview',
            {},
        ),

        'alerts': alerts,

        'alert_count': len(alerts),

        'recommendations': recommendations,

        'recommendation_count': len(
            recommendations
        ),

        'information': information,

        'source_errors': source_errors,

                'registry_version_count': len(
            evaluation_data.get('versions', [])
        ),

        'legacy_history_record_count': len(
            evaluation_data.get('legacy_history', [])
        ),

        'evaluation_record_count': len(records),

        'model_version_count': len(
            evaluation_data.get('versions', [])
        ),

        'monitoring_status': 'not_connected',
    }
