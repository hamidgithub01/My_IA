from datetime import date, datetime


def create_temporal_features(row):
    """
    Create temporal features from the daily date.
    """

    value = row.get('Date')

    if isinstance(value, datetime):
        current_date = value.date()

    elif isinstance(value, date):
        current_date = value

    elif isinstance(value, str):

        try:
            current_date = date.fromisoformat(
                value[:10]
            )

        except ValueError:
            return {}

    else:
        return {}

    weekday = current_date.weekday()

    return {
        'Day_of_Week': weekday,

        'Day_of_Month':
            current_date.day,

        'Month':
            current_date.month,

        'Quarter':
            ((current_date.month - 1) // 3) + 1,

        'Is_Weekend':
            int(weekday >= 5),

        'Is_Month_Start':
            int(current_date.day == 1),
    }