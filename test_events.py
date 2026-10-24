
from math import isnan

from ml.targets.events import (
    create_event_targets_daily,
    create_event_targets_period,
)


# 1. Missing event information means no event
missing = create_event_targets_daily(
    {"Event_Count": None, "Special_Event": None}, "1D"
)
assert missing["Target_Has_Event_1D"] == 0
assert missing["Target_Multiple_Events_1D"] == 0
assert missing["Target_Has_Special_Event_1D"] == 0

# 2. Explicit zero events
zero = create_event_targets_daily(
    {"Event_Count": 0, "Special_Event": ""}, "1D"
)
assert zero["Target_Has_Event_1D"] == 0
assert zero["Target_Has_Special_Event_1D"] == 0

# 3. Multiple events and a special event
positive = create_event_targets_daily(
    {"Event_Count": 2, "Special_Event": "Birthday"}, "1D"
)
assert positive["Target_Has_Event_1D"] == 1
assert positive["Target_Multiple_Events_1D"] == 1
assert positive["Target_Has_Special_Event_1D"] == 1

# 4. Period containing events
period = create_event_targets_period(
    [
        {"Event_Count": 0, "Special_Event": ""},
        {"Event_Count": 2, "Special_Event": "Meeting"},
    ],
    "8_15D",
)
assert period["Target_Has_Event_8_15D"] == 1
assert period["Target_Multiple_Events_8_15D"] == 1
assert period["Target_Has_Special_Event_8_15D"] == 1

# 5. Missing future row must remain unknown
empty = create_event_targets_daily(None, "1D")
assert isnan(empty["Target_Has_Event_1D"])

# 6. Negative event count must be rejected
try:
    create_event_targets_daily({"Event_Count": -1}, "1D")
except ValueError:
    pass
else:
    raise AssertionError("Negative Event_Count was not rejected")

print("Event edge-case tests passed.")
