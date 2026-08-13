def create_behavioral_targets(row):
    """
    Create behavioral targets from one prepared daily row.

    Targets describe important behavioral outcomes
    that the machine-learning system may learn to predict.
    """

    stress_level = float(
        row.get('Stress_Level') or 0.0
    )

    sleep_hours = float(
        row.get('Sleep_Hours') or 0.0
    )

    social_activity = str(
        row.get('Social_Activity') or ''
    ).strip().lower()

    health_impact = str(
        row.get('Health_Impact') or ''
    ).strip().lower()

    return {
        'Target_High_Stress':
            int(stress_level >= 7),

        'Target_Low_Sleep':
            int(
                sleep_hours > 0
                and sleep_hours < 6
            ),

        'Target_High_Social_Activity':
            int(
                social_activity == 'high'
            ),

        'Target_Health_Impact':
            int(
                health_impact
                in {'moderate', 'medium', 'high'}
            ),
    }