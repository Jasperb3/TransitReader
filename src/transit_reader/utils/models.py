from pydantic import BaseModel, Field
from datetime import datetime
from transit_reader.utils.subject_selection import get_subject_data
from transit_reader.utils.transit_selection import get_transit_parameters
from transit_reader.utils.constants import TODAY


class TransitState(BaseModel):
    # Subject identification
    name: str
    email: str

    # Birth data
    date_of_birth: datetime
    dob: str
    birthplace: str
    birthplace_city: str
    birthplace_country: str
    birthplace_latitude: float
    birthplace_longitude: float
    birthplace_timezone: str

    # Transit analysis parameters
    today: str  # Report generation date (always current)
    transit_datetime: datetime  # Can be current or custom
    transit_date_formatted: str  # Formatted transit date for display
    current_location: str
    current_location_city: str
    current_location_country: str
    current_location_latitude: float
    current_location_longitude: float
    current_location_timezone: str
    is_custom_transit: bool = False  # Flag to indicate custom parameters

    # Analysis outputs
    current_transits: str = ""
    transit_analysis: str = ""
    natal_chart: str = ""
    natal_analysis: str = ""
    transit_to_natal_chart: str = ""
    transit_to_natal_analysis: str = ""
    kerykeion_transit_chart: str = ""
    report_markdown: str = ""
    report_pdf: str = ""


def create_transit_state() -> TransitState:
    """
    Factory function to create a TransitState instance with user-provided data.

    This function:
    1. Prompts for subject data (or loads existing)
    2. Prompts for transit parameters (current or custom time/location)
    3. Returns a fully initialized TransitState object

    Returns:
        TransitState: Initialized state object ready for flow execution
    """
    # Get subject data
    subject_data = get_subject_data()

    if not subject_data:
        raise ValueError("Failed to load or create subject data. Cannot proceed.")

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

    # Extract transit location
    transit_location = transit_params["location"]

    # Parse birth datetime
    birth_dt = datetime.strptime(subject_data["date_of_birth"], "%Y-%m-%d %H:%M:%S")

    # Create TransitState instance
    state = TransitState(
        # Subject data
        name=subject_data["name"],
        email=subject_data.get("email", ""),

        # Birth data
        date_of_birth=birth_dt,
        dob=subject_data["date_of_birth"],
        birthplace=f"{subject_data['birthplace']['place']}, {subject_data['birthplace']['country']}",
        birthplace_city=subject_data["birthplace"]["place"],
        birthplace_country=subject_data["birthplace"]["country"],
        birthplace_latitude=subject_data["birthplace"]["latitude"],
        birthplace_longitude=subject_data["birthplace"]["longitude"],
        birthplace_timezone=subject_data["birthplace"]["timezone"],

        # Transit parameters
        today=TODAY,
        transit_datetime=transit_params["transit_datetime"],
        transit_date_formatted=transit_params["transit_datetime"].strftime("%A, %d %B %Y at %H:%M"),
        current_location=f"{transit_location['city']}, {transit_location['country']}",
        current_location_city=transit_location["city"],
        current_location_country=transit_location["country"],
        current_location_latitude=transit_location["latitude"],
        current_location_longitude=transit_location["longitude"],
        current_location_timezone=transit_location["timezone"],
        is_custom_transit=transit_params["is_custom"]
    )

    return state


class Email(BaseModel):
    subject: str = Field(description="The subject of the email.")
    body: str = Field(description="The body of the email.")
