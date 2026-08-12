from database.queries import (
    get_all_settings,
    get_setting,
    add_setting as query_add_setting,
    update_setting as query_update_setting,
    delete_setting as query_delete_setting,
)


def get_settings():
    return get_all_settings()


def get_setting_value(setting):
    record = get_setting(setting)

    if not record:
        return None

    return record['Value']


def add_setting(setting, value):
    query_add_setting(
        setting,
        value,
    )


def update_setting(setting, value):
    query_update_setting(
        setting,
        value,
    )


def delete_setting(setting):
    query_delete_setting(setting)