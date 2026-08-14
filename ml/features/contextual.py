
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


# ==========================================================
# KNOWN FUTURE CONTEXT
# ==========================================================

def create_known_future_features(
    target_row,
):
    """
    Create features from information known in advance
    about the target day.

    These values are fundamentally different from
    historical observations.

    Plans and recurring rules can be known before the
    target day occurs. Therefore, they are legitimate
    predictors for future forecasting.

    IMPORTANT:

        This function MUST NOT use actual outcomes such as:

            Expense_Total
            Income_Total
            Activity_Cost
            Health_Record_Count
            etc.

        It only uses information that can reasonably be
        known before the target day.
    """

    if not target_row:
        target_row = {}

    return {

        # --------------------------------------------------
        # Plans
        # --------------------------------------------------

        'Known_Plan_Count':
            int(
                target_row.get(
                    'Plan_Count',
                    0,
                )
                or 0
            ),

        'Known_Plan_Expected_Cost':
            float(
                target_row.get(
                    'Plan_Expected_Cost',
                    0.0,
                )
                or 0.0
            ),

        'Known_Plan_Duration_Days':
            float(
                target_row.get(
                    'Plan_Duration_Days',
                    0.0,
                )
                or 0.0
            ),

        'Known_High_Importance_Plan_Count':
            int(
                target_row.get(
                    'High_Importance_Plan_Count',
                    0,
                )
                or 0
            ),

        # --------------------------------------------------
        # Recurring
        # --------------------------------------------------

        'Known_Recurring_Count':
            int(
                target_row.get(
                    'Recurring_Count',
                    0,
                )
                or 0
            ),

        'Known_Recurring_Amount':
            float(
                target_row.get(
                    'Recurring_Amount',
                    0.0,
                )
                or 0.0
            ),

        'Known_Recurring_Expense_Amount':
            float(
                target_row.get(
                    'Recurring_Expense_Amount',
                    0.0,
                )
                or 0.0
            ),

        'Known_Recurring_Income_Amount':
            float(
                target_row.get(
                    'Recurring_Income_Amount',
                    0.0,
                )
                or 0.0
            ),

        'Known_Fixed_Recurring_Amount':
            float(
                target_row.get(
                    'Fixed_Recurring_Amount',
                    0.0,
                )
                or 0.0
            ),

        'Known_Active_Recurring_Count':
            int(
                target_row.get(
                    'Active_Recurring_Count',
                    0,
                )
                or 0
            ),
    }
