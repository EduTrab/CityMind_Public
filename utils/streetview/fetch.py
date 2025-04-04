import os
import json
import time
from configs.config import SAVE_DIR, ANSWERED_DIR, MAPS_API_KEY
from data.cities_coordinates import city_coordinates
from streetview import search_panoramas, get_panorama_meta, get_streetview
from utils.common.index_utils import random_location





def download_image(pano_id, idx):
    """
    Downloads a Google Street View image using the panorama ID
    and saves it along with its metadata.

    Parameters:
        pano_id (str): The panorama identifier.
        idx (int): The index to be used in the filename.

    Returns:
        tuple: (image_path, json_path)
    """
    try:
        image = get_streetview(pano_id=pano_id, api_key=MAPS_API_KEY)
        image_path = os.path.join(SAVE_DIR, f"{idx}.png")
        image.save(image_path, "png")

        meta = get_panorama_meta(pano_id=pano_id, api_key=MAPS_API_KEY)
        meta_data = {
            "pano_id": pano_id,
            "location": {"lat": meta.location.lat, "lng": meta.location.lng},
            "date": meta.date
        }
        json_path = os.path.join(SAVE_DIR, f"{idx}.json")
        with open(json_path, 'w') as f:
            json.dump(meta_data, f, indent=4)
        return image_path, json_path
    except Exception as e:
        print(f"Error downloading image or metadata for pano_id {pano_id}: {e}")
        return None, None




def search_and_download_random(idx, coords=None, max_retries=10):
    """
    Attempts to find and download a random Street View image.
    Retries up to max_retries times if it cannot find a valid panorama.

    Parameters:
        idx (int): Index for naming files.
        coords (optional): Tuple of (lat, lon) to override random.
        max_retries (int): Maximum retry attempts (default is 10).
    """
    retries = 0
    while retries < max_retries:
        try:
            if coords:
                base_lat, base_lon = coords
            else:
                base_lat, base_lon = random_location()

            print(f"[CityCoord] Using lat/lon: {base_lat:.5f}, {base_lon:.5f}")
            panos = search_panoramas(lat=base_lat, lon=base_lon)
            if not panos:
                raise Exception(f"No panoramas found at {base_lat}, {base_lon}")
            pano_id = panos[0].pano_id
            return download_image(pano_id, idx)
        except Exception as e:
            print(f"Exception occurred: {e}")
            retries += 1
            time.sleep(0.2)
    return None, None

