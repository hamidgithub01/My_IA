def create_health_targets(row):
    """
    Create health-related targets from one prepared daily row.

    Targets describe health-related outcomes that the
    machine-learning system may learn to predict.
    """

    health_impact = str(
        row.get('Health_Impact') or ''
    ).strip().lower()

    sleep_hours = float(
        row.get('Sleep_Hours') or 0.0
    )

    stress_level = float(
        row.get('Stress_Level') or 0.0
    )

    return {
        'Target_Health_Problem':
            int(
                health_impact
                in {'moderate', 'medium', 'high'}
            ),

        'Target_Insufficient_Sleep':
            int(
                sleep_hours > 0
                and sleep_hours < 6
            ),

        'Target_High_Stress':
            int(stress_level >= 7),
    }