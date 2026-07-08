from datetime import datetime

from transit_reader.utils.transit_timing import _detect_lunations, build_timing_table


def test_build_timing_table_returns_header_and_events(fixture_subject):
    result = build_timing_table(
        fixture_subject["date_of_birth"],
        fixture_subject["latitude"],
        fixture_subject["longitude"],
        fixture_subject["latitude"],
        fixture_subject["longitude"],
        datetime(2025, 1, 1, 12, 0),
        days_ahead=30,
        days_back=0,
    )

    assert "--- Verified Timing Table (computed) ---" in result
    lines = [line for line in result.splitlines() if line.startswith("* ")]
    assert len(lines) >= 1


def test_detect_lunations_synthetic_zero_crossing():
    day1 = datetime(2025, 1, 1)
    day2 = datetime(2025, 1, 2)

    snapshots = [
        (day1, {"objects": {"1": {"name": "Sun", "longitude": {"raw": 0.0}}, "2": {"name": "Moon", "longitude": {"raw": 355.0}}}}),
        (day2, {"objects": {"1": {"name": "Sun", "longitude": {"raw": 0.0}}, "2": {"name": "Moon", "longitude": {"raw": 5.0}}}}),
    ]

    events = _detect_lunations(snapshots)

    assert any(desc == "New Moon" for _, desc in events)
