import os
import streamlit as st


# Google Maps API Key
MAPS_API_KEY = st.secrets.get("google_maps_api_key", "")
print("✅ [DEBUG] MAPS_API_KEY loaded:", MAPS_API_KEY)  # <- ADD THIS

if not MAPS_API_KEY:
    st.warning("⚠️ Google Maps API Key is missing. City Dataset will not work.")




# Local storage directories
SAVE_DIR = "./data/saved_images/"
ANSWERED_DIR = "./data/answered_images/"
LOCAL_SAVE_FOLDER = "./data/saved_Local_images/"  
SAVE_DIRS = ["./static/images", SAVE_DIR, LOCAL_SAVE_FOLDER]

# Ensure all required folders exist
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(ANSWERED_DIR, exist_ok=True)
os.makedirs(LOCAL_SAVE_FOLDER, exist_ok=True)

# Batch-create any other save dirs
for folder in SAVE_DIRS:
    os.makedirs(folder, exist_ok=True)