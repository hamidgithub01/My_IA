
import joblib
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
MODEL_FILENAME = 'model.joblib'
ACTIVE_FILENAME = 'active.json'

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


def _model_path(
    registry_dir,
    target_name,
    version,
):
    """
    Return the persisted model file path.
    """

    return os.path.join(
        _version_directory(
            registry_dir,
            target_name,
            version,
        ),
        MODEL_FILENAME,
    )


def _active_path(
    registry_dir,
    target_name,
):
    """
    Return active.json path for a target.
    """

    return os.path.join(
        _target_directory(
            registry_dir,
            target_name,
        ),
        ACTIVE_FILENAME,
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
# REGISTER MODEL METADATA
# ==========================================================

def register_model(
    metadata,
    registry_dir=None,
):
    """
    Register model metadata.
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
# SAVE REGISTERED MODEL
# ==========================================================

def save_registered_model(
    model,
    metadata,
    registry_dir=None,
):
    """
    Save a trained model together with its registry metadata.

    The model is persisted as:

        model.joblib

    and metadata as:

        metadata.json
    """

    if model is None:

        raise ValueError(
            'model is required.'
        )

    if not hasattr(
        model,
        'predict',
    ):

        raise ValueError(
            'model must provide a callable predict() method.'
        )

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

    version_dir = _version_directory(
        registry_dir,
        target_name,
        version,
    )

    os.makedirs(
        version_dir,
        exist_ok=True,
    )

    model_path = _model_path(
        registry_dir,
        target_name,
        version,
    )

    metadata_path = save_model_metadata(
        metadata,
        registry_dir,
    )

    try:

        joblib.dump(
            model,
            model_path,
        )

    except Exception as exc:

        raise ValueError(
            'Failed to persist model.'
        ) from exc

    return {

        'status':
            REGISTRY_VALID,

        'target_name':
            target_name,

        'version':
            version,

        'model_path':
            model_path,

        'metadata_path':
            metadata_path,
    }


# ==========================================================
# LOAD REGISTERED MODEL
# ==========================================================

def load_registered_model(
    target_name,
    version,
    registry_dir=None,
):
    """
    Load a registered model together with its metadata.
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

    metadata_result = load_model_metadata(
        target_name,
        version,
        registry_dir,
    )

    if (
        metadata_result['status']
        != REGISTRY_VALID
    ):

        return {

            'status':
                metadata_result['status'],

            'model':
                None,

            'metadata':
                metadata_result.get(
                    'metadata'
                ),

            'model_path':
                None,

            'metadata_path':
                metadata_result.get(
                    'path'
                ),
        }

    model_path = _model_path(
        registry_dir,
        target_name,
        version,
    )

    if not os.path.isfile(
        model_path
    ):

        return {

            'status':
                REGISTRY_NOT_FOUND,

            'model':
                None,

            'metadata':
                metadata_result[
                    'metadata'
                ],

            'model_path':
                model_path,

            'metadata_path':
                metadata_result[
                    'path'
                ],
        }

    try:

        model = joblib.load(
            model_path
        )

    except Exception as exc:

        return {

            'status':
                REGISTRY_INVALID,

            'model':
                None,

            'metadata':
                metadata_result[
                    'metadata'
                ],

            'model_path':
                model_path,

            'metadata_path':
                metadata_result[
                    'path'
                ],

            'error':
                str(exc),
        }

    if not hasattr(
        model,
        'predict',
    ):

        return {

            'status':
                REGISTRY_INVALID,

            'model':
                None,

            'metadata':
                metadata_result[
                    'metadata'
                ],

            'model_path':
                model_path,

            'metadata_path':
                metadata_result[
                    'path'
                ],

            'error':
                'Registered model does not provide '
                'a predict() method.',
        }

    return {

        'status':
            REGISTRY_VALID,

        'model':
            model,

        'metadata':
            metadata_result[
                'metadata'
            ],

        'model_path':
            model_path,

        'metadata_path':
            metadata_result[
                'path'
            ],
    }


# ==========================================================
# ACTIVE MODEL
# ==========================================================

def activate_registered_model(
    target_name,
    version,
    registry_dir=None,
):
    """
    Mark a registered model version as the active model.

    IMPORTANT:

        The model must already exist and be valid.

        Activation does not train or modify the model.

        It only changes which registered version is considered
        active for production inference.
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

    loaded = load_registered_model(
        target_name,
        version,
        registry_dir,
    )

    if (
        loaded['status']
        != REGISTRY_VALID
    ):

        return {

            'status':
                loaded['status'],

            'target_name':
                target_name,

            'version':
                version,

            'active':
                False,

            'path':
                _active_path(
                    registry_dir,
                    target_name,
                ),
        }

    target_dir = _target_directory(
        registry_dir,
        target_name,
    )

    os.makedirs(
        target_dir,
        exist_ok=True,
    )

    active_data = {

        'target_name':
            target_name,

        'active_version':
            version,

        'activated_at':
            _utc_timestamp(),

        'status':
            REGISTRY_VALID,
    }

    path = _active_path(
        registry_dir,
        target_name,
    )

    temporary_path = (
        path
        + '.tmp'
    )

    try:

        with open(
            temporary_path,
            'w',
            encoding='utf-8',
        ) as file:

            json.dump(
                active_data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        os.replace(
            temporary_path,
            path,
        )

    except OSError as exc:

        if os.path.isfile(
            temporary_path
        ):

            try:

                os.remove(
                    temporary_path
                )

            except OSError:

                pass

        raise ValueError(
            'Failed to activate registered model.'
        ) from exc

    return {

        'status':
            REGISTRY_VALID,

        'target_name':
            target_name,

        'version':
            version,

        'active':
            True,

        'active_path':
            path,

        'activated_at':
            active_data[
                'activated_at'
            ],
    }


# ==========================================================
# GET ACTIVE MODEL VERSION
# ==========================================================

def get_active_model_version(
    target_name,
    registry_dir=None,
):
    """
    Return the currently active model version.

    Returns None when no active model exists.
    """

    registry_dir = _registry_path(
        registry_dir
    )

    target_name = _validate_string(
        target_name,
        'target_name',
    )

    path = _active_path(
        registry_dir,
        target_name,
    )

    if not os.path.isfile(
        path
    ):

        return None

    try:

        with open(
            path,
            'r',
            encoding='utf-8',
        ) as file:

            active_data = json.load(
                file
            )

    except (
        OSError,
        json.JSONDecodeError,
    ):

        return None

    if not isinstance(
        active_data,
        dict,
    ):

        return None

    active_version = active_data.get(
        'active_version'
    )

    if active_version is None:

        return None

    try:

        return _validate_version(
            active_version
        )

    except ValueError:

        return None


# ==========================================================
# LOAD ACTIVE MODEL
# ==========================================================

def load_active_model(
    target_name,
    registry_dir=None,
):
    """
    Load the currently active model.

    This function intentionally does NOT load the latest
    registered version.

    It loads only the version explicitly marked active.
    """

    registry_dir = _registry_path(
        registry_dir
    )

    target_name = _validate_string(
        target_name,
        'target_name',
    )

    active_version = get_active_model_version(
        target_name,
        registry_dir,
    )

    if active_version is None:

        return {

            'status':
                REGISTRY_NOT_FOUND,

            'model':
                None,

            'metadata':
                None,

            'version':
                None,

            'model_path':
                None,

            'metadata_path':
                None,
        }

    result = load_registered_model(
        target_name,
        active_version,
        registry_dir,
    )

    result[
        'version'
    ] = active_version

    return result


# ==========================================================
# REGISTRY CHECK
# ==========================================================

def is_model_registered(
    target_name,
    version,
    registry_dir=None,
):
    """
    Check whether a valid model exists in the registry.
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
# MANUAL TEST
# ==========================================================

if __name__ == '__main__':

    from sklearn.linear_model import LinearRegression
    import tempfile

    print()
    print(
        '=================================================='
    )

    print(
        '       MODEL REGISTRY ACTIVE MODEL TEST'
    )

    print(
        '=================================================='
    )

    temporary_directory = (
        tempfile.mkdtemp()
    )

    target_name = (
        'Target_Expense_Total_1D'
    )

    feature_names = [
        'feature_a',
        'feature_b',
    ]

    # ======================================================
    # MODEL 1
    # ======================================================

    model_1 = LinearRegression()

    model_1.fit(
        [
            [1.0, 2.0],
            [2.0, 3.0],
            [3.0, 4.0],
        ],
        [
            3.0,
            5.0,
            7.0,
        ],
    )

    metadata_1 = {

        'target_name':
            target_name,

        'target_task':
            'regression',

        'target_type':
            'numeric',

        'model_type':
            'regression',

        'algorithm':
            'LinearRegression',

        'feature_names':
            feature_names,

        'version':
            'v1.0.0',
    }

    result_1 = save_registered_model(
        model_1,
        metadata_1,
        temporary_directory,
    )

    print()
    print(
        '========== SAVE V1 =========='
    )

    print(
        result_1
    )

    assert result_1[
        'status'
    ] == REGISTRY_VALID

    # ======================================================
    # ACTIVATE V1
    # ======================================================

    activation_1 = activate_registered_model(
        target_name,
        'v1.0.0',
        temporary_directory,
    )

    print()
    print(
        '========== ACTIVATE V1 =========='
    )

    print(
        activation_1
    )

    assert activation_1[
        'active'
    ] is True

    assert get_active_model_version(
        target_name,
        temporary_directory,
    ) == 'v1.0.0'

    # ======================================================
    # MODEL 2
    # ======================================================

    model_2 = LinearRegression()

    model_2.fit(
        [
            [1.0, 2.0],
            [2.0, 3.0],
            [3.0, 4.0],
        ],
        [
            4.0,
            6.0,
            8.0,
        ],
    )

    metadata_2 = {

        'target_name':
            target_name,

        'target_task':
            'regression',

        'target_type':
            'numeric',

        'model_type':
            'regression',

        'algorithm':
            'LinearRegression',

        'feature_names':
            feature_names,

        'version':
            'v2.0.0',
    }

    result_2 = save_registered_model(
        model_2,
        metadata_2,
        temporary_directory,
    )

    print()
    print(
        '========== SAVE V2 =========='
    )

    print(
        result_2
    )

    assert result_2[
        'status'
    ] == REGISTRY_VALID

    # ======================================================
    # LATEST VS ACTIVE
    # ======================================================

    latest_version = get_latest_model_version(
        target_name,
        temporary_directory,
    )

    active_version = get_active_model_version(
        target_name,
        temporary_directory,
    )

    print()
    print(
        '========== LATEST VS ACTIVE =========='
    )

    print(
        'Latest version:',
        latest_version
    )

    print(
        'Active version:',
        active_version
    )

    assert latest_version == 'v2.0.0'

    assert active_version == 'v1.0.0'

    # ======================================================
    # LOAD ACTIVE
    # ======================================================

    active_result = load_active_model(
        target_name,
        temporary_directory,
    )

    print()
    print(
        '========== LOAD ACTIVE MODEL =========='
    )

    print(
        'Status:',
        active_result[
            'status'
        ]
    )

    print(
        'Version:',
        active_result[
            'version'
        ]
    )

    assert active_result[
        'status'
    ] == REGISTRY_VALID

    assert active_result[
        'version'
    ] == 'v1.0.0'

    assert active_result[
        'model'
    ] is not None

    # ======================================================
    # ACTIVATE V2
    # ======================================================

    activation_2 = activate_registered_model(
        target_name,
        'v2.0.0',
        temporary_directory,
    )

    print()
    print(
        '========== ACTIVATE V2 =========='
    )

    print(
        activation_2
    )

    assert activation_2[
        'active'
    ] is True

    assert get_active_model_version(
        target_name,
        temporary_directory,
    ) == 'v2.0.0'

    # ======================================================
    # LOAD ACTIVE V2
    # ======================================================

    active_result_2 = load_active_model(
        target_name,
        temporary_directory,
    )

    print()
    print(
        '========== VERIFY ACTIVE V2 =========='
    )

    print(
        'Status:',
        active_result_2[
            'status'
        ]
    )

    print(
        'Version:',
        active_result_2[
            'version'
        ]
    )

    assert active_result_2[
        'status'
    ] == REGISTRY_VALID

    assert active_result_2[
        'version'
    ] == 'v2.0.0'

    # ======================================================
    # VERSION LIST
    # ======================================================

    versions = list_model_versions(
        target_name,
        temporary_directory,
    )

    print()
    print(
        '========== REGISTERED VERSIONS =========='
    )

    print(
        versions
    )

    assert versions == [
        'v1.0.0',
        'v2.0.0',
    ]

    # ======================================================
    # SUCCESS
    # ======================================================

    print()
    print(
        '=================================================='
    )

    print(
        '     MODEL REGISTRY ACTIVE MODEL TEST PASSED'
    )

    print(
        '=================================================='
    )
