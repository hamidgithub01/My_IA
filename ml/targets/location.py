def create_location_targets(row):
    """
    Create location-related targets from one prepared daily row.

    Targets describe whether location-related activity
    is present for the day.
    """

    location = str(
        row.get('Location') or ''
    ).strip()

    return {
        'Target_Has_Location':
            int(bool(location)),
    }