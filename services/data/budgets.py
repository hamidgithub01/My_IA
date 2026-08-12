from database.queries import (
    get_all_budgets,
    get_budget as query_get_budget,
    add_budget as query_add_budget,
    update_budget as query_update_budget,
    delete_budget as query_delete_budget,
)


def get_budgets():
    return get_all_budgets()


def get_budget(month, category):
    return query_get_budget(month, category)


def add_budget(month, category, budget_limit, notes):
    query_add_budget(
        month,
        category,
        budget_limit,
        notes,
    )


def update_budget(month, category, budget_limit, notes):
    query_update_budget(
        month,
        category,
        budget_limit,
        notes,
    )


def delete_budget(month, category):
    query_delete_budget(
        month,
        category,
    )