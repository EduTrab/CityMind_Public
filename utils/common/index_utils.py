import os
import random
import streamlit as st

from configs.config import SAVE_DIR, ANSWERED_DIR
from data.cities_coordinates import city_coordinates


def get_next_idx():
    """
    Returns the next numeric index for naming new Street View files.
    Ignores local image files that include non-numeric names.
    """
    existing_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.png')]
    answered_files = [f for f in os.listdir(ANSWERED_DIR) if f.endswith('.png')]
    all_files = existing_files + answered_files

    indices = []
    for f in all_files:
        base = os.path.splitext(f)[0]
        if base.isdigit():
            indices.append(int(base))
    return max(indices, default=-1) + 1



def random_location(fallback_coords=None):
    """
    Returns a random lat/lon around either:
    - fallback_coords (if provided)
    - st.session_state.city_latlon (if set and visible)
    - a random city from city_coordinates
    """
    if fallback_coords:
        base_lat, base_lon = fallback_coords
    elif "city_latlon" in st.session_state and st.session_state.city_latlon:
        base_lat, base_lon = st.session_state.city_latlon
    else:
        base_lat, base_lon = random.choice(city_coordinates)

    perturb_lat = random.uniform(-0.01, 0.01)
    perturb_lon = random.uniform(-0.01, 0.01)
    return base_lat + perturb_lat, base_lon + perturb_lon
