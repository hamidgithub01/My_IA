def create_travel_targets(row):
    """
    Create travel-related targets from one prepared daily row.

    Targets describe whether travel activity is expected
    or present during the day.
    """

    travel = str(
        row.get('Travel') or ''
    ).strip().lower()

    return {
        'Target_Travel':
            int(
                travel
                in {'yes', 'true', '1'}
            ),
    }