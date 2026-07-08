from pydantic import BaseModel, Field
from datetime import datetime
from transit_reader.utils.subject_selection import get_subject_data
from transit_reader.utils.transit_selection import get_transit_parameters, get_appendices_preference
from transit_reader.utils.biographical_questionnaire import format_biographical_context_for_prompt
from transit_reader.utils.constants import TODAY


class TransitState(BaseModel):
    # Subject identification
    name: str = ""
    email: str = ""

    # Birth data
    date_of_birth: datetime = datetime(1970, 1, 1)
    dob: str = ""
    birthplace: str = ""
    birthplace_city: str = ""
    birthplace_country: str = ""
    birthplace_latitude: float = 0.0
    birthplace_longitude: float = 0.0
    birthplace_timezone: str = ""

    # Transit analysis parameters
    today: str = ""
    transit_datetime: datetime = datetime(1970, 1, 1)
    transit_date_formatted: str = ""
    current_location: str = ""
    current_location_city: str = ""
    current_location_country: str = ""
    current_location_latitude: float = 0.0
    current_location_longitude: float = 0.0
    current_location_timezone: str = ""
    is_custom_transit: bool = False
    include_appendices: bool = True  # Whether to generate detailed chart appendices

    # Biographical context
    biographical_context_raw: dict = Field(default_factory=dict)
    biographical_context: str = ""

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


def create_transit_state() -> TransitState:
    """
    Interactively gather subject, transit, and appendices preferences and
    build the initial TransitState for the flow.

    Returns:
        TransitState: Populated initial state
    """
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

    return TransitState(
        name=subject_data["name"],
        email=subject_data.get("email", ""),
        date_of_birth=datetime.strptime(subject_data["date_of_birth"], "%Y-%m-%d %H:%M:%S"),
        dob=subject_data["date_of_birth"],
        birthplace=f"{subject_data['birthplace']['place']}, {subject_data['birthplace']['country']}",
        birthplace_city=subject_data["birthplace"]["place"],
        birthplace_country=subject_data["birthplace"]["country"],
        birthplace_latitude=subject_data["birthplace"]["latitude"],
        birthplace_longitude=subject_data["birthplace"]["longitude"],
        birthplace_timezone=subject_data["birthplace"]["timezone"],
        today=TODAY,
        transit_datetime=transit_params["transit_datetime"],
        transit_date_formatted=transit_params["transit_datetime"].strftime("%A, %d %B %Y at %H:%M"),
        current_location=f"{transit_location['city']}, {transit_location['country']}",
        current_location_city=transit_location["city"],
        current_location_country=transit_location["country"],
        current_location_latitude=transit_location["latitude"],
        current_location_longitude=transit_location["longitude"],
        current_location_timezone=transit_location["timezone"],
        is_custom_transit=transit_params["is_custom"],
        include_appendices=include_appendices,
        biographical_context_raw=subject_data.get("biographical_context", {}),
        biographical_context=format_biographical_context_for_prompt(subject_data.get("biographical_context", {})),
    )


class Email(BaseModel):
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The body of the email.")
