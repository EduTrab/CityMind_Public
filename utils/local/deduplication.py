import os
from configs.config import ANSWERED_DIR

def prune_local_records(record_list):
    """
    Filters out local image records that have already been answered (based on filename match).
    Used to clean up st.session_state.local_records.
    """
    answered = set(os.listdir(ANSWERED_DIR))
    cleaned = []
    for rec in record_list:
        base = os.path.splitext(os.path.basename(rec["image_path"]))[0]
        if not any(base in f for f in answered):
            cleaned.append(rec)
    return cleaned
