from ml.preparation.preparation import (
    get_prepared_dataset,
)

from ml.features.contextual import (
    create_known_future_features,
)


# ==========================================================
# EXPECTED KNOWN FUTURE FEATURES
# ==========================================================

EXPECTED_FEATURE_SOURCES = {
    'Known_Plan_Count':
        'Plan_Count',

    'Known_Plan_Expected_Cost':
        'Plan_Expected_Cost',

    'Known_Plan_Duration_Days':
        'Plan_Duration_Days',

    'Known_High_Importance_Plan_Count':
        'High_Importance_Plan_Count',

    'Known_Recurring_Count':
        'Recurring_Count',

    'Known_Recurring_Amount':
        'Recurring_Amount',

    'Known_Recurring_Expense_Amount':
        'Recurring_Expense_Amount',

    'Known_Recurring_Income_Amount':
        'Recurring_Income_Amount',

    'Known_Fixed_Recurring_Amount':
        'Fixed_Recurring_Amount',
}


# ==========================================================
# FORBIDDEN ACTUAL OUTCOMES
# ==========================================================

FORBIDDEN_ACTUAL_FIELDS = {
    'Expense_Total',
    'Expense_Count',

    'Income_Total',
    'Income_Count',

    'Event_Count',

    'Health_Record_Count',
    'Max_Health_Severity',
    'Avg_Energy_Level',

    'Activity_Count',
    'Activity_Duration_Minutes',
    'Activity_Cost',

    'Sleep_Record_Count',
    'Sleep_Duration_Minutes',
    'Avg_Sleep_Quality',
    'Total_Awakenings',
}


# ==========================================================
# TEST
# ==========================================================

def test_known_future_features():
    print(
        "========== KNOWN FUTURE FEATURES TEST =========="
    )

    prepared_data = get_prepared_dataset()

    if not prepared_data:
        print(
            "No prepared data available."
        )

        return

    # ------------------------------------------------------
    # Test 1:
    # All expected source fields must exist.
    # ------------------------------------------------------

    available_fields = set(
        prepared_data[0].keys()
    )

    missing_sources = []

    for (
        feature_name,
        source_field,
    ) in EXPECTED_FEATURE_SOURCES.items():

        if source_field not in available_fields:

            missing_sources.append(
                (
                    feature_name,
                    source_field,
                )
            )

    if missing_sources:

        print(
            "Missing source fields:"
        )

        for (
            feature_name,
            source_field,
        ) in missing_sources:

            print(
                f"  {feature_name} "
                f"<- {source_field}"
            )

        raise AssertionError(
            "One or more Known Future "
            "Feature sources are missing."
        )

    print(
        "All Known Future Feature sources: PASSED"
    )

    # ------------------------------------------------------
    # Test 2:
    # Build Known Future Features from every row.
    # ------------------------------------------------------

    for row in prepared_data:

        features = (
            create_known_future_features(
                row
            )
        )

        actual_feature_names = set(
            features.keys()
        )

        expected_feature_names = set(
            EXPECTED_FEATURE_SOURCES.keys()
        )

        if (
            actual_feature_names
            != expected_feature_names
        ):

            missing = (
                expected_feature_names
                - actual_feature_names
            )

            unexpected = (
                actual_feature_names
                - expected_feature_names
            )

            raise AssertionError(
                "Known Future Feature "
                "structure mismatch.\n"
                f"Missing: {missing}\n"
                f"Unexpected: {unexpected}"
            )

    print(
        "Known Future Feature structure: PASSED"
    )

    # ------------------------------------------------------
    # Test 3:
    # No forbidden actual outcome fields may be used
    # as Known Future Features.
    # ------------------------------------------------------

    for (
        feature_name,
        source_field,
    ) in EXPECTED_FEATURE_SOURCES.items():

        if source_field in (
            FORBIDDEN_ACTUAL_FIELDS
        ):

            raise AssertionError(
                f"Temporal leakage detected: "
                f"{feature_name} uses "
                f"actual field "
                f"{source_field}."
            )

    print(
        "Actual outcome leakage check: PASSED"
    )

    # ------------------------------------------------------
    # Test 4:
    # Explicitly reject the previously identified
    # non-existent field.
    # ------------------------------------------------------

    if (
        'Active_Recurring_Count'
        in available_fields
    ):

        raise AssertionError(
            "Unexpected Active_Recurring_Count "
            "found in prepared data. "
            "Review the Known Future design."
        )

    print(
        "Recurring source consistency: PASSED"
    )

    # ------------------------------------------------------
    # Test 5:
    # Verify that target-day actual outcomes can change
    # without changing Known Future Features.
    #
    # This is a direct anti-leakage test.
    # ------------------------------------------------------

    sample_row = dict(
        prepared_data[0]
    )

    original_features = (
        create_known_future_features(
            sample_row
        )
    )

    # Change actual outcomes deliberately.
    for field in FORBIDDEN_ACTUAL_FIELDS:

        if field in sample_row:

            sample_row[field] = (
                999999.99
            )

    modified_features = (
        create_known_future_features(
            sample_row
        )
    )

    if (
        original_features
        != modified_features
    ):

        raise AssertionError(
            "Temporal leakage detected: "
            "Known Future Features changed "
            "when actual target-day outcomes "
            "were modified."
        )

    print(
        "Target-day outcome independence: PASSED"
    )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    print(
        "========== KNOWN FUTURE FEATURES "
        "TEST PASSED =========="
    )


if __name__ == '__main__':
    test_known_future_features()