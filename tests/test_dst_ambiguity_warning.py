from datetime import datetime

from transit_reader.utils.immanuel_natal_chart import get_natal_chart
from transit_reader.utils.immanuel_natal_to_transit_chart import get_transit_natal_aspects

AMBIGUOUS_DOB = datetime(2024, 10, 27, 1, 30)


def test_get_natal_chart_warns_on_ambiguous_dst(capsys):
    get_natal_chart(AMBIGUOUS_DOB, 51.5074, -0.1278)

    captured = capsys.readouterr()
    assert "DST fall-back hour" in captured.out


def test_get_transit_natal_aspects_warns_on_ambiguous_dst(capsys):
    get_transit_natal_aspects(
        51.5074, -0.1278,
        AMBIGUOUS_DOB,
        51.5074, -0.1278,
        datetime(2025, 1, 1, 12, 0),
    )

    captured = capsys.readouterr()
    assert "DST fall-back hour" in captured.out
