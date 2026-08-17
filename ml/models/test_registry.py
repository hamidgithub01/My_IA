
import json
import os


from ml.models.registry import (
    REGISTRY_VALID,
    REGISTRY_NOT_FOUND,
    REGISTRY_INVALID,
    validate_model_metadata,
    save_model_metadata,
    load_model_metadata,
    list_model_versions,
    get_latest_model_version,
    register_model,
    is_model_registered,
)


# ==========================================================
# TEST METADATA
# ==========================================================

def create_metadata(
    version='v1.0.0',
):
    return {

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
                'feature_c',
            ],

        'version':
            version,
    }


# ==========================================================
# VALIDATION TEST
# ==========================================================

def test_validate_metadata():

    metadata = create_metadata()

    assert (
        validate_model_metadata(
            metadata
        )
        is True
    )


# ==========================================================
# MISSING FIELD TEST
# ==========================================================

def test_missing_metadata_field():

    metadata = create_metadata()

    del metadata[
        'algorithm'
    ]

    try:

        validate_model_metadata(
            metadata
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# EMPTY FEATURES TEST
# ==========================================================

def test_empty_feature_names():

    metadata = create_metadata()

    metadata[
        'feature_names'
    ] = []

    try:

        validate_model_metadata(
            metadata
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# INVALID VERSION TEST
# ==========================================================

def test_invalid_version():

    metadata = create_metadata(
        'version-1'
    )

    try:

        validate_model_metadata(
            metadata
        )

        assert False

    except ValueError:

        pass


# ==========================================================
# SAVE / LOAD TEST
# ==========================================================

def test_save_and_load_metadata(
    tmp_path,
):

    metadata = create_metadata()

    path = save_model_metadata(
        metadata,
        str(tmp_path),
    )

    assert os.path.isfile(
        path
    )

    result = load_model_metadata(
        metadata[
            'target_name'
        ],
        metadata[
            'version'
        ],
        str(tmp_path),
    )

    assert (
        result['status']
        == REGISTRY_VALID
    )

    loaded = result[
        'metadata'
    ]

    assert (
        loaded['target_name']
        == metadata['target_name']
    )

    assert (
        loaded['version']
        == metadata['version']
    )

    assert (
        loaded['feature_names']
        == metadata['feature_names']
    )


# ==========================================================
# NOT FOUND TEST
# ==========================================================

def test_load_missing_model(
    tmp_path,
):

    result = load_model_metadata(
        'UnknownTarget',
        'v1.0.0',
        str(tmp_path),
    )

    assert (
        result['status']
        == REGISTRY_NOT_FOUND
    )

    assert (
        result['metadata']
        is None
    )


# ==========================================================
# INVALID METADATA FILE TEST
# ==========================================================

def test_invalid_metadata_file(
    tmp_path,
):

    target_name = (
        'Target_Expense_Total_1D'
    )

    version = 'v1.0.0'

    directory = (
        tmp_path
        / target_name
        / version
    )

    directory.mkdir(
        parents=True
    )

    metadata_path = (
        directory
        / 'metadata.json'
    )

    metadata_path.write_text(
        '{ invalid json',
        encoding='utf-8',
    )

    result = load_model_metadata(
        target_name,
        version,
        str(tmp_path),
    )

    assert (
        result['status']
        == REGISTRY_INVALID
    )


# ==========================================================
# VERSION LIST TEST
# ==========================================================

def test_list_versions(
    tmp_path,
):

    target = (
        'Target_Expense_Total_1D'
    )

    save_model_metadata(
        create_metadata('v1.0.0'),
        str(tmp_path),
    )

    save_model_metadata(
        create_metadata('v1.2.0'),
        str(tmp_path),
    )

    save_model_metadata(
        create_metadata('v1.1.0'),
        str(tmp_path),
    )

    versions = list_model_versions(
        target,
        str(tmp_path),
    )

    assert versions == [
        'v1.0.0',
        'v1.1.0',
        'v1.2.0',
    ]


# ==========================================================
# LATEST VERSION TEST
# ==========================================================

def test_latest_version(
    tmp_path,
):

    target = (
        'Target_Expense_Total_1D'
    )

    save_model_metadata(
        create_metadata('v1.0.0'),
        str(tmp_path),
    )

    save_model_metadata(
        create_metadata('v2.0.0'),
        str(tmp_path),
    )

    save_model_metadata(
        create_metadata('v1.9.9'),
        str(tmp_path),
    )

    latest = get_latest_model_version(
        target,
        str(tmp_path),
    )

    assert latest == 'v2.0.0'


# ==========================================================
# REGISTER MODEL TEST
# ==========================================================

def test_register_model(
    tmp_path,
):

    metadata = create_metadata()

    result = register_model(
        metadata,
        str(tmp_path),
    )

    assert (
        result['status']
        == REGISTRY_VALID
    )

    assert (
        result['target_name']
        == metadata['target_name']
    )

    assert (
        result['version']
        == metadata['version']
    )

    assert os.path.isfile(
        result['metadata_path']
    )


# ==========================================================
# REGISTRATION CHECK TEST
# ==========================================================

def test_is_model_registered(
    tmp_path,
):

    metadata = create_metadata()

    assert (
        is_model_registered(
            metadata['target_name'],
            metadata['version'],
            str(tmp_path),
        )
        is False
    )

    register_model(
        metadata,
        str(tmp_path),
    )

    assert (
        is_model_registered(
            metadata['target_name'],
            metadata['version'],
            str(tmp_path),
        )
        is True
    )


# ==========================================================
# VERSION SEPARATION TEST
# ==========================================================

def test_versions_are_separate(
    tmp_path,
):

    target = (
        'Target_Expense_Total_1D'
    )

    metadata_v1 = create_metadata(
        'v1.0.0'
    )

    metadata_v2 = create_metadata(
        'v2.0.0'
    )

    save_model_metadata(
        metadata_v1,
        str(tmp_path),
    )

    save_model_metadata(
        metadata_v2,
        str(tmp_path),
    )

    result_v1 = load_model_metadata(
        target,
        'v1.0.0',
        str(tmp_path),
    )

    result_v2 = load_model_metadata(
        target,
        'v2.0.0',
        str(tmp_path),
    )

    assert (
        result_v1['metadata']['version']
        == 'v1.0.0'
    )

    assert (
        result_v2['metadata']['version']
        == 'v2.0.0'
    )


# ==========================================================
# METADATA PERSISTENCE TEST
# ==========================================================

def test_metadata_persistence(
    tmp_path,
):

    metadata = create_metadata()

    path = save_model_metadata(
        metadata,
        str(tmp_path),
    )

    with open(
        path,
        'r',
        encoding='utf-8',
    ) as file:

        saved = json.load(
            file
        )

    assert (
        saved['registry_status']
        == REGISTRY_VALID
    )

    assert (
        saved['target_name']
        == metadata['target_name']
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == '__main__':

    print()
    print(
        '=================================================='
    )

    print(
        '          MODEL REGISTRY TEST SUITE'
    )

    print(
        '=================================================='
    )

    print(
        'Model registry tests are intended to be '
        'executed with pytest.'
    )

    print(
        '=================================================='
    )
