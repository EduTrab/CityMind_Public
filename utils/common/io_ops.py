import os
import json
import shutil
import streamlit as st

from configs.config import ANSWERED_DIR, SAVE_DIRS
from utils.common.drive_upload import async_upload_record


def save_and_move_image(record):
    from utils.common.drive_upload import async_upload_record

    image_path = record["image_path"]
    json_path = record["json_path"]

    if not os.path.exists(image_path) or not os.path.exists(json_path):
        st.warning(f"⚠️ Missing image or json: {image_path}, {json_path}")
        return

    # Load existing JSON
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

    # ✅ Debug: Confirm what we're saving
    st.write(f"💾 Saving JSON for `{os.path.basename(json_path)}` with `user_choice`: `{data.get('user_choice')}`")

    answered_json = os.path.join(ANSWERED_DIR, os.path.basename(json_path))
    with open(answered_json, 'w') as f:
        json.dump(data, f, indent=4)

    # Move image
    answered_img = os.path.join(ANSWERED_DIR, os.path.basename(image_path))
    shutil.move(image_path, answered_img)

    # Upload
    user_id = st.session_state.get("session_id", "unknown")
    async_upload_record({"image_path": answered_img, "json_path": answered_json}, user_id)

    # Cleanup
    for folder in SAVE_DIRS:
        for path in [os.path.join(folder, os.path.basename(image_path)), os.path.join(folder, os.path.basename(json_path))]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    st.write(f"🧹 Removed duplicate: `{path}`")
                except Exception as e:
                    st.warning(f"⚠️ Could not delete `{path}`: {e}")
