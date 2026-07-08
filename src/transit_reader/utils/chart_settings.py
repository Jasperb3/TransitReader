"""
Centralized Immanuel Chart Settings

Loads chart_config.yaml and applies it to Immanuel's global settings once,
so the object list and house system are defined in one place instead of
being duplicated (and mutated three times) across the immanuel_*.py modules.
"""

from pathlib import Path

import yaml
from immanuel.const import chart
from immanuel.setup import settings

CHART_CONFIG_PATH = Path(__file__).parent.parent / "config" / "chart_config.yaml"

HOUSE_SYSTEMS = {
    "placidus": chart.PLACIDUS,
    "koch": chart.KOCH,
    "equal": chart.EQUAL,
    "whole_sign": chart.WHOLE_SIGN,
    "vehlow_equal": chart.VEHLOW_EQUAL,
}

# Shared display order for chart formatters. Only includes objects enabled
# by default in chart_config.yaml's extra_objects.
DISPLAY_ORDER = [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn',
    'Uranus', 'Neptune', 'Pluto', 'Chiron', 'True North Node',
    'True South Node', 'Asc', 'MC', 'IC', 'Desc',
]

_configured = False


def configure_immanuel() -> None:
    """
    Apply chart_config.yaml's object list and house system to Immanuel's
    global settings. Idempotent -- repeated calls do not re-append objects.
    """
    global _configured
    if _configured:
        return

    with open(CHART_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    for object_name in config.get("extra_objects", []):
        object_const = getattr(chart, object_name)
        if object_const not in settings.objects:
            settings.objects.append(object_const)

    house_system = config.get("house_system")
    if house_system:
        settings.house_system = HOUSE_SYSTEMS[house_system]

    _configured = True
