import pytest

from ml.preparation.preparation import (
    get_prepared_dataset,
)


@pytest.fixture
def prepared_data():
    """
    Provide the prepared dataset for temporal-integrity tests.
    """

    return get_prepared_dataset()