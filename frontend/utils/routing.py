from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class PageDefinition:
    key: str
    label: str
    route: str
    icon: str


PAGES = (
    PageDefinition(
        key='dashboard',
        label='Dashboard',
        route='/',
        icon='dashboard',
    ),
    PageDefinition(
        key='expenses',
        label='Expenses',
        route='/expenses',
        icon='payments',
    ),
    PageDefinition(
        key='income',
        label='Income',
        route='/income',
        icon='account_balance',
    ),
    PageDefinition(
        key='budgets',
        label='Budgets',
        route='/budgets',
        icon='account_balance_wallet',
    ),
    PageDefinition(
        key='predictions',
        label='Predictions',
        route='/predictions',
        icon='auto_awesome',
    ),
    PageDefinition(
        key='analysis',
        label='Analysis',
        route='/analysis',
        icon='analytics',
    ),
    PageDefinition(
        key='reports',
        label='Reports',
        route='/reports',
        icon='description',
    ),
    PageDefinition(
        key='days',
        label='Days',
        route='/days',
        icon='calendar_today',
    ),
    PageDefinition(
        key='events',
        label='Events',
        route='/events',
        icon='event',
    ),
    PageDefinition(
        key='health',
        label='Health',
        route='/health',
        icon='favorite',
    ),
    PageDefinition(
        key='sleep',
        label='Sleep',
        route='/sleep',
        icon='bedtime',
    ),
    PageDefinition(
        key='settings',
        label='Settings',
        route='/settings',
        icon='settings',
    ),
)


PAGE_BY_KEY = {
    page.key: page
    for page in PAGES
}


PAGE_BY_ROUTE = {
    page.route: page
    for page in PAGES
}


def get_page(
    key: str,
) -> PageDefinition | None:
    return PAGE_BY_KEY.get(key)


def get_page_by_route(
    route: str,
) -> PageDefinition | None:
    return PAGE_BY_ROUTE.get(route)


def get_page_title(
    key: str,
) -> str:
    page = get_page(key)

    if page is None:
        return 'Personal Finance AI'

    return page.label