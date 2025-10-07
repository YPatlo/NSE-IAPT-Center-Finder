import json
import os
import pickle
from api import fetch_centres
from geocode import geocode_address
from math import radians, sin, cos, sqrt, asin

GEOCODE_CACHE_FILE = "geocode_cache.pkl"

def simplify_address(addr: str) -> str:
    import re
    if not addr:
        return ""
    s = addr.strip()
    # remove repeated “NEAR” or redundant phrases
    s = s.replace("NEAR", "")
    # clean up commas / whitespace
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
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

def normalize(s: str):
    return s.strip().lower()

def select_state(states_dict):
    print("Select State:")
    for sid, st in states_dict.items():
        print(f"  {sid}: {st.get('state_name')}")
    choice = input("Enter State ID: ").strip()
    if choice not in states_dict:
        print("Invalid state ID.")
        return None
    return choice

def select_district(districts_list):
    print("Select District:")
    for dist in districts_list:
        print(f"  {dist['DistrictId']}: {dist['DistrictName']}")
    choice = input("Enter District ID: ").strip()
    for dist in districts_list:
        if dist["DistrictId"] == choice:
            return dist
    print("Invalid district ID.")
    return None

def select_city(city_list):
    print("Available Cities:")
    for city in city_list:
        print(f"  - {city}")
    choice = input("Enter City name (approx): ").strip()
    nchoice = normalize(choice)
    city_map = {normalize(city): city for city in city_list}
    if nchoice in city_map:
        return city_map[nchoice]
    # try fuzzy / prefix matching
    for norm, orig in city_map.items():
        if norm.startswith(nchoice) or nchoice.startswith(norm):
            return orig
    print("City not recognized.")
    return None

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

def main():
    with open("locations.json", "r", encoding="utf-8") as f:
        states = json.load(f)

    state_id = select_state(states)
    if not state_id:
        return
    state = states[state_id]

    districts = state.get("districts", [])
    if not districts:
        print("No districts for selected state.")
        return

    district = select_district(districts)
    if not district:
        return

    cities = district.get("cities", [])
    if not cities:
        print("No cities in selected district.")
        return

    city = select_city(cities)
    if not city:
        return

    print(f"\nFetching centres for {state['state_name']} / {district['DistrictName']} / {city} ...")
    centres = fetch_centres(state_id, district["DistrictId"], city, length=100)
    if not centres:
        print("No centres found.")
        return

    geocode_cache = load_geocode_cache()

    state = states[state_id]
    state_name = state["state_name"]
    district_name = district["DistrictName"]

    print(f"\nGeocoding {len(centres)} centres (with caching)...")
    for c in centres:
        addr = c.address
        if not addr or not addr.strip():
            print("Skipping centre with empty address:", c.name)
            c.coords = None
            continue

        clean = simplify_address(addr)
        full_addr = f"{clean}, {city}, {district_name}, {state_name}, India"
        print("Attempting geocode on:", full_addr)
        c.coords = geocode_address(full_addr)
        print("Result:", c.coords)

    save_geocode_cache(geocode_cache)

    user_addr = input("\nEnter your current address or location: ").strip()
    user_coords = geocode_with_cache(user_addr, geocode_cache)
    if not user_coords:
        print("Could not geocode your location. Exiting.")
        return

    print(f"Your coordinates: {user_coords}")

    save_geocode_cache(geocode_cache)

    nearest = find_nearest_centres(user_coords, centres, top_k=3)
    if not nearest:
        print("No centres with valid coordinates.")
        return

    print("\nNearest IAPT Centre(s):")
    for idx, (c, dist) in enumerate(nearest, start=1):
        print(f"\n#{idx}")
        print(f"  Code: {getattr(c, 'code', 'N/A')}")
        print(f"  Name: {getattr(c, 'name', 'N/A')}")
        print(f"  Address: {getattr(c, 'address', 'N/A')}")
        print(f"  Coordinator: {getattr(c, 'coordinator_name', 'N/A')}")
        print(f"  Subject: {getattr(c, 'subject', 'N/A')}")
        print(f"  Distance: {dist:.2f} km")

if __name__ == "__main__":
    main()

