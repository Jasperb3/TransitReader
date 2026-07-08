from datetime import datetime

from transit_reader.utils.immanuel_natal_to_transit_chart import (
    _find_natal_house,
    get_transit_natal_aspects,
)


def _synthetic_cusps():
    # House 1 starts at 20°, houses 2-11 evenly spaced, house 12 starts at 350° (wraps to house 1 at 20°)
    cusps = [20.0]
    for i in range(1, 11):
        cusps.append((20.0 + i * 30) % 360)
    cusps.append(350.0)
    return cusps


def test_find_natal_house_normal_case():
    cusps = _synthetic_cusps()
    # 35 degrees falls within house 1 (20-50)
    assert _find_natal_house(35.0, cusps) == 1


def test_find_natal_house_wrap_around():
    cusps = _synthetic_cusps()
    # cusp12 (index 11) = 350°, cusp1 (index 0) = 20° -> house 12 wraps across 0°/360°
    assert cusps[11] == 350.0
    assert cusps[0] == 20.0
    assert _find_natal_house(5.0, cusps) == 12


def test_get_transit_natal_aspects_includes_natal_house_sections(fixture_subject):
    result = get_transit_natal_aspects(
        fixture_subject["latitude"],
        fixture_subject["longitude"],
        fixture_subject["date_of_birth"],
        fixture_subject["latitude"],
        fixture_subject["longitude"],
        datetime(2025, 1, 1, 12, 0),
    )

    assert "--- Transiting Planets in NATAL Houses ---" in result
    assert "--- NATAL House Cusps ---" in result
    assert "--- Aspects ---" in result
