
from database.queries import (
    get_all_expenses,
    get_expense_by_id,
    add_expense as query_add_expense,
    update_expense as query_update_expense,
    delete_expense as query_delete_expense,
)


def get_expenses():
    return get_all_expenses()


def get_expense(expense_id):
    return get_expense_by_id(expense_id)


def add_expense(
    date,
    time,
    category,
    description,
    amount,
):
    return query_add_expense(
        date,
        time,
        category,
        description,
        amount,
    )


def update_expense(
    expense_id,
    date,
    time,
    category,
    description,
    amount,
):
    return query_update_expense(
        expense_id,
        date,
        time,
        category,
        description,
        amount,
    )


def delete_expense(expense_id):
    return query_delete_expense(expense_id)