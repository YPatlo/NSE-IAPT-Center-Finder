import os
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Replace YOUR_API_KEY with your actual Google Maps API key
geolocator = GoogleV3(api_key=os.getenv("API_KEY"), timeout=10)

def geocode_address(address: str):
    if not address or address.strip() == "":
        return None
    try:
        location = geolocator.geocode(address)
    except GeocoderTimedOut:
        print(f"Geocoding timed out for address: {address}")
        return None
    except GeocoderServiceError as e:
        print(f"Geocoder service error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

    if location:
        print(f"Found: {location.address}")
        return (location.latitude, location.longitude)
    else:
        print(f"No result found for address: '{address}'")
        return None

