import os
import pickle
from geocode import geocode_address
from math import radians, sin, cos, sqrt, asin

GEOCODE_CACHE_FILE = "geocode_cache.pkl"

def simplify_address(addr: str) -> str:
    import re
    if not addr:
        return ""
    s = addr.strip()
    s = s.replace("NEAR", "")
    s = re.sub(r",\s+", ", ", s)
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()

def load_geocode_cache():
    if os.path.exists(GEOCODE_CACHE_FILE):
        with open(GEOCODE_CACHE_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_geocode_cache(cache):
    with open(GEOCODE_CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)

def haversine(coord1, coord2):
    R = 6371.0
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))

def normalize(s: str):
    return s.strip().lower()

def geocode_with_cache(address: str, cache: dict):
    key = normalize(address)
    if key in cache:
        return cache[key]
    coords = None
    try:
        coords = geocode_address(address)
    except Exception as e:
        print(f"Geocoding error for '{address}': {e}")
    cache[key] = coords
    return coords

def find_nearest_centres(user_coords, centres, top_k=1):
    results = []
    for c in centres:
        if hasattr(c, "coords") and c.coords:
            d = haversine(user_coords, c.coords)
            results.append((c, d))
    results.sort(key=lambda x: x[1])
    return results[:top_k]