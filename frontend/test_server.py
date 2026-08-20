from nicegui import ui

print('STEP 1: Python started')

ui.label('Personal Finance AI - Server Test')

print('STEP 2: UI created')

ui.run(
    host='127.0.0.1',
    port=8090,
    reload=False,
    show=False,
)

print('STEP 3: ui.run returned')