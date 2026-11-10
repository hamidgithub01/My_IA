from pathlib import Path

from nicegui import ui

from ml.models.registry import (
    REGISTRY_VALID,
    activate_registered_model,
    get_active_model_version,
    list_model_versions,
    load_model_metadata,
)

REGISTRY_ROOT = Path('ml') / 'models' / 'registry'


def _discover_targets():
    if not REGISTRY_ROOT.is_dir():
        return []
    return sorted(
        path.name for path in REGISTRY_ROOT.iterdir()
        if path.is_dir() and list_model_versions(path.name)
    )


def _metric_text(metadata):
    metrics = metadata.get('evaluation_metrics') or {}
    primary = metadata.get('primary_metric')
    if primary and primary in metrics:
        try:
            return f'{primary.upper()}: {float(metrics[primary]):,.4f}'
        except (TypeError, ValueError):
            return f'{primary.upper()}: {metrics[primary]}'
    if metrics:
        return ' | '.join(
            f'{key}: {value:.4f}' if isinstance(value, (int, float)) else f'{key}: {value}'
            for key, value in list(metrics.items())[:3]
        )
    return 'No evaluation metrics recorded'


def models_page():
    ui.label('Model Registry').classes('text-2xl font-bold')
    ui.label(
        'Browse registered model versions, inspect their metadata, and choose which version is active for predictions.'
    ).classes('text-sm text-gray-500')

    targets = _discover_targets()
    if not targets:
        ui.label('No registered model versions were found.').classes('text-orange-700')
        return

    target_options = {
        target: target.replace('Target_', '').replace('_', ' ')
        for target in targets
    }
    search = ui.input('Search targets').props('clearable').classes('w-full')
    target_select = ui.select(
        options=target_options,
        value=targets[0],
        label='Target',
    ).classes('w-full')

    summary = ui.row().classes('w-full flex-wrap gap-3')
    versions_container = ui.column().classes('w-full gap-3')
    notice = ui.label('').classes('text-sm')

    def render_versions():
        target = target_select.value
        versions_container.clear()
        notice.text = ''
        if not target:
            return
        versions = list_model_versions(target)
        active_version = get_active_model_version(target)
        with versions_container:
            ui.label(f'{len(versions)} registered version(s)').classes('text-sm text-gray-500')
            for version in reversed(versions):
                result = load_model_metadata(target, version)
                metadata = result.get('metadata') or {}
                valid = result.get('status') == REGISTRY_VALID
                is_active = version == active_version
                with ui.card().classes('w-full'):
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(version).classes('text-lg font-semibold')
                        if is_active:
                            ui.badge('ACTIVE', color='positive')
                        elif not valid:
                            ui.badge('INVALID', color='negative')
                        else:
                            ui.badge('SAVED', color='info')
                    ui.label(
                        f"Algorithm: {metadata.get('algorithm', 'Unknown')} · "
                        f"Task: {metadata.get('target_task', metadata.get('model_type', 'Unknown'))}"
                    ).classes('text-sm text-gray-600')
                    ui.label(_metric_text(metadata)).classes('text-sm')
                    ui.label(
                        f"Training rows: {metadata.get('training_rows', '—')} · "
                        f"Test rows: {metadata.get('test_rows', '—')}"
                    ).classes('text-xs text-gray-500')
                    ui.label(
                        f"Created: {metadata.get('created_at', 'Unknown')}"
                    ).classes('text-xs text-gray-500')
                    if valid and not is_active:
                        ui.button(
                            'Activate this version',
                            icon='check_circle',
                            on_click=lambda t=target, v=version: activate_version(t, v),
                        ).props('color=primary unelevated')
                    elif is_active:
                        ui.label('This version is currently used by default predictions.').classes('text-xs text-green-700')
                    else:
                        ui.label('This version cannot be activated because its registry entry is invalid.').classes('text-xs text-red-700')

    def activate_version(target, version):
        try:
            result = activate_registered_model(target, version)
            if result.get('status') == REGISTRY_VALID and result.get('active'):
                notice.text = f'{target}: {version} is now active.'
                ui.notify(notice.text, type='positive')
            else:
                notice.text = f'Activation failed: {result.get("status", "unknown status")}'
                ui.notify(notice.text, type='negative')
        except Exception as exc:
            notice.text = f'Activation failed: {exc}'
            ui.notify(notice.text, type='negative')
        render_versions()

    def filter_targets():
        query = (search.value or '').strip().lower()
        filtered = {
            target: label for target, label in target_options.items()
            if query in target.lower() or query in label.lower()
        }
        current = target_select.value
        target_select.options = filtered
        if current not in filtered:
            target_select.value = next(iter(filtered), None)
        target_select.update()
        render_versions()

    search.on('update:model-value', lambda _: filter_targets())
    target_select.on_value_change(lambda _: render_versions())
    render_versions()
