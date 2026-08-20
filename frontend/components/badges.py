from nicegui import ui


# ==========================================================
# GENERIC BADGE
# ==========================================================

def badge(
    label,
    variant='neutral',
    icon=None,
):
    """
    Generic application badge.

    Variants:
        neutral
        success
        warning
        danger
        info
        primary
    """

    variants = {
        'neutral': {
            'classes': 'bg-gray-100 text-gray-600',
        },
        'success': {
            'classes': 'bg-green-50 text-green-700',
        },
        'warning': {
            'classes': 'bg-amber-50 text-amber-700',
        },
        'danger': {
            'classes': 'bg-red-50 text-red-700',
        },
        'info': {
            'classes': 'bg-sky-50 text-sky-700',
        },
        'primary': {
            'classes': 'bg-indigo-50 text-indigo-700',
        },
    }

    config = variants.get(
        str(variant).lower(),
        variants['neutral'],
    )

    with ui.row().classes(
        'inline-flex '
        'items-center '
        'gap-1.5 '
        'px-2.5 '
        'py-1 '
        'rounded-full '
        'text-xs '
        'font-medium '
        'whitespace-nowrap '
        + config['classes']
    ):

        if icon:

            ui.icon(
                icon
            ).classes(
                'text-sm'
            )

        ui.label(
            str(label)
        ).classes(
            'text-xs '
            'font-medium'
        )


# ==========================================================
# STATUS BADGE
# ==========================================================

def status_badge(
    label,
    status='neutral',
):

    status_config = {
        'neutral': {
            'variant': 'neutral',
            'dot': 'status-dot-neutral',
        },
        'success': {
            'variant': 'success',
            'dot': 'status-dot-success',
        },
        'warning': {
            'variant': 'warning',
            'dot': 'status-dot-warning',
        },
        'danger': {
            'variant': 'danger',
            'dot': 'status-dot-danger',
        },
        'info': {
            'variant': 'info',
            'dot': 'status-dot-info',
        },
    }

    config = status_config.get(
        str(status).lower(),
        status_config['neutral'],
    )

    with ui.row().classes(
        'inline-flex '
        'items-center '
        'gap-2 '
        'px-2.5 '
        'py-1 '
        'rounded-full '
        'text-xs '
        'font-medium '
        f"{_variant_classes(config['variant'])}"
    ):

        ui.element('span').classes(
            'status-dot '
            f"{config['dot']}"
        )

        ui.label(
            label
        ).classes(
            'text-xs '
            'font-medium'
        )


# ==========================================================
# TREND BADGE
# ==========================================================

def trend_badge(
    value,
    direction='neutral',
):

    config = {
        'up': {
            'icon': 'trending_up',
            'variant': 'success',
        },
        'down': {
            'icon': 'trending_down',
            'variant': 'danger',
        },
        'neutral': {
            'icon': 'trending_flat',
            'variant': 'neutral',
        },
    }

    selected = config.get(
        str(direction).lower(),
        config['neutral'],
    )

    badge(
        label=value,
        variant=selected['variant'],
        icon=selected['icon'],
    )


# ==========================================================
# PRIORITY BADGE
# ==========================================================

def priority_badge(
    priority,
):

    config = {
        'low': {
            'label': 'Low',
            'variant': 'info',
        },
        'medium': {
            'label': 'Medium',
            'variant': 'warning',
        },
        'high': {
            'label': 'High',
            'variant': 'danger',
        },
        'critical': {
            'label': 'Critical',
            'variant': 'danger',
        },
    }

    selected = config.get(
        str(priority).lower(),
        {
            'label': str(priority),
            'variant': 'neutral',
        },
    )

    badge(
        label=selected['label'],
        variant=selected['variant'],
    )


# ==========================================================
# AI STATUS BADGE
# ==========================================================

def ai_status_badge(
    status,
):

    config = {
        'available': {
            'label': 'Available',
            'variant': 'success',
        },
        'processing': {
            'label': 'Processing',
            'variant': 'info',
        },
        'reliable': {
            'label': 'Reliable',
            'variant': 'success',
        },
        'monitoring': {
            'label': 'Monitoring',
            'variant': 'info',
        },
        'pending': {
            'label': 'Pending',
            'variant': 'warning',
        },
        'unavailable': {
            'label': 'Unavailable',
            'variant': 'danger',
        },
    }

    selected = config.get(
        str(status).lower(),
        {
            'label': str(status),
            'variant': 'neutral',
        },
    )

    badge(
        label=selected['label'],
        variant=selected['variant'],
    )


# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _variant_classes(variant):

    classes = {
        'neutral': 'bg-gray-100 text-gray-600',
        'success': 'bg-green-50 text-green-700',
        'warning': 'bg-amber-50 text-amber-700',
        'danger': 'bg-red-50 text-red-700',
        'info': 'bg-sky-50 text-sky-700',
        'primary': 'bg-indigo-50 text-indigo-700',
    }

    return classes.get(
        str(variant).lower(),
        classes['neutral'],
    )