from ml.targets.behavioral import (
    create_behavioral_targets,
)

from ml.targets.financial import (
    create_financial_targets,
)

from ml.targets.events import (
    create_event_targets,
)

from ml.targets.health import (
    create_health_targets,
)

from ml.targets.location import (
    create_location_targets,
)


print()
print('========== SYNTHETIC TARGET INTEGRATION TEST ==========')
print()


# =========================================================
# SYNTHETIC HISTORICAL DATA
# =========================================================

previous_rows = [
    {
        'Stress_Level': 3,
        'Sleep_Hours': 8,
        'Social_Activity': 'low',
        'Work_Status': 'off',

        'Expense_Total': 100,
        'Income_Total': 0,

        'Event_Count': 1,
        'Special_Event': '',

        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 8,

        'Location': 'Casablanca',
    },

    {
        'Stress_Level': 4,
        'Sleep_Hours': 7,
        'Social_Activity': 'medium',
        'Work_Status': 'working',

        'Expense_Total': 100,
        'Income_Total': 500,

        'Event_Count': 0,
        'Special_Event': '',

        'Health_Problem': 'no',
        'Health_Severity': 3,
        'Energy_Level': 7,

        'Location': 'Casablanca',
    },
]


# =========================================================
# SYNTHETIC FUTURE DATA
# =========================================================

future_rows = [
    {
        'Stress_Level': 7,
        'Sleep_Hours': 4.5,
        'Social_Activity': 'high',
        'Work_Status': 'working',

        'Expense_Total': 200,
        'Income_Total': 0,

        'Event_Count': 3,
        'Special_Event': 'birthday',

        'Health_Problem': 'yes',
        'Health_Severity': 8,
        'Energy_Level': 3,

        'Location': 'Rabat',
    },

    {
        'Stress_Level': 3,
        'Sleep_Hours': 8,
        'Social_Activity': 'low',
        'Work_Status': 'off',

        'Expense_Total': 50,
        'Income_Total': 500,

        'Event_Count': 0,
        'Special_Event': '',

        'Health_Problem': 'no',
        'Health_Severity': 2,
        'Energy_Level': 8,

        'Location': 'Rabat',
    },

    {
        'Stress_Level': 5,
        'Sleep_Hours': 6,
        'Social_Activity': 'medium',
        'Work_Status': 'working',

        'Expense_Total': 150,
        'Income_Total': 0,

        'Event_Count': 2,
        'Special_Event': '',

        'Health_Problem': 'no',
        'Health_Severity': 7,
        'Energy_Level': 5,

        'Location': 'Casablanca',
    },
]


# =========================================================
# TEST 1: DAILY TARGET INTEGRATION
# =========================================================

print('========== TEST 1: DAILY TARGET INTEGRATION ==========')
print()

behavioral = create_behavioral_targets(
    future_rows,
    '1D',
)

financial = create_financial_targets(
    future_rows,
    '1D',
    previous_rows,
)

events = create_event_targets(
    future_rows,
    '1D',
)

health = create_health_targets(
    future_rows,
    '1D',
)

location = create_location_targets(
    future_rows,
    '1D',
    previous_rows,
)

daily_targets = {}

daily_targets.update(behavioral)
daily_targets.update(financial)
daily_targets.update(events)
daily_targets.update(health)
daily_targets.update(location)

print(daily_targets)


# ---------------------------------------------------------
# Behavioral
# ---------------------------------------------------------

assert daily_targets[
    'Target_High_Stress_1D'
] == 1

assert daily_targets[
    'Target_Moderate_or_High_Stress_1D'
] == 1

assert daily_targets[
    'Target_Low_Sleep_1D'
] == 1

assert daily_targets[
    'Target_Very_Low_Sleep_1D'
] == 1

assert daily_targets[
    'Target_High_Social_Activity_1D'
] == 1

assert daily_targets[
    'Target_Moderate_or_High_Social_Activity_1D'
] == 1

assert daily_targets[
    'Target_Working_Day_1D'
] == 1


# ---------------------------------------------------------
# Financial
# ---------------------------------------------------------

assert daily_targets[
    'Target_Expense_Total_1D'
] == 200.0

assert daily_targets[
    'Target_Income_Total_1D'
] == 0.0

assert daily_targets[
    'Target_Balance_1D'
] == -200.0

assert daily_targets[
    'Target_Expense_Days_1D'
] == 1

assert daily_targets[
    'Target_Income_Days_1D'
] == 0

assert daily_targets[
    'Target_High_Expense_1D'
] == 1


# ---------------------------------------------------------
# Events
# ---------------------------------------------------------

assert daily_targets[
    'Target_Has_Event_1D'
] == 1

assert daily_targets[
    'Target_Multiple_Events_1D'
] == 1

assert daily_targets[
    'Target_Has_Special_Event_1D'
] == 1


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

assert daily_targets[
    'Target_Health_Problem_1D'
] == 1

assert daily_targets[
    'Target_High_Health_Severity_1D'
] == 1

assert daily_targets[
    'Target_Low_Energy_1D'
] == 1

assert daily_targets[
    'Target_Significant_Health_Day_1D'
] == 1


# ---------------------------------------------------------
# Location
# ---------------------------------------------------------

assert daily_targets[
    'Target_Has_Location_1D'
] == 1

assert daily_targets[
    'Target_Location_Changed_1D'
] == 1

assert daily_targets[
    'Target_Same_Location_1D'
] == 0

assert daily_targets[
    'Target_Location_1D'
] == 'rabat'


print('Daily target integration: VALID')


# =========================================================
# TEST 2: PERIOD TARGET INTEGRATION
# =========================================================

print()
print('========== TEST 2: PERIOD TARGET INTEGRATION ==========')
print()

behavioral = create_behavioral_targets(
    future_rows,
    '8_15D',
)

financial = create_financial_targets(
    future_rows,
    '8_15D',
    previous_rows,
)

events = create_event_targets(
    future_rows,
    '8_15D',
)

health = create_health_targets(
    future_rows,
    '8_15D',
)

location = create_location_targets(
    future_rows,
    '8_15D',
    previous_rows,
)

period_targets = {}

period_targets.update(behavioral)
period_targets.update(financial)
period_targets.update(events)
period_targets.update(health)
period_targets.update(location)

print(period_targets)


# ---------------------------------------------------------
# Behavioral period
# ---------------------------------------------------------

assert period_targets[
    'Target_High_Stress_8_15D'
] == 1

assert period_targets[
    'Target_Moderate_or_High_Stress_8_15D'
] == 1

assert period_targets[
    'Target_Low_Sleep_8_15D'
] == 1

assert period_targets[
    'Target_Very_Low_Sleep_8_15D'
] == 1

assert period_targets[
    'Target_High_Social_Activity_8_15D'
] == 1

assert period_targets[
    'Target_Moderate_or_High_Social_Activity_8_15D'
] == 1

assert period_targets[
    'Target_Working_Day_8_15D'
] == 1


# ---------------------------------------------------------
# Financial period
# ---------------------------------------------------------

assert period_targets[
    'Target_Expense_Total_8_15D'
] == 400.0

assert period_targets[
    'Target_Income_Total_8_15D'
] == 500.0

assert period_targets[
    'Target_Balance_8_15D'
] == 100.0

assert period_targets[
    'Target_Expense_Days_8_15D'
] == 3

assert period_targets[
    'Target_Income_Days_8_15D'
] == 1

assert period_targets[
    'Target_High_Expense_8_15D'
] == 1


# ---------------------------------------------------------
# Events period
# ---------------------------------------------------------

assert period_targets[
    'Target_Has_Event_8_15D'
] == 1

assert period_targets[
    'Target_Multiple_Events_8_15D'
] == 1

assert period_targets[
    'Target_Has_Special_Event_8_15D'
] == 1


# ---------------------------------------------------------
# Health period
# ---------------------------------------------------------

assert period_targets[
    'Target_Health_Problem_8_15D'
] == 1

assert period_targets[
    'Target_High_Health_Severity_8_15D'
] == 1

assert period_targets[
    'Target_Low_Energy_8_15D'
] == 1

assert period_targets[
    'Target_Significant_Health_Day_8_15D'
] == 1


# ---------------------------------------------------------
# Location period
# ---------------------------------------------------------

assert period_targets[
    'Target_Has_Location_8_15D'
] == 1

assert period_targets[
    'Target_Location_Changed_8_15D'
] == 1

assert period_targets[
    'Target_Same_Location_8_15D'
] == 1

assert period_targets[
    'Target_Location_8_15D'
] == 'casablanca'


print('Period target integration: VALID')


# =========================================================
# TEST 3: TARGET NAME COLLISION CHECK
# =========================================================

print()
print('========== TEST 3: TARGET NAME COLLISION CHECK ==========')
print()

all_target_names = list(
    daily_targets.keys()
) + list(
    period_targets.keys()
)

assert len(
    all_target_names
) == len(
    set(all_target_names)
)

print('No target-name collisions: VALID')


# =========================================================
# TEST 4: EXPECTED TARGET GROUPS
# =========================================================

print()
print('========== TEST 4: EXPECTED TARGET GROUPS ==========')
print()

expected_groups = [
    'Target_High_Stress_1D',
    'Target_Expense_Total_1D',
    'Target_Has_Event_1D',
    'Target_Health_Problem_1D',
    'Target_Has_Location_1D',
]

for target_name in expected_groups:

    assert target_name in daily_targets


print('All target groups present: VALID')


# =========================================================
# TEST 5: TARGET COUNT
# =========================================================

print()
print('========== TEST 5: TARGET COUNT ==========')
print()

print(
    f'Daily target count: '
    f'{len(daily_targets)}'
)

print(
    f'Period target count: '
    f'{len(period_targets)}'
)

assert len(daily_targets) > 0
assert len(period_targets) > 0

print('Target counts: VALID')


# =========================================================
# FINAL
# =========================================================

print()
print('========== SYNTHETIC TARGET INTEGRATION TEST PASSED ==========')