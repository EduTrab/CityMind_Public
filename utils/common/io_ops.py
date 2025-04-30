import os
import json
import shutil
import streamlit as st

from configs.config import ANSWERED_DIR, SAVE_DIRS
from utils.common.drive_upload import async_upload_record


def save_and_move_image(record):
    """
    Saves answers to JSON, moves image + JSON to ANSWERED_DIR, and cleans up.
    Drive upload is now handled asynchronously.
    """
    from utils.common.drive_upload import async_upload_record

    image_path = record["image_path"]
    json_path = record["json_path"]

    if not os.path.exists(image_path) or not os.path.exists(json_path):
        print(f"[Warning] Missing image or json: {image_path}, {json_path}")
        return

    # Load & update JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
    data.update({
        "mc_question": record.get("mc_question", ""),
        "mc_options": record.get("mc_options", {}),
        "mc_correct": record.get("mc_correct", "?"),
        "mc_reason": record.get("mc_reason", ""),
        "user_choice": record.get("user_choice", None),
        "question_mode": "llm_mcqa"
    })
    answered_json = os.path.join(ANSWERED_DIR, os.path.basename(json_path))
    with open(answered_json, 'w') as f:
        json.dump(data, f, indent=4)

    # Move image
    answered_img = os.path.join(ANSWERED_DIR, os.path.basename(image_path))
    shutil.move(image_path, answered_img)

    # Async upload
    print(f"[DEBUG] Username: {st.session_state.get('username')}") 
    user_id = st.session_state.get("username", st.session_state.get("session_id", "unknown"))
    async_upload_record({"image_path": answered_img, "json_path": answered_json}, user_id)

    # Local cleanup
    for folder in SAVE_DIRS:
        for path in [os.path.join(folder, os.path.basename(image_path)), os.path.join(folder, os.path.basename(json_path))]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"[Cleanup] Removed duplicate: {path}")
                except Exception as e:
                    print(f"[Warning] Could not delete {path}: {e}")
