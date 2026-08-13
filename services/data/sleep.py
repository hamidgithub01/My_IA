from database.queries import (
    get_all_sleep_records,
    get_sleep_record_by_id,
    get_sleep_records_by_date,
    add_sleep_record as query_add_sleep_record,
    update_sleep_record as query_update_sleep_record,
    delete_sleep_record as query_delete_sleep_record,
)


def get_sleep_records():
    return get_all_sleep_records()


def get_sleep_record(sleep_id):
    return get_sleep_record_by_id(sleep_id)


def get_sleep_records_date(date):
    return get_sleep_records_by_date(date)


def add_sleep_record(
    date,
    start_time,
    end_time,
    duration_minutes,
    sleep_type,
    continuity,
    location,
    position,
    awakenings,
    sleep_quality,
    noise_level,
    light_level,
    temperature_level,
    comfort_level,
    stress_before_sleep,
    caffeine_before_sleep,
    screen_before_sleep,
    before_sleep_activity,
    dreams,
    notes,
):
    return query_add_sleep_record(
        date,
        start_time,
        end_time,
        duration_minutes,
        sleep_type,
        continuity,
        location,
        position,
        awakenings,
        sleep_quality,
        noise_level,
        light_level,
        temperature_level,
        comfort_level,
        stress_before_sleep,
        caffeine_before_sleep,
        screen_before_sleep,
        before_sleep_activity,
        dreams,
        notes,
    )


def update_sleep_record(
    sleep_id,
    date,
    start_time,
    end_time,
    duration_minutes,
    sleep_type,
    continuity,
    location,
    position,
    awakenings,
    sleep_quality,
    noise_level,
    light_level,
    temperature_level,
    comfort_level,
    stress_before_sleep,
    caffeine_before_sleep,
    screen_before_sleep,
    before_sleep_activity,
    dreams,
    notes,
):
    return query_update_sleep_record(
        sleep_id,
        date,
        start_time,
        end_time,
        duration_minutes,
        sleep_type,
        continuity,
        location,
        position,
        awakenings,
        sleep_quality,
        noise_level,
        light_level,
        temperature_level,
        comfort_level,
        stress_before_sleep,
        caffeine_before_sleep,
        screen_before_sleep,
        before_sleep_activity,
        dreams,
        notes,
    )


def delete_sleep_record(sleep_id):
    return query_delete_sleep_record(sleep_id)