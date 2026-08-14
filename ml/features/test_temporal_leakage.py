from ml.preparation.preparation import (
    get_prepared_dataset,
)

from ml.features.build import (
    build_feature_row,
)


def to_date(value):
    if hasattr(value, 'date'):
        return value.date()

    if isinstance(value, str):
        return value[:10]

    return value


def run_temporal_leakage_test():

    print(
        '========== TEMPORAL LEAKAGE TEST =========='
    )

    prepared_data = get_prepared_dataset()

    if len(prepared_data) < 2:

        print(
            'Not enough data for temporal leakage test.'
        )

        return False

    prepared_data = sorted(
        prepared_data,
        key=lambda row: row['Date'],
    )

    errors = []

    # ======================================================
    # TEST EVERY TRAINING ROW
    # ======================================================

    for index in range(
        1,
        len(prepared_data),
    ):

        target_row = prepared_data[index]

        target_date = to_date(
            target_row['Date']
        )

        previous_rows = prepared_data[:index]

        # --------------------------------------------------
        # Verify previous_rows
        # --------------------------------------------------

        for historical_row in previous_rows:

            historical_date = to_date(
                historical_row.get('Date')
            )

            if (
                historical_date is not None
                and historical_date >= target_date
            ):

                errors.append(
                    (
                        target_date,
                        'previous_rows contains '
                        f'future/current date '
                        f'{historical_date}'
                    )
                )

        # --------------------------------------------------
        # Build features
        # --------------------------------------------------

        features = build_feature_row(
            target_row,
            previous_rows,
        )

        # --------------------------------------------------
        # Direct target leakage
        # --------------------------------------------------

        forbidden = {
            'Expense_Total',
            'Income_Total',
            'Event_Count',
            'Health_Record_Count',
            'Max_Health_Severity',
            'Avg_Energy_Level',
            'Activity_Count',
            'Activity_Duration_Minutes',
            'Activity_Cost',
            'Sleep_Duration_Minutes',
            'Avg_Sleep_Quality',
            'Total_Awakenings',
            'Stress_Level',
            'Sleep_Hours',
            'Social_Activity',
            'Work_Status',
            'Travel',
            'Special_Event',
            'Location',
        }

        leaked_columns = [
            column
            for column in features
            if column in forbidden
        ]

        if leaked_columns:

            errors.append(
                (
                    target_date,
                    'raw target-day columns found '
                    f'in features: {leaked_columns}'
                )
            )

        # --------------------------------------------------
        # Target columns
        # --------------------------------------------------

        target_columns = [
            column
            for column in features
            if column.startswith('Target_')
        ]

        if target_columns:

            errors.append(
                (
                    target_date,
                    'Target columns found in features: '
                    f'{target_columns}'
                )
            )

    # ======================================================
    # RESULT
    # ======================================================

    print(
        'Training rows checked:',
        len(prepared_data) - 1,
    )

    print(
        'Leakage errors:',
        len(errors),
    )

    if errors:

        print()
        print(
            '========== TEMPORAL LEAKAGE DETECTED =========='
        )

        for error in errors:

            print(
                f'Date: {error[0]}'
            )

            print(
                f'Problem: {error[1]}'
            )

        return False

    print(
        '========== TEMPORAL LEAKAGE TEST PASSED =========='
    )

    return True


if __name__ == '__main__':

    success = run_temporal_leakage_test()

    if not success:

        raise SystemExit(1)