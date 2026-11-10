
import json
import os

from database.connection import get_connection
from ml.models import registry as model_registry


# ==========================================================
# CONSTANTS
# ==========================================================

EVALUATION_DATA_MISSING = 'missing'
EVALUATION_DATA_INVALID = 'invalid'


# ==========================================================
# JSON
# ==========================================================

def _decode_json(value, default=None):
    """
    Decode a JSON database field safely.
    """

    if value is None:
        return default

    if isinstance(value, (dict, list)):
        return value

    if isinstance(value, str):

        if not value.strip():
            return default

        try:
            return json.loads(value)

        except json.JSONDecodeError:
            return default

    return default


# ==========================================================
# DATABASE
# ==========================================================

def _load_legacy_model_history():
    """
    Read historical model records from MariaDB.

    These records are kept separate from File Registry
    versions because model_history has no version identifier.
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                trained_at,
                algorithm,
                model_type,
                target_name,
                target_task,
                target_type,
                class_count,
                training_rows,
                mae,
                rmse,
                r_squared,
                evaluation_status,
                evaluation_metrics,
                reused_previous_state

            FROM model_history

            ORDER BY
                trained_at DESC,
                id DESC
            """
        )

        columns = [
            column[0]
            for column in cursor.description
        ]

        records = []

        for row in cursor.fetchall():

            if isinstance(row, dict):

                record = dict(row)

            else:

                record = dict(
                    zip(
                        columns,
                        row,
                    )
                )

            record['evaluation_metrics'] = (
                _decode_json(
                    record.get(
                        'evaluation_metrics'
                    ),
                    {},
                )
            )

            record['source'] = 'model_history'

            records.append(record)

        return records, None

    except Exception as exc:

        return [], str(exc)

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ==========================================================
# FILE REGISTRY
# ==========================================================

def _get_registry_targets():
    """
    Discover target directories in the model registry.
    """

    registry_dir = model_registry._registry_path(
        None
    )

    if not os.path.isdir(registry_dir):
        return []

    targets = []

    for entry in os.listdir(registry_dir):

        target_path = os.path.join(
            registry_dir,
            entry,
        )

        if os.path.isdir(target_path):

            targets.append(entry)

    return sorted(targets)


def _load_target_versions(target_name):
    """
    Load evaluation metadata for all versions of one target.

    Model binaries are never loaded.
    """

    versions = model_registry.list_model_versions(
        target_name
    )

    active_version = (
        model_registry.get_active_model_version(
            target_name
        )
    )

    records = []
    errors = []

    for version in versions:

        try:

            result = model_registry.load_model_metadata(
                target_name,
                version,
            )

            if (
                result.get('status')
                != model_registry.REGISTRY_VALID
            ):

                errors.append({

                    'target_name':
                        target_name,

                    'version':
                        version,

                    'message':
                        'Model metadata could not be loaded.',

                    'status':
                        result.get('status'),
                })

                continue

            metadata = result.get(
                'metadata'
            ) or {}

            metrics = metadata.get(
                'evaluation_metrics'
            )

            if not isinstance(metrics, dict):
                metrics = {}

            
            if metrics:
                evaluation_data_status = 'metrics_recorded'
            else:
                evaluation_data_status = 'metrics_missing'

            evaluation_valid = metadata.get(
                'evaluation_valid'
            )

            evaluation_status = metadata.get(
                'evaluation_status'
            )

            if (
                evaluation_valid is True
                and evaluation_status == 'valid'
            ):
                evaluation_validity_status = 'valid'

            elif (
                evaluation_valid is False
                or (
                    evaluation_status is not None
                    and evaluation_status != 'valid'
                )
            ):
                evaluation_validity_status = 'invalid'

            else:
                evaluation_validity_status = 'unknown'


            record = {

                'source':
                    'file_registry',

                'target_name':
                    target_name,

                'target_task':
                    metadata.get(
                        'target_task'
                    ),

                'target_type':
                    metadata.get(
                        'target_type'
                    ),

                'model_type':
                    metadata.get(
                        'model_type'
                    ),

                'algorithm':
                    metadata.get(
                        'algorithm'
                    ),

                'version':
                    version,

                'is_active':
                    version == active_version,

                'active_version':
                    active_version,

                'trained_at':
                    metadata.get(
                        'trained_at'
                    ),

                'training_rows':
                    metadata.get(
                        'training_rows'
                    ),

                'test_rows':
                    metadata.get(
                        'test_rows'
                    ),

                'primary_metric':
                    metadata.get(
                        'primary_metric'
                    ),

                'metric_direction':
                    metadata.get(
                        'metric_direction'
                    ),

                'evaluation_metrics':
                    metrics,

                'evaluation_valid':
                    metadata.get(
                        'evaluation_valid'
                    ),

                'evaluation_status':
                    evaluation_status,

                'evaluation_validity_status':
                    evaluation_validity_status,

                'chronological_evaluation':
                    metadata.get(
                        'chronological_evaluation'
                    ),

                'chronological_boundary_valid':
                    metadata.get(
                        'chronological_boundary_valid'
                    ),

                'test_ratio':
                    metadata.get(
                        'test_ratio'
                    ),

                'min_test_rows':
                    metadata.get(
                        'min_test_rows'
                    ),

                'actual_test_rows':
                    metadata.get(
                        'actual_test_rows'
                    ),

                'training_date_start':
                    metadata.get(
                        'training_date_start'
                    ),

                'training_date_end':
                    metadata.get(
                        'training_date_end'
                    ),

                'testing_date_start':
                    metadata.get(
                        'testing_date_start'
                    ),

                'testing_date_end':
                    metadata.get(
                        'testing_date_end'
                    ),

                'training_class_count':
                    metadata.get(
                        'training_class_count'
                    ),

                'class_count':
                    metadata.get(
                        'class_count'
                    ),

                'training_classes':
                    metadata.get(
                        'training_classes'
                    ),

                'classes':
                    metadata.get(
                        'classes'
                    ),

                'classification_average':
                    metadata.get(
                        'classification_average'
                    ),

                'training_target_unique_count':
                    metadata.get(
                        'training_target_unique_count'
                    ),

                'training_target_has_variation':
                    metadata.get(
                        'training_target_has_variation'
                    ),

                'evaluation_data_status':
                    evaluation_data_status,

                'metadata_path':
                    result.get(
                        'path'
                    ),
            }

            records.append(record)

        except Exception as exc:

            errors.append({

                'target_name':
                    target_name,

                'version':
                    version,

                'message':
                    str(exc),
            })

    return records, errors


def _load_registry_evaluations():
    """
    Load all registered model versions.
    """

    try:

        targets = _get_registry_targets()

    except Exception as exc:

        return [], [{

            'source':
                'file_registry',

            'message':
                str(exc),
        }]

    all_records = []
    all_errors = []

    for target_name in targets:

        records, errors = _load_target_versions(
            target_name
        )

        all_records.extend(records)
        all_errors.extend(errors)

    return all_records, all_errors


# ==========================================================
# TARGET SUMMARIES
# ==========================================================

def _build_target_summaries(version_records):
    """
    Group registered model versions by target.
    """

    grouped = {}

    for record in version_records:

        target_name = record[
            'target_name'
        ]

        if target_name not in grouped:

            grouped[target_name] = {

                'target_name':
                    target_name,

                'target_task':
                    record.get(
                        'target_task'
                    ),

                'active_version':
                    record.get(
                        'active_version'
                    ),

                'versions':
                    [],

            }

        grouped[target_name][
            'versions'
        ].append(record)

    targets = []

    for target in grouped.values():

        versions = target[
            'versions'
        ]

        target['versions_count'] = len(
            versions
        )

        target['evaluated_versions_count'] = sum(
            1
            for version in versions
            if version[
                'evaluation_data_status'
            ] == 'metrics_recorded'
        )


        target['valid_evaluations_count'] = sum(
            1
            for version in versions
            if version.get(
                'evaluation_validity_status'
            ) == 'valid'
        )

        target['invalid_evaluations_count'] = sum(
            1
            for version in versions
            if version.get(
                'evaluation_validity_status'
            ) == 'invalid'
        )

        target['unknown_evaluations_count'] = sum(
            1
            for version in versions
            if version.get(
                'evaluation_validity_status'
            ) == 'unknown'
        )

        target['latest_version'] = (
            versions[-1]['version']
            if versions
            else None
        )

        targets.append(target)

    return sorted(
        targets,
        key=lambda item: item['target_name'],
    )


# ==========================================================
# OVERVIEW
# ==========================================================

def _build_overview(
    targets,
    version_records,
    legacy_records,
):
    """
    Build factual counts without assigning model quality.
    """

    total_versions = len(
        version_records
    )

    versions_with_evaluation = sum(
        1
        for record in version_records
        if record[
            'evaluation_data_status'
        ] == 'metrics_recorded'
    )

    versions_without_evaluation = (
        total_versions
        - versions_with_evaluation
    )

    active_versions = sum(
        1
        for record in version_records
        if record['is_active']
    )


    valid_evaluations = sum(
        1
        for record in version_records
        if record.get(
            'evaluation_validity_status'
        ) == 'valid'
    )

    invalid_evaluations = sum(
        1
        for record in version_records
        if record.get(
            'evaluation_validity_status'
        ) == 'invalid'
    )

    unknown_evaluations = sum(
        1
        for record in version_records
        if record.get(
            'evaluation_validity_status'
        ) == 'unknown'
    )

    valid_chronological_evaluations = sum(
        1
        for record in version_records
        if record.get(
            'chronological_boundary_valid'
        ) is True
    )

    invalid_chronological_evaluations = sum(
        1
        for record in version_records
        if record.get(
            'chronological_boundary_valid'
        ) is False
    )

    unknown_chronological_evaluations = sum(
        1
        for record in version_records
        if record.get(
            'chronological_boundary_valid'
        ) is None
    )


    return {


        'valid_evaluations':
            valid_evaluations,

        'invalid_evaluations':
            invalid_evaluations,

        'unknown_evaluations':
            unknown_evaluations,

        'valid_chronological_evaluations':
            valid_chronological_evaluations,

        'invalid_chronological_evaluations':
            invalid_chronological_evaluations,

        'unknown_chronological_evaluations':
            unknown_chronological_evaluations,


        'registered_targets':
            len(targets),

        'registered_versions':
            total_versions,

        'versions_with_evaluation':
            versions_with_evaluation,

        'versions_without_evaluation':
            versions_without_evaluation,

        'active_versions':
            active_versions,

        'legacy_history_records':
            len(legacy_records),
    }


# ==========================================================
# PUBLIC SERVICE
# ==========================================================

def load_evaluation_page_data():
    """
    Load all data required by the Evaluation page.

    Data sources:

        1. File Registry
        2. MariaDB model_history

    The two sources remain separate.
    """

    version_records, registry_errors = (
        _load_registry_evaluations()
    )

    legacy_records, database_error = (
        _load_legacy_model_history()
    )

    targets = _build_target_summaries(
        version_records
    )

    overview = _build_overview(
        targets,
        version_records,
        legacy_records,
    )

    errors = list(
        registry_errors
    )

    if database_error is not None:

        errors.append({

            'source':
                'model_history',

            'message':
                database_error,
        })

    return {

        'status':
            'partial' if errors else 'success',

        'overview':
            overview,

        'targets':
            targets,

        'versions':
            version_records,

        'legacy_history':
            legacy_records,

        'errors':
            errors,
    }
