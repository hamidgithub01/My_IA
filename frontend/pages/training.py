from threading import Thread, Lock

from nicegui import ui

from frontend.services.training_service import train_all_targets


STATUS_LABELS = {
    'activated': 'Activated',
    'saved_not_activated': 'Saved · not activated',
    'rejected': 'Rejected',
    'insufficient_data': 'Insufficient data',
    'failed': 'Failed',
}


def training_page():
    state = {
        'running': False,
        'done': False,
        'report': None,
        'error': None,
        'progress': 0,
        'total': 0,
        'completed': 0,
        'last_target': '',
        'lock': Lock(),
    }

    with ui.column().classes('w-full min-w-0 gap-6'):
        with ui.row().classes('w-full items-center justify-between flex-wrap'):
            with ui.column().classes('gap-1'):
                ui.label('Training Center').classes('text-2xl font-bold text-primary-app')
                ui.label('Train and evaluate all registered models using the data recorded in this application.').classes('text-sm text-secondary-app')
            status_badge = ui.badge('Ready', color='grey')

        with ui.card().classes('w-full p-5'):
            with ui.row().classes('w-full items-center justify-between flex-wrap'):
                with ui.column().classes('gap-1'):
                    ui.label('Manual model training').classes('text-lg font-semibold')
                    ui.label('Training starts only when you press the button. Each target is processed independently.').classes('text-sm text-secondary-app')
                train_button = ui.button('Train all models', icon='model_training').props('unelevated no-caps color=primary')
            progress = ui.linear_progress(value=0).classes('w-full mt-4')
            progress_label = ui.label('Not started').classes('text-sm text-secondary-app')
            ui.label('A model is activated only when evaluation is valid and the comparison policy permits it. Existing active models are preserved when a candidate cannot be safely compared.').classes('text-xs text-secondary-app mt-2')

        summary = ui.element('div').classes('grid grid-cols-2 md:grid-cols-5 gap-3 w-full')
        with summary:
            summary_cards = {}
            for key, label in (
                ('activated', 'Activated'),
                ('saved_not_activated', 'Saved only'),
                ('rejected', 'Rejected'),
                ('insufficient_data', 'Insufficient data'),
                ('failed', 'Failed'),
            ):
                with ui.card().classes('p-3'):
                    summary_cards[key] = ui.label('—').classes('text-2xl font-bold')
                    ui.label(label).classes('text-xs text-secondary-app')

        ui.label('Target results').classes('text-lg font-semibold')
        results_table = ui.table(
            columns=[
                {'name': 'target_name', 'label': 'Target', 'field': 'target_name', 'align': 'left'},
                {'name': 'status', 'label': 'Result', 'field': 'status'},
                {'name': 'rows', 'label': 'Train / test', 'field': 'rows'},
                {'name': 'metric', 'label': 'Primary metric', 'field': 'metric'},
                {'name': 'version', 'label': 'Candidate version', 'field': 'version'},
                {'name': 'reason', 'label': 'Details', 'field': 'reason', 'align': 'left'},
            ],
            rows=[],
            row_key='target_name',
        ).classes('w-full')
        results_table.props(' dense flat bordered wrap-cells')

    def render_report(report):
        rows = []
        for item in report['results']:
            metrics = item.get('metrics') or {}
            metric_name = item.get('primary_metric')
            metric_value = metrics.get(metric_name) if metric_name else None
            rows.append({
                'target_name': item.get('target_name'),
                'status': STATUS_LABELS.get(item.get('status'), item.get('status', '—')),
                'rows': f"{item.get('training_rows', '—')} / {item.get('test_rows', '—')}",
                'metric': f'{metric_name}: {metric_value:.4f}' if isinstance(metric_value, (int, float)) else '—',
                'version': item.get('candidate_model_version') or '—',
                'reason': item.get('reason') or '',
            })
        results_table.rows = rows
        results_table.update()
        for key, label in report.get('summary', {}).items():
            summary_cards[key].set_text(str(label))
        progress.value = 1
        progress_label.set_text(f"Completed {report['completed']} / {report['total']} targets")
        status_badge.set_text('Completed')
        status_badge.props('color=positive')
        train_button.enable()

    def start_training():
        if state['running']:
            return
        state['running'] = True
        state['done'] = False
        state['report'] = None
        state['error'] = None
        train_button.disable()
        status_badge.set_text('Training')
        status_badge.props('color=warning')
        progress.value = 0
        progress_label.set_text('Preparing target list…')
        results_table.rows = []
        results_table.update()
        for card in summary_cards.values():
            card.set_text('—')

        def worker():
            try:
                def on_progress(done, total, result):
                    with state['lock']:
                        state['progress'] = done / total if total else 1
                        state['total'] = total
                        state['completed'] = done
                        state['last_target'] = result.get('target_name', '')
                report = train_all_targets(progress_callback=on_progress)
                with state['lock']:
                    state['report'] = report
            except Exception as exc:
                with state['lock']:
                    state['error'] = f'{type(exc).__name__}: {exc}'
            finally:
                with state['lock']:
                    state['done'] = True

        Thread(target=worker, daemon=True).start()

    def poll_worker():
        if not state['running']:
            return
        with state['lock']:
            done = state['done']
            report = state['report']
            error = state['error']
        if not done:
            with state['lock']:
                current_progress = state['progress']
                completed = state['completed']
                total = state['total']
                last_target = state['last_target']
            progress.value = current_progress
            if last_target:
                progress_label.set_text(f'Processed {completed} / {total} targets · Last: {last_target}')
            return
        state['running'] = False
        if error:
            status_badge.set_text('Failed')
            status_badge.props('color=negative')
            progress_label.set_text(error)
            train_button.enable()
            return
        render_report(report)

    train_button.on_click(start_training)
    ui.timer(1.0, poll_worker)
