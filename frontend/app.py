from multiprocessing import freeze_support
from pathlib import Path

from nicegui import app, ui

from frontend.layout.shell import create_shell
from frontend.pages.dashboard import dashboard_page
from frontend.pages.predictions import predictions_page

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
# PAGES
# ==========================================================

register_page(
    route='/',
    active_page='dashboard',
    renderer=dashboard_page,
)

register_page(
    route='/predictions',
    active_page='predictions',
    renderer=predictions_page,
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