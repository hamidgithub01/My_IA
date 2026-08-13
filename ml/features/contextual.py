def normalize_text(value):
    """
    Safely normalize a value into lowercase text.

    None and empty values become an empty string.
    """

    return str(value or '').strip().lower()


def create_contextual_features(row):
    """
    Create contextual features from one prepared daily row.

    Missing contextual information is treated as unknown
    rather than causing an exception.
    """

    day_type = normalize_text(
        row.get('Day_Type')
    )

    work_status = normalize_text(
        row.get('Work_Status')
    )

    health_impact = normalize_text(
        row.get('Health_Impact')
    )

    travel = normalize_text(
        row.get('Travel')
    )

    special_event = normalize_text(
        row.get('Special_Event')
    )

    location = normalize_text(
        row.get('Location')
    )

    return {
        'Is_Workday':
            int(
                day_type
                in {
                    'workday',
                    'working day',
                }
            ),

        'Is_Holiday':
            int(
                day_type
                == 'holiday'
            ),

        'Is_Weekend_Day':
            int(
                day_type
                == 'weekend'
            ),

        'Is_Working':
            int(
                work_status
                in {
                    'working',
                    'work',
                }
            ),

        'Is_Off':
            int(
                work_status
                == 'off'
            ),

        'Is_Leave':
            int(
                work_status
                in {
                    'leave',
                    'vacation',
                }
            ),

        'Has_Health_Impact':
            int(
                health_impact
                not in {
                    '',
                    'none',
                    'normal',
                    'low',
                }
            ),

        'Has_Travel':
            int(
                travel
                in {
                    'yes',
                    'true',
                    '1',
                }
            ),

        'Has_Special_Event':
            int(
                bool(
                    special_event
                )
            ),

        'Has_Location':
            int(
                bool(
                    location
                )
            ),
    }