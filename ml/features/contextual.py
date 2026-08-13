
def create_contextual_features(row):
    """
    Create contextual features from one prepared daily row.

    Contextual features describe the surrounding circumstances
    of the day without directly encoding the date itself.
    """

    return {
        'Is_Workday':
            int(
                row.get('Day_Type', '').strip().lower()
                in {
                    'workday',
                    'working day',
                }
            ),

        'Is_Holiday':
            int(
                row.get('Day_Type', '').strip().lower()
                == 'holiday'
            ),

        'Is_Weekend_Day':
            int(
                row.get('Day_Type', '').strip().lower()
                == 'weekend'
            ),

        'Is_Working':
            int(
                row.get('Work_Status', '').strip().lower()
                in {
                    'working',
                    'work',
                }
            ),

        'Is_Off':
            int(
                row.get('Work_Status', '').strip().lower()
                == 'off'
            ),

        'Is_Leave':
            int(
                row.get('Work_Status', '').strip().lower()
                in {
                    'leave',
                    'vacation',
                }
            ),

        'Has_Health_Impact':
            int(
                row.get('Health_Impact', '').strip().lower()
                not in {
                    '',
                    'none',
                    'normal',
                    'low',
                }
            ),

        'Has_Travel':
            int(
                row.get('Travel', '').strip().lower()
                in {
                    'yes',
                    'true',
                    '1',
                }
            ),

        'Has_Special_Event':
            int(
                bool(
                    str(
                        row.get('Special_Event') or ''
                    ).strip()
                )
            ),

        'Has_Location':
            int(
                bool(
                    str(
                        row.get('Location') or ''
                    ).strip()
                )
            ),
    }