
from database.queries import (
    get_all_income,
    get_income_by_id,
    add_income as query_add_income,
    update_income as query_update_income,
    delete_income as query_delete_income,
)


def get_income():
    return get_all_income()


def get_income_record(income_id):
    return get_income_by_id(income_id)


def add_income(
    date,
    time,
    source,
    description,
    amount,
    income_type,
):
    return query_add_income(
        date,
        time,
        source,
        description,
        amount,
        income_type,
    )


def update_income(
    income_id,
    date,
    time,
    source,
    description,
    amount,
    income_type,
):
    return query_update_income(
        income_id,
        date,
        time,
        source,
        description,
        amount,
        income_type,
    )


def delete_income(income_id):
    return query_delete_income(income_id)
