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





def geocode_city_to_candidates(city_name):
    """
    Queries Google’s Geocoding API for all matches to `city_name`.
    Returns a list of dicts:
      [{ "description": formatted_address, "lat": ..., "lng": ... }, …]
    """
    if not city_name:
        return []

    api_key = st.secrets.get("google_maps_api_key", "")
    if not api_key:
        st.error("⚠️ Missing Google Maps API key – please add it to secrets.")
        return []

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": city_name, "key": api_key}
    try:
        resp = requests.get(url, params=params, timeout=5).json()
    except Exception as e:
        st.error(f"❌ Geocoding request failed: {e}")
        return []

    results = resp.get("results", [])
    candidates = []
    for r in results:
        loc = r["geometry"]["location"]
        candidates.append({
            "description": r.get("formatted_address", city_name),
            "lat": loc["lat"],
            "lng": loc["lng"]
        })
    return candidates
