
import pytest

from ml.features.build import build_training_dataset


def test_temporal_split():
    data = build_training_dataset()

    print()
    print(
        '========== TEMPORAL TRAIN/TEST SPLIT TEST =========='
    )

    if len(data) < 3:

        pytest.skip(
            f'Not enough rows for temporal split: {len(data)}'
        )

    # ------------------------------------------------------
    # Sort chronologically
    # ------------------------------------------------------

    data = sorted(
        data,
        key=lambda row: row['Date'],
    )

    # ------------------------------------------------------
    # Chronological split
    #
    # 80% training
    # 20% test
    # ------------------------------------------------------

    split_index = int(
        len(data) * 0.8
    )

    # Make sure both sets contain at least one row.
    split_index = max(
        1,
        min(
            split_index,
            len(data) - 1,
        ),
    )

    training_data = data[:split_index]
    test_data = data[split_index:]

    last_training_date = (
        training_data[-1]['Date']
    )

    first_test_date = (
        test_data[0]['Date']
    )

    print(
        f'Total rows: {len(data)}'
    )

    print(
        f'Training rows: {len(training_data)}'
    )

    print(
        f'Test rows: {len(test_data)}'
    )

    print(
        f'Last training date: '
        f'{last_training_date}'
    )

    print(
        f'First test date: '
        f'{first_test_date}'
    )

    # ------------------------------------------------------
    # Test 1: chronological ordering
    # ------------------------------------------------------

    chronological_errors = []

    for index in range(
        1,
        len(data),
    ):

        previous_date = data[
            index - 1
        ]['Date']

        current_date = data[
            index
        ]['Date']

        if current_date <= previous_date:

            chronological_errors.append(
                (
                    previous_date,
                    current_date,
                )
            )

    assert not chronological_errors, (
        'Chronological ordering failed:\n'
        + '\n'.join(
            f' - {error}'
            for error in chronological_errors
        )
    )

    print(
        'Chronological ordering: PASSED'
    )

    # ------------------------------------------------------
    # Test 2: no date overlap
    # ------------------------------------------------------

    training_dates = {
        row['Date']
        for row in training_data
    }

    test_dates = {
        row['Date']
        for row in test_data
    }

    date_overlap = (
        training_dates
        & test_dates
    )

    assert not date_overlap, (
        'Date separation failed. '
        f'Overlapping dates: {sorted(date_overlap)}'
    )

    print(
        'Date separation: PASSED'
    )

    # ------------------------------------------------------
    # Test 3: test must be strictly after training
    # ------------------------------------------------------

    temporal_violations = []

    for row in test_data:

        if row['Date'] <= last_training_date:

            temporal_violations.append(
                row['Date']
            )

    assert not temporal_violations, (
        'Future leakage detected. '
        f'Violating dates: {temporal_violations}'
    )

    print(
        'Future leakage: PASSED'
    )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    print()

    print(
        '========== TEMPORAL SPLIT TEST PASSED =========='
    )


if __name__ == '__main__':
    test_temporal_split()
