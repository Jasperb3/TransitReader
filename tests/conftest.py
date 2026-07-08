from datetime import datetime

import pytest


@pytest.fixture
def fixture_subject():
    """Public birth data for Winston Churchill (not a real user subject)."""
    return {
        "date_of_birth": datetime(1874, 11, 30, 1, 30),
        "latitude": 51.848,
        "longitude": -1.353,
        "timezone": "Europe/London",
    }
