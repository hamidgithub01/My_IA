
from multiprocessing import freeze_support
from pathlib import Path

from nicegui import app, ui

from frontend.layout.shell import create_shell

from frontend.pages.dashboard import dashboard_page
from frontend.pages.predictions import predictions_page

from frontend.pages.data import data_page
from frontend.pages.features import features_page
from frontend.pages.targets import targets_page
from frontend.pages.training import training_page
from frontend.pages.models import models_page
from frontend.pages.evaluation import evaluation_page

from frontend.pages.monitoring import monitoring_page
from frontend.pages.patterns import patterns_page
from frontend.pages.alerts import alerts_page
from frontend.pages.recommendations import recommendations_page

from frontend.pages.analysis import analysis_page
from frontend.pages.reports import reports_page

from frontend.pages.expenses import expenses_page
from frontend.pages.income import income_page
from frontend.pages.budgets import budgets_page

from frontend.pages.days import days_page
from frontend.pages.events import events_page
from frontend.pages.health import health_page
from frontend.pages.sleep import sleep_page

from frontend.pages.settings import settings_page


# ==========================================================
# PATHS
# ==========================================================

FRONTEND_DIR = Path(__file__).resolve().parent
ASSETS_DIR = FRONTEND_DIR / 'assets'


# ==========================================================
# STATIC FILES
# ==========================================================

if ASSETS_DIR.exists():
    app.add_static_files(
        '/frontend/assets',
        str(ASSETS_DIR),
    )


# ==========================================================
# PAGE REGISTRY
# ==========================================================

def register_page(
    route: str,
    active_page: str,
    renderer,
):
    @ui.page(route)
    def page():
        content = create_shell(
            active_page=active_page,
        )

        with content:
            renderer()


# ==========================================================
# MAIN
# ==========================================================

register_page(
    route='/',
    active_page='dashboard',
    renderer=dashboard_page,
)


# ==========================================================
# FINANCE
# ==========================================================

register_page(
    route='/expenses',
    active_page='expenses',
    renderer=expenses_page,
)

register_page(
    route='/income',
    active_page='income',
    renderer=income_page,
)

register_page(
    route='/budgets',
    active_page='budgets',
    renderer=budgets_page,
)


# ==========================================================
# AI & PREDICTIONS
# ==========================================================

register_page(
    route='/predictions',
    active_page='predictions',
    renderer=predictions_page,
)

register_page(
    route='/analysis',
    active_page='analysis',
    renderer=analysis_page,
)

register_page(
    route='/reports',
    active_page='reports',
    renderer=reports_page,
)


# ==========================================================
# MACHINE LEARNING
# ==========================================================

register_page(
    route='/data',
    active_page='data',
    renderer=data_page,
)

register_page(
    route='/features',
    active_page='features',
    renderer=features_page,
)

register_page(
    route='/targets',
    active_page='targets',
    renderer=targets_page,
)

register_page(
    route='/training',
    active_page='training',
    renderer=training_page,
)

register_page(
    route='/models',
    active_page='models',
    renderer=models_page,
)

register_page(
    route='/evaluation',
    active_page='evaluation',
    renderer=evaluation_page,
)


# ==========================================================
# MONITORING
# ==========================================================

register_page(
    route='/monitoring',
    active_page='monitoring',
    renderer=monitoring_page,
)

register_page(
    route='/patterns',
    active_page='patterns',
    renderer=patterns_page,
)

register_page(
    route='/alerts',
    active_page='alerts',
    renderer=alerts_page,
)

register_page(
    route='/recommendations',
    active_page='recommendations',
    renderer=recommendations_page,
)


# ==========================================================
# LIFE & CONTEXT
# ==========================================================

register_page(
    route='/days',
    active_page='days',
    renderer=days_page,
)

register_page(
    route='/events',
    active_page='events',
    renderer=events_page,
)

register_page(
    route='/health',
    active_page='health',
    renderer=health_page,
)

register_page(
    route='/sleep',
    active_page='sleep',
    renderer=sleep_page,
)


# ==========================================================
# SETTINGS
# ==========================================================

register_page(
    route='/settings',
    active_page='settings',
    renderer=settings_page,
)


# ==========================================================
# APPLICATION
# ==========================================================

def main():
    ui.run(
        host='127.0.0.1',
        port=8090,
        title='Personal Finance AI',
        reload=False,
        show=False,
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ in {'__main__', '__mp_main__'}:
    freeze_support()
    main()