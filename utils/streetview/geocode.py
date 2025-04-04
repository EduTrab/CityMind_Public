import requests
from configs.config import MAPS_API_KEY

def resolve_city_to_coordinates(city_name):
    if not city_name:
        return None
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": city_name,
        "key": MAPS_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    data = response.json()
    if data.get("results"):
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    return None
