import os
import json
import time
from configs.config import LOCAL_SAVE_FOLDER, ANSWERED_DIR
from utils.local.naming import get_next_local_idx

def process_local_uploads(uploaded_files, force_rename=False):
    """
    Saves uploaded files with unique names + creates JSON if missing.
    Returns:
        - records: files to process
        - skipped: files already in answered_images/ (unless force_rename=True)
    """
    records = []
    skipped = []
    image_exts = [".png", ".jpg", ".jpeg"]
    answered_names = set(os.listdir(ANSWERED_DIR))

    for uploaded_file in uploaded_files:
        name, ext = os.path.splitext(uploaded_file.name)
        if ext.lower() not in image_exts:
            continue

        is_duplicate = any(name in f for f in answered_names)

        if is_duplicate and not force_rename:
            skipped.append(uploaded_file.name)
            continue

        idx = get_next_local_idx()
        suffix = f"_re{idx}" if force_rename else f"_local_{idx}"
        new_name = f"{name}{suffix}{ext}"
        img_path = os.path.join(LOCAL_SAVE_FOLDER, new_name)

        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        json_path = os.path.join(LOCAL_SAVE_FOLDER, f"{name}{suffix}.json")
        if not os.path.exists(json_path):
            meta = {
                "source": "local",
                "original_name": uploaded_file.name,
                "created_at": time.time()
            }
            with open(json_path, "w") as jf:
                json.dump(meta, jf, indent=4)

        records.append({
            "image_path": img_path,
            "json_path": json_path,
            "source": "local"
        })

    return {"records": records, "skipped": skipped}
