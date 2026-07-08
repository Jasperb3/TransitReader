from datetime import datetime

from transit_reader.utils.immanuel_natal_chart import get_natal_chart
from transit_reader.utils.immanuel_transit_chart import get_transit_chart
from transit_reader.utils.immanuel_natal_to_transit_chart import get_transit_natal_aspects


def test_get_natal_chart_golden_values(fixture_subject):
    result = get_natal_chart(
        fixture_subject["date_of_birth"],
        fixture_subject["latitude"],
        fixture_subject["longitude"],
    )

    assert "--- Natal Chart Summary ---" in result
    assert "* Sun" in result
    assert "Sagittarius" in result

    house_cusp_count = result.count(" Cusp:")
    assert house_cusp_count == 12


def test_get_transit_chart_structure(fixture_subject):
    result = get_transit_chart(
        fixture_subject["latitude"],
        fixture_subject["longitude"],
        datetime(2025, 1, 1, 12, 0),
    )

    assert "--- Transit Chart Summary ---" in result
    assert "House System:" in result


def test_get_transit_natal_aspects_structure(fixture_subject):
    result = get_transit_natal_aspects(
        fixture_subject["latitude"],
        fixture_subject["longitude"],
        fixture_subject["date_of_birth"],
        fixture_subject["latitude"],
        fixture_subject["longitude"],
        datetime(2025, 1, 1, 12, 0),
    )

    assert isinstance(result, str)
    assert "--- Aspects ---" in result
