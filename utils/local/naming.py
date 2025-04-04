import os
from configs.config import LOCAL_SAVE_FOLDER, ANSWERED_DIR

def get_next_local_idx():
    indices = []
    for f in os.listdir(LOCAL_SAVE_FOLDER) + os.listdir(ANSWERED_DIR):
        if "_local_" in f and f.endswith(".png"):
            try:
                i = int(f.split("_local_")[1].split(".")[0])
                indices.append(i)
            except: pass
    return max(indices, default=0) + 1

def get_prefix_from_filename(filename):
    return filename.split("_local_")[0] if "_local_" in filename else os.path.splitext(filename)[0]
