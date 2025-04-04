# utils/common/cleanup.py
import os
import shutil
from configs.config import SAVE_DIR, LOCAL_SAVE_FOLDER, ANSWERED_DIR


def clear_folder(path, extensions=(".png", ".json")):
    count = 0
    for file in os.listdir(path):
        if file.endswith(extensions):
            try:
                os.remove(os.path.join(path, file))
                count += 1
            except Exception as e:
                print(f"[Warning] Could not delete {file}: {e}")
    return count

def auto_clear_on_switch(prev_source, current_source):
    if prev_source == "Default Dataset" and current_source == "Local Dataset":
        cleared = clear_folder(SAVE_DIR)
        print(f"[Cleanup] Cleared {cleared} files from saved_images/")



def remove_stale_images():
    """
    Cleans up any images in saved_images/ that don't have corresponding MCQ JSONs
    or whose indexes are already in answered_images.
    Only runs after a successful batch has been created.
    """
    pngs = [f for f in os.listdir(SAVE_DIR) if f.endswith('.png')]
    jsons = set(f.replace('.json', '') for f in os.listdir(SAVE_DIR) if f.endswith('.json'))
    answered = set(f.replace('.json', '') for f in os.listdir(ANSWERED_DIR) if f.endswith('.json'))

    deleted = 0
    for img in pngs:
        base = img.replace('.png', '')
        if base not in jsons and base not in answered:
            try:
                os.remove(os.path.join(SAVE_DIR, img))
                deleted += 1
            except Exception as e:
                print(f"[Warning] Couldn't delete {img}: {e}")
    if deleted:
        print(f"[Stale Cleanup] Removed {deleted} unprocessed image(s) from saved_images/")