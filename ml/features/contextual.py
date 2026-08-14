def normalize_text(value):
    """
    Safely normalize a value into lowercase text.

    None and empty values become an empty string.
    """

    return str(
        value or ''
    ).strip().lower()


# ==========================================================
# HISTORICAL CONTEXT
# ==========================================================

def create_historical_contextual_features(
    historical_row,
):
    """
    Create contextual features from a historical day.

    IMPORTANT:

        These features describe a day that has already ended.

        They must only be used as historical information
        when building features for a later target day.

        Days information is recorded after the day ends.
        Therefore, these values must NEVER describe the
        target day itself.
    """

    if not historical_row:
        return {
            'Historical_Is_Workday': 0,
            'Historical_Is_Holiday': 0,
            'Historical_Is_Weekend_Day': 0,

            'Historical_Is_Working': 0,
            'Historical_Is_Off': 0,
            'Historical_Is_Leave': 0,

            'Historical_Has_Health_Impact': 0,
            'Historical_Has_Travel': 0,
            'Historical_Has_Special_Event': 0,
            'Historical_Has_Location': 0,
        }

    day_type = normalize_text(
        historical_row.get(
            'Day_Type'
        )
    )

    work_status = normalize_text(
        historical_row.get(
            'Work_Status'
        )
    )

    health_impact = normalize_text(
        historical_row.get(
            'Health_Impact'
        )
    )

    travel = normalize_text(
        historical_row.get(
            'Travel'
        )
    )

    special_event = normalize_text(
        historical_row.get(
            'Special_Event'
        )
    )

    location = normalize_text(
        historical_row.get(
            'Location'
        )
    )

    return {

        # --------------------------------------------------
        # Day type
        # --------------------------------------------------

        'Historical_Is_Workday':
            int(
                day_type
                in {
                    'workday',
                    'working day',
                }
            ),

        'Historical_Is_Holiday':
            int(
                day_type
                == 'holiday'
            ),

        'Historical_Is_Weekend_Day':
            int(
                day_type
                == 'weekend'
            ),

        # --------------------------------------------------
        # Work status
        # --------------------------------------------------

        'Historical_Is_Working':
            int(
                work_status
                in {
                    'working',
                    'work',
                }
            ),

        'Historical_Is_Off':
            int(
                work_status
                == 'off'
            ),

        'Historical_Is_Leave':
            int(
                work_status
                in {
                    'leave',
                    'vacation',
                }
            ),

        # --------------------------------------------------
        # Health
        # --------------------------------------------------

        'Historical_Has_Health_Impact':
            int(
                health_impact
                not in {
                    '',
                    'none',
                    'normal',
                    'low',
                }
            ),

        # --------------------------------------------------
        # Travel
        # --------------------------------------------------

        'Historical_Has_Travel':
            int(
                travel
                in {
                    'yes',
                    'true',
                    '1',
                }
            ),

        # --------------------------------------------------
        # Special event
        # --------------------------------------------------

        'Historical_Has_Special_Event':
            int(
                bool(
                    special_event
                )
            ),

        # --------------------------------------------------
        # Location
        # --------------------------------------------------

        'Historical_Has_Location':
            int(
                bool(
                    location
                )
            ),
    }