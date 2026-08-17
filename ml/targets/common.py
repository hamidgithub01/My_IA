# =========================================================
# TARGET COMMON HELPERS
# =========================================================


# =========================================================
# HORIZONS
# =========================================================

DAILY_HORIZONS = {
    '1D': 1,
    '2D': 2,
    '3D': 3,
    '4D': 4,
    '5D': 5,
    '6D': 6,
    '7D': 7,
}


PERIOD_HORIZONS = {
    '8_15D': (8, 15),
    '16_30D': (16, 30),
    '30D': (1, 30),
}


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def to_float(value, default=0.0):
    """
    Safely convert a value to float.

    Invalid or missing values return default.
    """

    try:
        return float(
            value
            if value is not None
            else default
        )

    except (TypeError, ValueError):
        return default


def to_int(value, default=0):
    """
    Safely convert a value to int.

    Invalid or missing values return default.
    """

    try:
        return int(
            value
            if value is not None
            else default
        )

    except (TypeError, ValueError):
        return default


def normalize_text(value):
    """
    Safely normalize a text value.
    """

    return str(
        value or ''
    ).strip().lower()


# =========================================================
# HORIZON HELPERS
# =========================================================

def is_daily_horizon(horizon_name):
    """
    Return True when the horizon is a daily horizon.
    """

    return horizon_name in DAILY_HORIZONS


def is_period_horizon(horizon_name):
    """
    Return True when the horizon is a period horizon.
    """

    return horizon_name in PERIOD_HORIZONS


# =========================================================
# COMMON EMPTY VALUE
# =========================================================

def nan_value():
    """
    Return the standard missing target value.
    """

    return float('nan')