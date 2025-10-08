import json
from api import fetch_centres
from utils import (
    simplify_address,
    load_geocode_cache,
    save_geocode_cache,
    normalize,
    geocode_with_cache,
    find_nearest_centres,
)

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
    for norm, orig in city_map.items():
        if norm.startswith(nchoice) or nchoice.startswith(norm):
            return orig
    print("City not recognized.")
    return None

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

    total = len(centres)
    print(f"Total centres fetched: {total}")

    geocode_cache = load_geocode_cache()

    state_name = state["state_name"]
    district_name = district["DistrictName"]

    valid_count = 0
    for c in centres:
        addr = c.address
        if not addr or not addr.strip():
            c.coords = None
            continue

        clean = simplify_address(addr)
        full_addr = f"{clean}, {city}, {district_name}, {state_name}, India"
        coords = geocode_with_cache(full_addr, geocode_cache)
        if coords:
            valid_count += 1
        c.coords = coords

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
