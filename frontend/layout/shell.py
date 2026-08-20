from nicegui import ui

from frontend.layout.header import create_header
from frontend.layout.sidebar import create_sidebar


# ==========================================================
# APPLICATION SHELL
# ==========================================================

def create_shell(active_page='dashboard'):
    """
    Create the persistent application shell.

    Structure:
        Header
        Sidebar
        Main content
    """

    create_header(
        active_page=active_page,
    )

    create_sidebar(
        active_page=active_page,
    )

    # ======================================================
    # MAIN APPLICATION AREA
    # ======================================================

    with ui.column().classes(
        'w-full '
        'min-h-screen '
        'min-w-0 '
        'gap-0 '
        'bg-[var(--app-background)]'
    ):

        # --------------------------------------------------
        # CONTENT
        # --------------------------------------------------

        content = ui.column().classes(
            'w-full '
            'flex-1 '
            'min-w-0 '
            'p-4 '
            'md:p-6 '
            'lg:p-8 '
            'gap-6 '
            'max-w-screen-2xl '
            'mx-auto'
        )

    return content