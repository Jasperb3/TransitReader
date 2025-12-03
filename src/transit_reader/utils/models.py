from pydantic import BaseModel, Field
from datetime import datetime
from transit_reader.utils.subject_selection import get_subject_data
from transit_reader.utils.transit_selection import get_transit_parameters, get_appendices_preference
from transit_reader.utils.biographical_questionnaire import format_biographical_context_for_prompt
from transit_reader.utils.constants import TODAY

# Get subject data at module load
subject_data = get_subject_data()

# Prepare current location from subject data (defaults to birthplace if no current_location)
if "current_location" in subject_data:
    current_loc = {
        "city": subject_data["current_location"]["place"],
        "country": subject_data["current_location"]["country"],
        "latitude": subject_data["current_location"]["latitude"],
        "longitude": subject_data["current_location"]["longitude"],
        "timezone": subject_data["current_location"]["timezone"]
    }
else:
    # Default to birthplace if no current location specified
    current_loc = {
        "city": subject_data["birthplace"]["place"],
        "country": subject_data["birthplace"]["country"],
        "latitude": subject_data["birthplace"]["latitude"],
        "longitude": subject_data["birthplace"]["longitude"],
        "timezone": subject_data["birthplace"]["timezone"]
    }

# Get transit parameters (interactive prompts)
transit_params = get_transit_parameters(subject_data, current_loc)
transit_location = transit_params["location"]

# Ask user about appendices preference
include_appendices = get_appendices_preference()


class TransitState(BaseModel):
    # Subject identification
    name: str = subject_data["name"]
    email: str = subject_data.get("email", "")

    # Birth data
    date_of_birth: datetime = datetime.strptime(subject_data["date_of_birth"], "%Y-%m-%d %H:%M:%S")
    dob: str = subject_data["date_of_birth"]
    birthplace: str = f"{subject_data['birthplace']['place']}, {subject_data['birthplace']['country']}"
    birthplace_city: str = subject_data["birthplace"]["place"]
    birthplace_country: str = subject_data["birthplace"]["country"]
    birthplace_latitude: float = subject_data["birthplace"]["latitude"]
    birthplace_longitude: float = subject_data["birthplace"]["longitude"]
    birthplace_timezone: str = subject_data["birthplace"]["timezone"]

    # Transit analysis parameters
    today: str = TODAY
    transit_datetime: datetime = transit_params["transit_datetime"]
    transit_date_formatted: str = transit_params["transit_datetime"].strftime("%A, %d %B %Y at %H:%M")
    current_location: str = f"{transit_location['city']}, {transit_location['country']}"
    current_location_city: str = transit_location["city"]
    current_location_country: str = transit_location["country"]
    current_location_latitude: float = transit_location["latitude"]
    current_location_longitude: float = transit_location["longitude"]
    current_location_timezone: str = transit_location["timezone"]
    is_custom_transit: bool = transit_params["is_custom"]
    include_appendices: bool = include_appendices  # Whether to generate detailed chart appendices

    # Biographical context
    biographical_context_raw: dict = subject_data.get("biographical_context", {})
    biographical_context: str = format_biographical_context_for_prompt(subject_data.get("biographical_context", {}))

    # Analysis outputs
    current_transits: str = ""
    transit_analysis: str = ""
    natal_chart: str = ""
    natal_analysis: str = ""
    transit_to_natal_chart: str = ""
    transit_to_natal_analysis: str = ""
    chart_appendices: str = ""  # Combined appendices from all three chart analyses
    kerykeion_transit_chart: str = ""
    report_markdown: str = ""
    report_pdf: str = ""




class Email(BaseModel):
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The body of the email.")
