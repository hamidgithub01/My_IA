from datetime import date, datetime
from decimal import Decimal


def clean_date(value):
    """
    Convert a value to a Python date.

    Returns None when the value cannot be converted.
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None

    return None


def clean_numeric(value, default=0.0):
    """
    Convert numeric values to float.

    Returns the provided default when the value is invalid.
    """

    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clean_text(value, default=None):
    """
    Normalize text values.

    Empty strings are treated as missing values.
    """

    if value is None:
        return default

    if not isinstance(value, str):
        value = str(value)

    value = value.strip()

    if not value:
        return default

    return value


def clean_record(record):
    """
    Clean a generic database record.

    This function does not modify the original record.
    """

    if not record:
        return {}

    cleaned = {}

    for key, value in record.items():

        if isinstance(value, (date, datetime)):
            cleaned[key] = clean_date(value)

        elif isinstance(value, Decimal):
            cleaned[key] = clean_numeric(value)

        elif isinstance(value, str):
            cleaned[key] = clean_text(value)

        else:
            cleaned[key] = value

    return cleaned