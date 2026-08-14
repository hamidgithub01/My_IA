
def normalize_text(value):
    """
    Safely normalize a value into lowercase text.

    None and empty values become an empty string.
    """

    return str(
        value or ''
    ).strip().lower()


# ==========================================================
# BINARY ENCODING
# ==========================================================

def encode_binary(
    value,
    positive_values,
):
    """
    Convert a categorical value into a binary feature.

    Returns 1 when the value belongs to positive_values,
    otherwise 0.
    """

    normalized = normalize_text(
        value
    )

    positive_values = {
        str(item).strip().lower()
        for item in positive_values
    }

    return int(
        normalized in positive_values
    )


# ==========================================================
# DAY TYPE
# ==========================================================

def encode_day_type(value):
    """
    Encode historical day type.

    Unknown = 0
    Workday = 1
    Holiday = 2
    Weekend = 3
    """

    mapping = {
        'workday': 1,
        'working day': 1,
        'holiday': 2,
        'weekend': 3,
    }

    return mapping.get(
        normalize_text(value),
        0,
    )


# ==========================================================
# WORK STATUS
# ==========================================================

def encode_work_status(value):
    """
    Encode historical work status.

    Unknown = 0
    Working = 1
    Off = 2
    Leave = 3
    Vacation = 4
    """

    mapping = {
        'working': 1,
        'work': 1,
        'off': 2,
        'leave': 3,
        'vacation': 4,
    }

    return mapping.get(
        normalize_text(value),
        0,
    )


# ==========================================================
# HEALTH IMPACT
# ==========================================================

def encode_health_impact(value):
    """
    Encode historical health impact.

    Low / Normal = 0
    Moderate / Medium = 1
    High = 2
    Unknown = 0
    """

    mapping = {
        'low': 0,
        'normal': 0,
        'moderate': 1,
        'medium': 1,
        'high': 2,
    }

    return mapping.get(
        normalize_text(value),
        0,
    )


# ==========================================================
# TRAVEL
# ==========================================================

def encode_travel(value):
    """
    Encode historical travel information.
    """

    return encode_binary(
        value,
        [
            'yes',
            'true',
            '1',
        ],
    )


# ==========================================================
# SOCIAL ACTIVITY
# ==========================================================

def encode_social_activity(value):
    """
    Encode historical social activity.

    Low = 0
    Moderate / Medium = 1
    High = 2
    Unknown = 0
    """

    mapping = {
        'low': 0,
        'moderate': 1,
        'medium': 1,
        'high': 2,
    }

    return mapping.get(
        normalize_text(value),
        0,
    )


# ==========================================================
# SPECIAL EVENT
# ==========================================================

def encode_special_event(value):
    """
    Indicate whether a historical special event exists.
    """

    if not normalize_text(value):
        return 0

    return 1


# ==========================================================
# LOCATION
# ==========================================================

def encode_location(value):
    """
    Indicate whether historical location information exists.

    The actual location is intentionally not converted into
    a number because doing so would create an artificial
    numerical order.
    """

    if not normalize_text(value):
        return 0

    return 1


# ==========================================================
# HISTORICAL BEHAVIORAL FEATURES
# ==========================================================

def create_historical_behavioral_features(
    historical_row,
):
    """
    Create behavioral features from ONE historical day.

    This function is intentionally designed for historical
    rows only.

    It must NEVER receive the target day's row.

    The resulting values describe what happened on a previous
    day and can therefore safely be used to predict a future
    target day.
    """

    if not historical_row:
        return {
            'Historical_Day_Type_Code': 0,
            'Historical_Work_Status_Code': 0,
            'Historical_Health_Impact_Code': 0,
            'Historical_Travel_Flag': 0,
            'Historical_Stress_Level': 0.0,
            'Historical_Sleep_Hours': 0.0,
            'Historical_Social_Activity_Code': 0,
            'Historical_Special_Event_Flag': 0,
            'Historical_Location_Flag': 0,
        }

    return {
        'Historical_Day_Type_Code':
            encode_day_type(
                historical_row.get(
                    'Day_Type'
                )
            ),

        'Historical_Work_Status_Code':
            encode_work_status(
                historical_row.get(
                    'Work_Status'
                )
            ),

        'Historical_Health_Impact_Code':
            encode_health_impact(
                historical_row.get(
                    'Health_Impact'
                )
            ),

        'Historical_Travel_Flag':
            encode_travel(
                historical_row.get(
                    'Travel'
                )
            ),

        'Historical_Stress_Level':
            float(
                historical_row.get(
                    'Stress_Level'
                )
                or 0.0
            ),

        'Historical_Sleep_Hours':
            float(
                historical_row.get(
                    'Sleep_Hours'
                )
                or 0.0
            ),

        'Historical_Social_Activity_Code':
            encode_social_activity(
                historical_row.get(
                    'Social_Activity'
                )
            ),

        'Historical_Special_Event_Flag':
            encode_special_event(
                historical_row.get(
                    'Special_Event'
                )
            ),

        'Historical_Location_Flag':
            encode_location(
                historical_row.get(
                    'Location'
                )
            ),
    }


# ==========================================================
# BACKWARD-COMPATIBILITY
# ==========================================================

def create_behavioral_features(row):
    """
    Backward-compatible wrapper.

    IMPORTANT:
    This function is retained so existing imports do not
    immediately break.

    New feature-engineering code should NOT call this
    function with the target row.

    Use:

        create_historical_behavioral_features(
            historical_row
        )

    instead.
    """

    return create_historical_behavioral_features(
        row
    )
