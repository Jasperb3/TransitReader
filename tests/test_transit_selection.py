from datetime import datetime
from zoneinfo import ZoneInfo

from transit_reader.utils.transit_selection import _now_at_location


def test_now_at_location_differs_by_expected_hour_gap():
    ny = _now_at_location("America/New_York")
    sydney = _now_at_location("Australia/Sydney")

    expected_ny = datetime.now(ZoneInfo("America/New_York")).replace(tzinfo=None, second=0, microsecond=0)
    expected_sydney = datetime.now(ZoneInfo("Australia/Sydney")).replace(tzinfo=None, second=0, microsecond=0)

    assert abs((ny - expected_ny).total_seconds()) < 60
    assert abs((sydney - expected_sydney).total_seconds()) < 60


def test_now_at_location_none_matches_machine_local_time():
    result = _now_at_location(None)
    expected = datetime.now().replace(second=0, microsecond=0)

    assert abs((result - expected).total_seconds()) < 60
