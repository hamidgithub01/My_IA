from math import isnan

from ml.targets.health import create_health_targets


def test_daily_statuses():
    cases = {
        'Good': (1, 0, 0, 0),
        'Normal': (0, 1, 0, 0),
        'Tired': (0, 0, 1, 0),
        'Sick': (0, 0, 0, 1),
    }

    for status, expected in cases.items():
        row = {
            'Health_Status': status,
            'Severity': 5,
            'Energy_Level': 5,
        }

        result = create_health_targets(
            [row],
            '1D',
        )

        actual = (
            result['Target_Health_Status_Good_1D'],
            result['Target_Health_Status_Normal_1D'],
            result['Target_Health_Status_Tired_1D'],
            result['Target_Health_Status_Sick_1D'],
        )

        assert actual == expected, (
            status,
            actual,
        )


def test_tired_is_significant_but_not_illness():
    row = {
        'Health_Status': 'Tired',
        'Severity': 5,
        'Energy_Level': 5,
    }

    result = create_health_targets(
        [row],
        '1D',
    )

    assert result['Target_Health_Problem_1D'] == 0
    assert result['Target_Significant_Health_Day_1D'] == 1


def test_high_severity():
    row = {
        'Health_Status': 'Normal',
        'Severity': 7,
        'Energy_Level': 5,
    }

    result = create_health_targets(
        [row],
        '1D',
    )

    assert result['Target_High_Health_Severity_1D'] == 1
    assert result['Target_Significant_Health_Day_1D'] == 1


def test_missing_values_remain_unknown():
    row = {
        'Health_Status': None,
        'Severity': None,
        'Energy_Level': None,
    }

    result = create_health_targets(
        [row],
        '1D',
    )

    for key, value in result.items():
        assert isnan(value), (key, value)


def test_period_statuses_are_distinct():
    rows = [
        {
            'Health_Status': 'Good',
            'Severity': 2,
            'Energy_Level': 8,
        },
        {
            'Health_Status': 'Tired',
            'Severity': 3,
            'Energy_Level': 5,
        },
        {
            'Health_Status': 'Sick',
            'Severity': 8,
            'Energy_Level': 5,
        },
    ]

    result = create_health_targets(
        rows,
        '8_15D',
    )

    assert result['Target_Health_Status_Good_8_15D'] == 1
    assert result['Target_Health_Status_Normal_8_15D'] == 0
    assert result['Target_Health_Status_Tired_8_15D'] == 1
    assert result['Target_Health_Status_Sick_8_15D'] == 1

    assert result['Target_Health_Problem_8_15D'] == 1
    assert result['Target_High_Health_Severity_8_15D'] == 1
    assert result['Target_Significant_Health_Day_8_15D'] == 1


def test_invalid_horizon():
    try:
        create_health_targets([], 'INVALID')
    except ValueError:
        return

    raise AssertionError('Invalid horizon was accepted')


def run_tests():
    test_daily_statuses()
    test_tired_is_significant_but_not_illness()
    test_high_severity()
    test_missing_values_remain_unknown()
    test_period_statuses_are_distinct()
    test_invalid_horizon()

    print('Health target tests passed.')


if __name__ == '__main__':
    run_tests()