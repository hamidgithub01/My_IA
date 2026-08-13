from ml.features.build import (
    build_training_dataset,
    get_feature_names,
)


def main():
    print("\n========== FEATURE ENGINEERING TEST ==========\n")

    try:
        dataset = build_training_dataset()

        print(
            f"Training rows: {len(dataset)}"
        )

        if not dataset:
            print(
                "\nNo training data available."
            )
            print(
                "At least 2 historical days are required."
            )
            return

        first_row = dataset[0]

        print(
            "\n========== FIRST TRAINING ROW ==========\n"
        )

        for key, value in first_row.items():
            print(
                f"{key}: {value}"
            )

        feature_names = get_feature_names(
            dataset
        )

        print(
            "\n========== FEATURE NAMES ==========\n"
        )

        for index, feature in enumerate(
            feature_names,
            start=1,
        ):
            print(
                f"{index}. {feature}"
            )

        print(
            "\n========== EXCLUSION CHECK ==========\n"
        )

        print(
            "Date in features:",
            'Date' in feature_names,
        )

        print(
            "Target in features:",
            'Target_Expense_Total'
            in feature_names,
        )

        print(
            "\n========== TARGET ==========\n"
        )

        print(
            "Target_Expense_Total:",
            first_row[
                'Target_Expense_Total'
            ],
        )

        print(
            "\n========== TEST RESULT ==========\n"
        )

        if (
            'Date' not in feature_names
            and
            'Target_Expense_Total'
            not in feature_names
        ):
            print(
                "PASS: Date and target are "
                "correctly excluded from model features."
            )
        else:
            print(
                "FAIL: Invalid feature leakage detected."
            )

    except Exception as error:

        print(
            "\n========== TEST FAILED ==========\n"
        )

        print(
            type(error).__name__
        )

        print(error)


if __name__ == "__main__":
    main()