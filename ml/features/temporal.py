from datetime import date, datetime
import calendar


def create_temporal_features(row):
    """
    Create calendar-based temporal features.
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

    days_in_month = calendar.monthrange(
        current_date.year,
        current_date.month,
    )[1]

    return {
        'Day_of_Week':
            weekday,

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

        'Is_Month_End':
            int(
                current_date.day
                == days_in_month
            ),

        'Week_of_Month':
            ((current_date.day - 1) // 7) + 1,

        'Days_From_Month_Start':
            current_date.day - 1,

        'Days_To_Month_End':
            days_in_month
            - current_date.day,
    }