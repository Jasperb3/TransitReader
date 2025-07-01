from pydantic import BaseModel, Field
from datetime import datetime
from transit_reader.utils.subject_selection import get_subject_data
from transit_reader.utils.constants import TODAY

subject_data = get_subject_data()

class TransitState(BaseModel):
    name: str = subject_data["name"]
    email: str = subject_data["email"]
    date_of_birth: datetime = datetime.strptime(subject_data["date_of_birth"], "%Y-%m-%d %H:%M:%S")
    dob: str = subject_data["date_of_birth"]
    birthplace: str = f"{subject_data['birthplace']['place']}, {subject_data['birthplace']['country']}"
    birthplace_city: str = subject_data["birthplace"]["place"]
    birthplace_country: str = subject_data["birthplace"]["country"]
    birthplace_latitude: float = subject_data["birthplace"]["latitude"]
    birthplace_longitude: float = subject_data["birthplace"]["longitude"]
    birthplace_timezone: str = subject_data["birthplace"]["timezone"]
    today: str = TODAY
    current_location: str = f"{subject_data['current_location']['place']}, {subject_data['current_location']['country']}"
    current_location_city: str = subject_data["current_location"]["place"]
    current_location_country: str = subject_data["current_location"]["country"]
    current_location_latitude: float = subject_data["current_location"]["latitude"]
    current_location_longitude: float = subject_data["current_location"]["longitude"]
    current_location_timezone: str = subject_data["current_location"]["timezone"]
    current_transits: str = ""
    transit_analysis: str = ""
    natal_chart: str = ""
    natal_analysis: str = ""
    transit_to_natal_chart: str = ""
    transit_to_natal_analysis: str = ""
    kerykeion_transit_chart: str = ""
    report_markdown: str = ""
    report_pdf: str = ""


class Email(BaseModel):
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The body of the email.")
