from database.queries import (
    get_all_health_records,
    get_health_record_by_id,
    get_health_record_by_date,
    add_health_record as query_add_health_record,
    update_health_record as query_update_health_record,
    delete_health_record as query_delete_health_record,
)


def get_health_records():
    return get_all_health_records()


def get_health_record(health_id):
    return get_health_record_by_id(health_id)


def get_health_record_date(date):
    return get_health_record_by_date(date)


def add_health_record(
    date,
    health_status,
    energy_level,
    symptoms,
    severity,
    treatment,
    notes,
):
    return query_add_health_record(
        date,
        health_status,
        energy_level,
        symptoms,
        severity,
        treatment,
        notes,
    )


def update_health_record(
    health_id,
    date,
    health_status,
    energy_level,
    symptoms,
    severity,
    treatment,
    notes,
):
    return query_update_health_record(
        health_id,
        date,
        health_status,
        energy_level,
        symptoms,
        severity,
        treatment,
        notes,
    )


def delete_health_record(health_id):
    return query_delete_health_record(health_id)