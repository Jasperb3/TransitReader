"""
Computed Timing Table Module

Scans daily Immanuel charts over a date window to detect real,
calculable timing events (aspect exactness, stations, sign ingresses,
lunations) instead of leaving "key dates" to LLM guesswork.
"""

import json
from datetime import datetime, timedelta

from immanuel import charts
from immanuel.classes.serialize import ToJSON

MAJOR_ASPECTS = {"Conjunction", "Opposition", "Square", "Trine", "Sextile"}

# Exactness dates are only tracked for these transiting bodies -- inner
# planets (Sun-Venus) move too fast for daily-resolution detection to be
# meaningful.
EXACTNESS_TRANSITING_IDS = {
    "4000006",  # Mars
    "4000007",  # Jupiter
    "4000008",  # Saturn
    "4000009",  # Uranus
    "4000010",  # Neptune
    "4000011",  # Pluto
    "5000001",  # Chiron
}

TRACKED_PLANET_NAMES = {
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
}


def _serialize_chart(chart_obj) -> dict:
    return json.loads(json.dumps(chart_obj, cls=ToJSON))


def _detect_aspect_exactness(snapshots: list) -> list:
    events = []
    prev_diffs = {}

    for day_dt, data in snapshots:
        objects = data.get("objects", {})
        for active_id, passives in data.get("aspects", {}).items():
            if active_id not in EXACTNESS_TRANSITING_IDS:
                continue
            for passive_id, details in passives.items():
                aspect_type = details.get("type")
                if aspect_type not in MAJOR_ASPECTS:
                    continue
                diff = details.get("difference", {}).get("raw")
                if diff is None:
                    continue

                key = (active_id, passive_id, aspect_type)
                if key in prev_diffs:
                    prev_date, prev_diff = prev_diffs[key]
                    if prev_diff != 0 and diff != 0 and (prev_diff > 0) != (diff > 0):
                        exact_date = prev_date if abs(prev_diff) < abs(diff) else day_dt
                        active_name = objects.get(active_id, {}).get("name", active_id)
                        passive_name = objects.get(passive_id, {}).get("name", passive_id)
                        events.append(
                            (exact_date, f"Transiting {active_name} {aspect_type} natal {passive_name} exact")
                        )
                prev_diffs[key] = (day_dt, diff)

    return events


def _detect_stations(snapshots: list) -> list:
    events = []
    prev_speeds = {}

    for day_dt, data in snapshots:
        for obj_id, obj in data.get("objects", {}).items():
            name = obj.get("name")
            if name not in TRACKED_PLANET_NAMES:
                continue
            speed = obj.get("speed")
            if speed is None:
                continue

            if obj_id in prev_speeds:
                prev_date, prev_speed = prev_speeds[obj_id]
                if prev_speed != 0 and speed != 0 and (prev_speed > 0) != (speed > 0):
                    station_type = "Station Retrograde" if speed < 0 else "Station Direct"
                    exact_date = prev_date if abs(prev_speed) < abs(speed) else day_dt
                    events.append((exact_date, f"{name} {station_type}"))
            prev_speeds[obj_id] = (day_dt, speed)

    return events


def _detect_ingresses(snapshots: list) -> list:
    events = []
    prev_signs = {}

    for day_dt, data in snapshots:
        for obj_id, obj in data.get("objects", {}).items():
            name = obj.get("name")
            if name not in TRACKED_PLANET_NAMES:
                continue
            sign_info = obj.get("sign", {})
            sign_number = sign_info.get("number")
            sign_name = sign_info.get("name")

            if obj_id in prev_signs and prev_signs[obj_id] != sign_number:
                events.append((day_dt, f"{name} ingresses into {sign_name}"))
            prev_signs[obj_id] = sign_number

    return events


def _detect_lunations(snapshots: list) -> list:
    events = []
    prev_elongation = None

    for day_dt, data in snapshots:
        objects = data.get("objects", {})
        sun = next((o for o in objects.values() if o.get("name") == "Sun"), None)
        moon = next((o for o in objects.values() if o.get("name") == "Moon"), None)
        if sun is None or moon is None:
            continue

        sun_lon = sun.get("longitude", {}).get("raw")
        moon_lon = moon.get("longitude", {}).get("raw")
        if sun_lon is None or moon_lon is None:
            continue

        elongation = (moon_lon - sun_lon) % 360

        if prev_elongation is not None:
            if prev_elongation > 350 and elongation < 10:
                events.append((day_dt, "New Moon"))
            if prev_elongation < 180 <= elongation:
                events.append((day_dt, "Full Moon"))

        prev_elongation = elongation

    return events


def build_timing_table(
    natal_dob: datetime,
    natal_lat: float,
    natal_lon: float,
    transit_lat: float,
    transit_lon: float,
    transit_datetime: datetime,
    days_ahead: int = 90,
    days_back: int = 7,
) -> str:
    """
    Scan daily transit-to-natal charts across a date window and return a
    markdown block of dated, computed timing events.

    Args:
        natal_dob: Subject's date of birth
        natal_lat: Birthplace latitude
        natal_lon: Birthplace longitude
        transit_lat: Transit location latitude
        transit_lon: Transit location longitude
        transit_datetime: Center point of the scan window (the "current" transit moment)
        days_ahead: Days forward from transit_datetime to scan
        days_back: Days backward from transit_datetime to scan

    Returns:
        str: Markdown block titled "--- Verified Timing Table (computed) ---"
            with one dated line per detected event.
    """
    natal_subject = charts.Subject(natal_dob, natal_lat, natal_lon)
    natal_chart = charts.Natal(natal_subject)

    start_day = (transit_datetime - timedelta(days=days_back)).replace(
        hour=12, minute=0, second=0, microsecond=0
    )
    total_days = days_back + days_ahead + 1

    snapshots = []
    for offset in range(total_days):
        day_dt = start_day + timedelta(days=offset)
        day_subject = charts.Subject(day_dt, transit_lat, transit_lon)
        day_chart = charts.Natal(day_subject, aspects_to=natal_chart)
        snapshots.append((day_dt, _serialize_chart(day_chart)))

    events = []
    events.extend(_detect_aspect_exactness(snapshots))
    events.extend(_detect_stations(snapshots))
    events.extend(_detect_ingresses(snapshots))
    events.extend(_detect_lunations(snapshots))
    events.sort(key=lambda e: e[0])

    lines = ["--- Verified Timing Table (computed) ---"]
    lines.append(
        "Exactness dates limited to transiting Mars through Pluto plus Chiron -- "
        "inner planets (Sun through Venus) move too fast for daily-resolution "
        "exactness detection."
    )
    if not events:
        lines.append("(No timing events detected in this window)")
    else:
        for event_date, description in events:
            lines.append(f"* {event_date.strftime('%Y-%m-%d')}: {description}")

    return "\n".join(lines)
