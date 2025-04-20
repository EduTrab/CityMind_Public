import streamlit as st
import requests


def resolve_city_to_coordinates(city_name):
    if not city_name:
        return None
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": city_name,
        "key": st.secrets.get("google_maps_api_key", "")
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    data = response.json()
    if data.get("results"):
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    return None




def geocode_city_to_candidates(city_name: str) -> list[dict]:
    """
    Query Google’s Geocoding API and return a list of matching
    { description, lat, lng } for the given city_name.
    """
    if not city_name:
        return []

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": city_name,
        "key": st.secrets.get("google_maps_api_key", "")
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return []

    data = resp.json().get("results", [])
    candidates = []
    for r in data:
        desc = r.get("formatted_address")
        loc = r.get("geometry", {}).get("location", {})
        if desc and "lat" in loc and "lng" in loc:
            candidates.append({
                "description": desc,
                "lat": loc["lat"],
                "lng": loc["lng"]
            })
    return candidates

