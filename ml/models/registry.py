
import json
import os
import re
from datetime import datetime, timezone


# ==========================================================
# REGISTRY STATUS
# ==========================================================

REGISTRY_VALID = 'valid'
REGISTRY_NOT_FOUND = 'not_found'
REGISTRY_INVALID = 'invalid'


# ==========================================================
# CONSTANTS
# ==========================================================

DEFAULT_REGISTRY_DIR = os.path.join(
    'ml',
    'models',
    'registry',
)

METADATA_FILENAME = 'metadata.json'

VERSION_PATTERN = re.compile(
    r'^v\d+\.\d+\.\d+$'
)


# ==========================================================
# BASIC HELPERS
# ==========================================================

def _validate_string(
    value,
    name,
):
    """
    Validate a required non-empty string.
    """

    if not isinstance(
        value,
        str,
    ):

        raise ValueError(
            f'{name} must be a string.'
        )

    if not value.strip():

        raise ValueError(
            f'{name} cannot be empty.'
        )

    return value.strip()


def _validate_version(
    version,
):
    """
    Validate semantic model version.

    Expected:

        v1.0.0
        v2.1.3
    """

    version = _validate_string(
        version,
        'version',
    )

    if not VERSION_PATTERN.match(
        version
    ):

        raise ValueError(
            'version must use the format '
            'vMAJOR.MINOR.PATCH.'
        )

    return version


def _utc_timestamp():
    """
    Return a timezone-aware UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


def _registry_path(
    registry_dir,
):
    """
    Normalize registry directory.
    """

    if registry_dir is None:

        registry_dir = (
            DEFAULT_REGISTRY_DIR
        )

    if not isinstance(
        registry_dir,
        str,
    ):

        raise ValueError(
            'registry_dir must be a string.'
        )

    if not registry_dir.strip():

        raise ValueError(
            'registry_dir cannot be empty.'
        )

    return os.path.abspath(
        registry_dir
    )


def _target_directory(
    registry_dir,
    target_name,
):
    """
    Return the directory used for a target.
    """

    target_name = _validate_string(
        target_name,
        'target_name',
    )

    return os.path.join(
        registry_dir,
        target_name,
    )


def _version_directory(
    registry_dir,
    target_name,
    version,
):
    """
    Return the directory used for one model version.
    """

    return os.path.join(
        _target_directory(
            registry_dir,
            target_name,
        ),
        _validate_version(
            version
        ),
    )


def _metadata_path(
    registry_dir,
    target_name,
    version,
):
    """
    Return metadata.json path.
    """

    return os.path.join(
        _version_directory(
            registry_dir,
            target_name,
            version,
        ),
        METADATA_FILENAME,
    )


# ==========================================================
# METADATA VALIDATION
# ==========================================================

def validate_model_metadata(
    metadata,
):
    """
    Validate model registry metadata.

    Required fields:

        target_name
        target_task
        target_type
        model_type
        algorithm
        feature_names
        version

    Optional fields are preserved.
    """

    if not isinstance(
        metadata,
        dict,
    ):

        raise ValueError(
            'metadata must be a dictionary.'
        )

    required_fields = [
        'target_name',
        'target_task',
        'target_type',
        'model_type',
        'algorithm',
        'feature_names',
        'version',
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in metadata
    ]

    if missing_fields:

        raise ValueError(
            'Model metadata is missing required fields: '
            f'{missing_fields}'
        )

    _validate_string(
        metadata['target_name'],
        'target_name',
    )

    _validate_string(
        metadata['target_task'],
        'target_task',
    )

    _validate_string(
        metadata['target_type'],
        'target_type',
    )

    _validate_string(
        metadata['model_type'],
        'model_type',
    )

    _validate_string(
        metadata['algorithm'],
        'algorithm',
    )

    _validate_version(
        metadata['version']
    )

    feature_names = metadata[
        'feature_names'
    ]

    if not isinstance(
        feature_names,
        list,
    ):

        raise ValueError(
            'feature_names must be a list.'
        )

    if not feature_names:

        raise ValueError(
            'feature_names cannot be empty.'
        )

    for feature_name in feature_names:

        _validate_string(
            feature_name,
            'feature_name',
        )

    return True


# ==========================================================
# SAVE METADATA
# ==========================================================

def save_model_metadata(
    metadata,
    registry_dir=None,
):
    """
    Save model metadata to the registry.

    Returns:

        metadata path
    """

    validate_model_metadata(
        metadata
    )

    registry_dir = _registry_path(
        registry_dir
    )

    target_name = metadata[
        'target_name'
    ]

    version = metadata[
        'version'
    ]

    target_dir = _target_directory(
        registry_dir,
        target_name,
    )

    version_dir = _version_directory(
        registry_dir,
        target_name,
        version,
    )

    os.makedirs(
        version_dir,
        exist_ok=True,
    )

    metadata_to_save = dict(
        metadata
    )

    if (
        'created_at'
        not in metadata_to_save
    ):

        metadata_to_save[
            'created_at'
        ] = _utc_timestamp()

    metadata_to_save[
        'registry_status'
    ] = REGISTRY_VALID

    path = _metadata_path(
        registry_dir,
        target_name,
        version,
    )

    with open(
        path,
        'w',
        encoding='utf-8',
    ) as file:

        json.dump(
            metadata_to_save,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return path


# ==========================================================
# LOAD METADATA
# ==========================================================

def load_model_metadata(
    target_name,
    version,
    registry_dir=None,
):
    """
    Load metadata for a specific model version.
    """

    registry_dir = _registry_path(
        registry_dir
    )

    target_name = _validate_string(
        target_name,
        'target_name',
    )

    version = _validate_version(
        version
    )

    path = _metadata_path(
        registry_dir,
        target_name,
        version,
    )

    if not os.path.isfile(
        path
    ):

        return {

            'status':
                REGISTRY_NOT_FOUND,

            'metadata':
                None,

            'path':
                path,
        }

    try:

        with open(
            path,
            'r',
            encoding='utf-8',
        ) as file:

            metadata = json.load(
                file
            )

    except (
        OSError,
        json.JSONDecodeError,
    ):

        return {

            'status':
                REGISTRY_INVALID,

            'metadata':
                None,

            'path':
                path,
        }

    try:

        validate_model_metadata(
            metadata
        )

    except ValueError:

        return {

            'status':
                REGISTRY_INVALID,

            'metadata':
                metadata,

            'path':
                path,
        }

    return {

        'status':
            REGISTRY_VALID,

        'metadata':
            metadata,

        'path':
            path,
    }


# ==========================================================
# LIST VERSIONS
# ==========================================================

def list_model_versions(
    target_name,
    registry_dir=None,
):
    """
    List registered versions for a target.

    Returns versions sorted in ascending semantic order.
    """

    registry_dir = _registry_path(
        registry_dir
    )

    target_dir = _target_directory(
        registry_dir,
        target_name,
    )

    if not os.path.isdir(
        target_dir
    ):

        return []

    versions = []

    for entry in os.listdir(
        target_dir
    ):

        entry_path = os.path.join(
            target_dir,
            entry,
        )

        if (
            os.path.isdir(entry_path)
            and VERSION_PATTERN.match(entry)
        ):

            versions.append(
                entry
            )

    def version_key(
        version,
    ):

        return tuple(
            int(part)
            for part in version[1:].split('.')
        )

    return sorted(
        versions,
        key=version_key,
    )


# ==========================================================
# LATEST VERSION
# ==========================================================

def get_latest_model_version(
    target_name,
    registry_dir=None,
):
    """
    Return the latest registered version.

    Returns None when no version exists.
    """

    versions = list_model_versions(
        target_name,
        registry_dir,
    )

    if not versions:

        return None

    return versions[-1]


# ==========================================================
# REGISTER MODEL
# ==========================================================

def register_model(
    metadata,
    registry_dir=None,
):
    """
    Register model metadata.

    The actual model object is intentionally not handled here.

    Model persistence is separated from metadata registration
    so that the registry remains simple and auditable.
    """

    validate_model_metadata(
        metadata
    )

    path = save_model_metadata(
        metadata,
        registry_dir,
    )

    return {

        'status':
            REGISTRY_VALID,

        'target_name':
            metadata['target_name'],

        'version':
            metadata['version'],

        'metadata_path':
            path,
    }


# ==========================================================
# REGISTRY CHECK
# ==========================================================

def is_model_registered(
    target_name,
    version,
    registry_dir=None,
):
    """
    Check whether a valid model metadata record exists.
    """

    result = load_model_metadata(
        target_name,
        version,
        registry_dir,
    )

    return (
        result['status']
        == REGISTRY_VALID
    )


# ==========================================================
# SIMPLE MANUAL TEST
# ==========================================================

if __name__ == '__main__':

    import tempfile

    temporary_directory = (
        tempfile.mkdtemp()
    )

    metadata = {

        'target_name':
            'Target_Expense_Total_1D',

        'target_task':
            'regression',

        'target_type':
            'numeric',

        'model_type':
            'regression',

        'algorithm':
            'RandomForestRegressor',

        'feature_names':
            [
                'feature_a',
                'feature_b',
            ],

        'version':
            'v1.0.0',
    }

    result = register_model(
        metadata,
        temporary_directory,
    )

    print()
    print(
        '========== MODEL REGISTRY TEST =========='
    )

    print(
        result
    )

    print(
        load_model_metadata(
            'Target_Expense_Total_1D',
            'v1.0.0',
            temporary_directory,
        )
    )

    print(
        list_model_versions(
            'Target_Expense_Total_1D',
            temporary_directory,
        )
    )

    print(
        get_latest_model_version(
            'Target_Expense_Total_1D',
            temporary_directory,
        )
    )

    print()
    print(
        '========== MODEL REGISTRY TEST PASSED =========='
    )