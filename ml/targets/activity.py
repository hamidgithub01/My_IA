def create_activity_targets(row):
    """
    Create activity-related targets from one prepared daily row.

    Targets describe the expected activity pattern of the day.
    """

    work_status = str(
        row.get('Work_Status') or ''
    ).strip().lower()

    travel = str(
        row.get('Travel') or ''
    ).strip().lower()

    social_activity = str(
        row.get('Social_Activity') or ''
    ).strip().lower()

    return {
        'Target_Working_Day':
            int(
                work_status
                in {'working', 'work'}
            ),

        'Target_Travel_Day':
            int(
                travel
                in {'yes', 'true', '1'}
            ),

        'Target_High_Social_Activity':
            int(
                social_activity == 'high'
            ),
    }