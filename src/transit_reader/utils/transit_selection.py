"""
Transit Time and Location Selection Module

Provides interactive prompts for selecting transit analysis parameters.
Allows users to choose between current date/time/location or custom values.
"""

import os
import googlemaps
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

gmaps = googlemaps.Client(key=os.getenv("GMAPS_API_KEY"))


def get_transit_datetime() -> datetime:
    """
    Prompt user for custom transit date and time.

    Returns:
        datetime: Custom datetime object for transit analysis
    """
    print(f"\n{BLUE}--- Enter Custom Transit Date and Time ---{RESET}")

    # Get date
    while True:
        try:
            year = int(input("Enter the year: "))
            if year < 1900 or year > 2100:
                raise ValueError
            break
        except ValueError:
            print(f"{RED}Invalid year. Please enter a valid year between 1900 and 2100.{RESET}")

    while True:
        try:
            month = int(input("Enter the month (1-12): "))
            if month < 1 or month > 12:
                raise ValueError
            break
        except ValueError:
            print(f"{RED}Invalid month. Please enter a valid month between 1 and 12.{RESET}")

    while True:
        try:
            day = int(input("Enter the day (1-31): "))
            # Validate the date
            try:
                datetime(year, month, day)
            except ValueError as e:
                print(f"{RED}Invalid day: {e}. Please enter a valid day.{RESET}")
                continue
            break
        except ValueError:
            print(f"{RED}Invalid input. Please enter a number for the day.{RESET}")

    # Get time
    while True:
        try:
            time = input("Enter the time in 24-hour format (e.g. 15:30 for 3:30pm): ")
            hour, minute = map(int, time.split(':'))
            if hour < 0 or hour > 23:
                raise ValueError("Hour must be between 0 and 23")
            if minute < 0 or minute > 59:
                raise ValueError("Minute must be between 0 and 59")
            break
        except ValueError as e:
            print(f"{RED}Invalid time. {e}. Please enter a valid time in 24-hour format (e.g. 15:30).{RESET}")

    transit_dt = datetime(year, month, day, hour, minute)
    print(f"{GREEN}Transit date/time set to: {transit_dt.strftime('%Y-%m-%d %H:%M')}{RESET}")

    return transit_dt


def get_timezone(latitude: float, longitude: float, timestamp: datetime = None) -> str:
    """
    Get timezone for given coordinates and timestamp.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        timestamp: Optional datetime for timezone lookup (defaults to now)

    Returns:
        str: Timezone string (e.g., 'America/New_York') or None if lookup fails
    """
    if timestamp is None:
        timestamp = datetime.now()

    timestamp_unix = timestamp.timestamp()

    try:
        timezone_result = gmaps.timezone((latitude, longitude), timestamp=timestamp_unix)
        if timezone_result and 'timeZoneId' in timezone_result:
            timezone_str = timezone_result['timeZoneId']
            return timezone_str
        else:
            print(f"{YELLOW}Warning: Could not determine timezone via Google API.{RESET}")
            return None
    except Exception as e:
        print(f"{RED}Error getting timezone from Google API: {e}{RESET}")
        return None


def get_transit_location(timestamp: datetime = None) -> dict:
    """
    Prompt user for custom transit location with geocoding.

    Args:
        timestamp: Optional datetime for timezone lookup

    Returns:
        dict: Location data with keys: city, country, latitude, longitude, timezone
    """
    print(f"\n{BLUE}--- Enter Custom Transit Location ---{RESET}")

    while True:
        try:
            address = input("Enter the location (city, state/country): ")
            geocode_result = gmaps.geocode(address)

            if not geocode_result:
                print(f"{RED}Invalid address. Could not geocode. Please enter a valid address.{RESET}")
                continue

            # Validate geocode result structure
            if not isinstance(geocode_result, list) or len(geocode_result) == 0:
                print(f"{RED}Unexpected geocode result format. Please try again.{RESET}")
                continue

            location = geocode_result[0].get('geometry', {}).get('location', {})
            if not location or 'lat' not in location or 'lng' not in location:
                print(f"{RED}Could not get coordinates for this address. Please try again.{RESET}")
                continue

            # Extract city and country from address components
            address_components = geocode_result[0].get('address_components', [])
            city = next((comp['long_name'] for comp in address_components if 'locality' in comp['types']), None)
            country = next((comp['long_name'] for comp in address_components if 'country' in comp['types']), None)

            # Fallback for city
            if not city:
                city = next((comp['long_name'] for comp in address_components if 'administrative_area_level_1' in comp['types']), None)
                if not city:
                    city = geocode_result[0].get('formatted_address', address)

            # Fallback for country
            if not country:
                country = "Unknown"

            lat = location['lat']
            lon = location['lng']

            # Get timezone for this location
            timezone = get_timezone(lat, lon, timestamp)

            formatted_address = geocode_result[0].get('formatted_address', address)
            print(f"{GREEN}Location set to: {formatted_address}{RESET}")
            print(f"{GREEN}Coordinates: {lat:.4f}, {lon:.4f}{RESET}")
            if timezone:
                print(f"{GREEN}Timezone: {timezone}{RESET}")

            return {
                "city": city,
                "country": country,
                "latitude": lat,
                "longitude": lon,
                "timezone": timezone
            }

        except googlemaps.exceptions.ApiError as e:
            print(f"{RED}Google Maps API Error: {e}. Check API key and usage limits.{RESET}")
        except Exception as e:
            print(f"{RED}Error processing location: {e}. Please try again.{RESET}")


def get_transit_parameters(subject_data: dict, current_location: dict = None) -> dict:
    """
    Main interactive function for transit time/location selection.

    Presents user with 4 options:
    1. Use current date/time and saved location (DEFAULT)
    2. Custom date/time only (keep saved location)
    3. Custom location only (use current date/time)
    4. Both custom date/time AND custom location

    Args:
        subject_data: Subject data dictionary containing birthplace info
        current_location: Optional current location override (defaults to birthplace)

    Returns:
        dict: Transit parameters with keys:
            - transit_datetime: datetime object
            - location: dict with city, country, latitude, longitude, timezone
            - is_custom: bool indicating if custom parameters were used
    """
    # Default to birthplace if no current location specified
    if current_location is None:
        current_location = {
            "city": subject_data.get("birthplace", {}).get("place", "Unknown"),
            "country": subject_data.get("birthplace", {}).get("country", "Unknown"),
            "latitude": subject_data.get("birthplace", {}).get("latitude"),
            "longitude": subject_data.get("birthplace", {}).get("longitude"),
            "timezone": subject_data.get("birthplace", {}).get("timezone")
        }

    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}Transit Analysis Options{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"  {BLUE}[1]{RESET} Use current date/time and saved location {YELLOW}(DEFAULT){RESET}")
    print(f"      Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"      Location: {current_location['city']}, {current_location['country']}")
    print(f"\n  {BLUE}[2]{RESET} Specify custom date/time {YELLOW}(keep saved location){RESET}")
    print(f"      Location: {current_location['city']}, {current_location['country']}")
    print(f"\n  {BLUE}[3]{RESET} Specify custom location {YELLOW}(use current date/time){RESET}")
    print(f"      Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"\n  {BLUE}[4]{RESET} Specify both custom date/time AND custom location")
    print(f"{GREEN}{'='*60}{RESET}\n")

    # Get user choice
    while True:
        choice = input(f"Enter your choice {BLUE}[1-4]{RESET} (press Enter for default): ").strip()

        # Default to option 1
        if choice == "":
            choice = "1"

        if choice in ["1", "2", "3", "4"]:
            break
        else:
            print(f"{RED}Invalid choice. Please enter 1, 2, 3, or 4.{RESET}")

    # Process choice
    transit_dt = None
    transit_location = None
    is_custom = False

    if choice == "1":
        # Use current date/time and saved location
        transit_dt = datetime.now()
        transit_location = current_location
        print(f"\n{GREEN}Using current date/time and saved location{RESET}")

    elif choice == "2":
        # Custom date/time, saved location
        transit_dt = get_transit_datetime()
        transit_location = current_location
        is_custom = True
        print(f"\n{GREEN}Using custom date/time with saved location{RESET}")

    elif choice == "3":
        # Saved date/time, custom location
        transit_dt = datetime.now()
        transit_location = get_transit_location(transit_dt)
        is_custom = True
        print(f"\n{GREEN}Using current date/time with custom location{RESET}")

    elif choice == "4":
        # Both custom
        transit_dt = get_transit_datetime()
        transit_location = get_transit_location(transit_dt)
        is_custom = True
        print(f"\n{GREEN}Using custom date/time and custom location{RESET}")

    # Validation
    if transit_location is None or transit_location.get('latitude') is None or transit_location.get('longitude') is None:
        print(f"{RED}Error: Invalid location data. Falling back to current settings.{RESET}")
        transit_dt = datetime.now()
        transit_location = current_location
        is_custom = False

    # Summary
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}Transit Analysis Parameters{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    print(f"  Date/Time: {transit_dt.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Location: {transit_location['city']}, {transit_location['country']}")
    print(f"  Coordinates: {transit_location['latitude']:.4f}, {transit_location['longitude']:.4f}")
    if transit_location['timezone']:
        print(f"  Timezone: {transit_location['timezone']}")
    print(f"{GREEN}{'='*60}{RESET}\n")

    return {
        "transit_datetime": transit_dt,
        "location": transit_location,
        "is_custom": is_custom
    }


if __name__ == "__main__":
    # Test the module with dummy subject data
    test_subject = {
        "name": "Test Subject",
        "birthplace": {
            "place": "New York",
            "country": "USA",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York"
        }
    }

    print("Testing transit_selection module...")
    transit_params = get_transit_parameters(test_subject)

    print("\n=== Results ===")
    print(f"Transit DateTime: {transit_params['transit_datetime']}")
    print(f"Location: {transit_params['location']}")
    print(f"Is Custom: {transit_params['is_custom']}")
