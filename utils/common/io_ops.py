import os
import json
import shutil
import streamlit as st

from configs.config import ANSWERED_DIR, SAVE_DIRS
from utils.common.drive_upload import upload_file


def save_and_move_image(record):
    """
    Saves the user's answers and metadata for the image by updating its JSON file.
    Moves the image and JSON file to the ANSWERED_DIR.
    Deletes duplicate copies from other save folders.
    """
    image_path = record["image_path"]
    json_path = record["json_path"]

    # ⛔️ Defensive check: don't crash if file was deleted
    if not os.path.exists(image_path):
        print(f"[Warning] Image not found, skipping save: {image_path}")
        return
    if not os.path.exists(json_path):
        print(f"[Warning] JSON not found, skipping save: {json_path}")
        return

    qmode = record["question_mode"]

    # Load existing metadata from JSON file
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Append MCQA data
    data["mc_question"] = record.get("mc_question", "")
    data["mc_options"]  = record.get("mc_options", {})
    data["mc_correct"]  = record.get("mc_correct", "?")
    data["mc_reason"]   = record.get("mc_reason", "")
    data["user_choice"] = record.get("user_choice", None)
    data["question_mode"] = "llm_mcqa"

    # Save updated JSON to answered folder
    answered_json_path = os.path.join(ANSWERED_DIR, os.path.basename(json_path))
    with open(answered_json_path, 'w') as f:
        json.dump(data, f, indent=4)

    # Move image to answered folder
    answered_image_path = os.path.join(ANSWERED_DIR, os.path.basename(image_path))
    shutil.move(image_path, answered_image_path)

    # ✅ Upload to Google Drive
    user_id = st.session_state.get("session_id", "unknown")
    print(f"[DRIVE SAVE] Saving as user_id: {user_id}")
    try:
        upload_file(answered_image_path, os.path.basename(answered_image_path), user_id)
        upload_file(answered_json_path, os.path.basename(answered_json_path), user_id)
        st.success(f"✅ Uploaded to Drive for user `{user_id}`")
    except Exception as e:
        st.warning(f"⚠️ Failed to upload to Drive: {e}")


    # ✅ Cleanup all matching files (img + json) from SAVE_DIRS
    for folder in SAVE_DIRS:
        alt_img = os.path.join(folder, os.path.basename(image_path))
        alt_json = os.path.join(folder, os.path.basename(json_path))
        for p in [alt_img, alt_json]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                    print(f"[Cleanup] Removed duplicate: {p}")
                except Exception as e:
                    print(f"[Warning] Could not delete {p}: {e}")
