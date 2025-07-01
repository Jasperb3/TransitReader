import os
import json
from datetime import datetime
from pathlib import Path
from kerykeion import AstrologicalSubject, KerykeionChartSVG
from transit_reader.utils.screenshot_util import capture_svg_screenshot
from transit_reader.utils.constants import CHARTS_DIR

def get_kerykeion_subject(name: str, year: int, month: int, day: int, hour: int, minute: int, city: str, nation: str, longitude: float, latitude: float, timezone: str) -> AstrologicalSubject:
    subject = AstrologicalSubject(
        name,
        year,
        month,
        day,
        hour,
        minute,
        city=city,
        nation=nation,
        lng=longitude,
        lat=latitude,
        tz_str=timezone,
        online=False,
        disable_chiron_and_lilith=False
    )

    return subject

def get_kerykeion_transit_chart(subject: AstrologicalSubject, second_obj: AstrologicalSubject, new_output_directory: str) -> str:
    transit_chart = KerykeionChartSVG(
        subject,
        chart_type='Transit',
        second_obj=second_obj,
        new_output_directory=CHARTS_DIR,
        double_chart_aspect_grid_type='table'
    )

    transits_svg_file_path = f"{new_output_directory}/{subject.name} - Transit Chart.svg"
    transit_chart.makeSVG()
    if not os.path.exists(transits_svg_file_path):
        raise FileNotFoundError(f"SVG generation failed. {transits_svg_file_path} not found.")
    renamed_transits_svg_file_path = transits_svg_file_path.replace(" ", "_")
    os.rename(transits_svg_file_path, renamed_transits_svg_file_path)
    print(f"Renamed SVG file to: {renamed_transits_svg_file_path}")
    transit_chart_png = capture_svg_screenshot(renamed_transits_svg_file_path, new_output_directory)
    renamed_transit_chart_png = f"{new_output_directory}/{subject.name.replace(' ', '_')}_-_Transit_Chart.png"
    os.rename(transit_chart_png, renamed_transit_chart_png)
    print(f"Transit chart saved to: {renamed_transit_chart_png}")

    return renamed_transit_chart_png


if __name__ == "__main__":
    subject_data_file = Path(__file__).parent.parent / "subjects" / "benjamin_jasper.json"
    with open(subject_data_file, "r") as f:
        subject_data = json.load(f)
    
    name = subject_data["name"]
    dob = datetime.strptime(subject_data["date_of_birth"], "%Y-%m-%d %H:%M:%S")
    birth_longitude = subject_data["birthplace"]["longitude"]
    birth_latitude = subject_data["birthplace"]["latitude"]
    birthplace = subject_data["birthplace"]["place"]
    birthplace_country = subject_data["birthplace"]["country"]
    birthplace_timezone = subject_data["birthplace"]["timezone"]
    current_location_longitude = subject_data["current_location"]["longitude"]
    current_location_latitude = subject_data["current_location"]["latitude"]
    current_location = subject_data["current_location"]["place"]
    current_location_country = subject_data["current_location"]["country"]
    current_location_timezone = subject_data["current_location"]["timezone"]
    today = datetime.now()
    
    subject = get_kerykeion_subject(name, dob.year, dob.month, dob.day, dob.hour, dob.minute, birthplace, birthplace_country, birth_longitude, birth_latitude, birthplace_timezone)
    second_obj = get_kerykeion_subject("Here Now", today.year, today.month, today.day, today.hour, today.minute, current_location, current_location_country, current_location_longitude, current_location_latitude, current_location_timezone)
    get_kerykeion_transit_chart(subject, second_obj, str(CHARTS_DIR))
