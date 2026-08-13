def create_event_targets(row):
    """
    Create event-related targets from one prepared daily row.

    Targets describe whether notable event activity
    is expected to occur during the day.
    """

    event_count = int(
        row.get('Event_Count') or 0
    )

    special_event = str(
        row.get('Special_Event') or ''
    ).strip()

    return {
        'Target_Has_Event':
            int(event_count > 0),

        'Target_Multiple_Events':
            int(event_count >= 2),

        'Target_Has_Special_Event':
            int(bool(special_event)),
    }