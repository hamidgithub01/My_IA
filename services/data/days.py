from database.queries import (
    get_all_days,
    get_day_by_date,
    add_day as query_add_day,
    update_day as query_update_day,
    delete_day as query_delete_day,
)


def get_days():
    return get_all_days()


def get_day(day_date):
    return get_day_by_date(day_date)


def add_day(
    date,
    day_type,
    work_status,
    health_impact,
    travel,
    special_event,
    stress_level,
    notes,
    sleep_hours,
    social_activity,
    location,
):
    query_add_day(
        date,
        day_type,
        work_status,
        health_impact,
        travel,
        special_event,
        stress_level,
        notes,
        sleep_hours,
        social_activity,
        location,
    )


def update_day(
    date,
    day_type,
    work_status,
    health_impact,
    travel,
    special_event,
    stress_level,
    notes,
    sleep_hours,
    social_activity,
    location,
):
    query_update_day(
        date,
        day_type,
        work_status,
        health_impact,
        travel,
        special_event,
        stress_level,
        notes,
        sleep_hours,
        social_activity,
        location,
    )


def delete_day(date):
    query_delete_day(date)

