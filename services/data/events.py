from database.queries import (
    get_all_events,
    get_event_by_id,
    add_event as query_add_event,
    update_event as query_update_event,
    delete_event as query_delete_event,
)


def get_events():
    return get_all_events()


def get_event(event_id):
    return get_event_by_id(event_id)


def add_event(date, time, event_type, description):
    query_add_event(
        date,
        time,
        event_type,
        description,
    )


def update_event(
    event_id,
    date,
    time,
    event_type,
    description,
):
    query_update_event(
        event_id,
        date,
        time,
        event_type,
        description,
    )


def delete_event(event_id):
    query_delete_event(event_id)

