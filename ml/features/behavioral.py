def encode_binary(value, positive_values):
    """
    Convert a categorical value into a binary feature.

    Returns 1 when the value belongs to positive_values,
    otherwise 0.
    """

    if value is None:
        return 0

    normalized = str(value).strip().lower()

    return int(
        normalized in {
            str(item).strip().lower()
            for item in positive_values
        }
    )


def encode_day_type(value):
    """
    Encode the type of day.
    """

    if value is None:
        return 0

    mapping = {
        'workday': 1,
        'working day': 1,
        'holiday': 2,
        'weekend': 3,
    }

    return mapping.get(
        str(value).strip().lower(),
        0,
    )


def encode_work_status(value):
    """
    Encode work status.
    """

    if value is None:
        return 0

    mapping = {
        'working': 1,
        'work': 1,
        'off': 2,
        'leave': 3,
        'vacation': 4,
    }

    return mapping.get(
        str(value).strip().lower(),
        0,
    )


def encode_health_impact(value):
    """
    Encode health impact.

    Low = 0
    Moderate = 1
    High = 2
    """

    if value is None:
        return 0

    mapping = {
        'low': 0,
        'normal': 0,
        'moderate': 1,
        'medium': 1,
        'high': 2,
    }

    return mapping.get(
        str(value).strip().lower(),
        0,
    )


def encode_travel(value):
    """
    Encode travel information.
    """

    return encode_binary(
        value,
        ['yes', 'true', '1'],
    )


def encode_social_activity(value):
    """
    Encode social activity.

    None/Low = 0
    Moderate = 1
    High = 2
    """

    if value is None:
        return 0

    mapping = {
        'low': 0,
        'moderate': 1,
        'medium': 1,
        'high': 2,
    }

    return mapping.get(
        str(value).strip().lower(),
        0,
    )


def encode_special_event(value):
    """
    Indicate whether a special event exists.
    """

    if value is None:
        return 0

    return int(
        bool(str(value).strip())
    )


def encode_location(value):
    """
    Indicate whether a location is available.

    We do not encode the actual location as a number
    because doing so would create an artificial order.
    """

    if value is None:
        return 0

    return int(
        bool(str(value).strip())
    )


def create_behavioral_features(row):
    """
    Create behavioral features from one prepared daily row.
    """

    return {
        'Day_Type_Code':
            encode_day_type(
                row.get('Day_Type')
            ),

        'Work_Status_Code':
            encode_work_status(
                row.get('Work_Status')
            ),

        'Health_Impact_Code':
            encode_health_impact(
                row.get('Health_Impact')
            ),

        'Travel_Flag':
            encode_travel(
                row.get('Travel')
            ),

        'Stress_Level':
            float(
                row.get('Stress_Level') or 0.0
            ),

        'Sleep_Hours':
            float(
                row.get('Sleep_Hours') or 0.0
            ),

        'Social_Activity_Code':
            encode_social_activity(
                row.get('Social_Activity')
            ),

        'Special_Event_Flag':
            encode_special_event(
                row.get('Special_Event')
            ),

        'Location_Flag':
            encode_location(
                row.get('Location')
            ),
    }