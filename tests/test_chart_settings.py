from immanuel.const import chart
from immanuel.setup import settings

from transit_reader.utils.chart_settings import configure_immanuel


def test_configure_immanuel_is_idempotent():
    configure_immanuel()
    configure_immanuel()

    for object_name in ("TRUE_NORTH_NODE", "TRUE_SOUTH_NODE", "LILITH"):
        object_const = getattr(chart, object_name)
        assert settings.objects.count(object_const) == 1
