import requests
import json
import time

BASE_URL = "https://iapt.manageexam.com"
HEADERS = {
    "accept": "*/*",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (compatible; fetch-script/1.0)",
    "x-requested-with": "XMLHttpRequest"
}

STATE_IDS = {
    1: "ANDAMAN AND NICOBAR",
    2: "ANDHRA PRADESH",
    3: "ARUNACHAL PRADESH",
    4: "ASSAM",
    5: "BIHAR",
    6: "CHANDIGARH",
    7: "CHHATTISGARH",
    8: "DADRA AND NAGAR HAVELI",
    9: "DAMAN AND DIU",
    10: "DELHI",
    11: "GOA",
    12: "GUJARAT",
    13: "HARYANA",
    14: "HIMACHAL PRADESH",
    15: "JAMMU AND KASHMIR",
    16: "JHARKHAND",
    17: "KARNATAKA",
    18: "KERALA",
    100: "LADAKH",
    19: "LAKSHADWEEP",
    20: "MADHYA PRADESH",
    21: "MAHARASHTRA",
    22: "MANIPUR",
    23: "MEGHALAYA",
    24: "MIZORAM",
    36: "NAGALAND",
    25: "ODISHA",
    26: "PUDUCHERRY",
    27: "PUNJAB",
    28: "RAJASTHAN",
    29: "SIKKIM",
    30: "TAMIL NADU",
    31: "TELANGANA",
    32: "TRIPURA",
    33: "UTTAR PRADESH",
    34: "UTTARAKHAND",
    35: "WEST BENGAL"
}


def fetch_districts(state_id):
    url = f"{BASE_URL}/Centre/Centre/GetCentreDistricts"
    try:
        resp = requests.get(url, params={"stateId": state_id}, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            print(f"⚠️ Failed to fetch districts for state {state_id}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ Exception fetching districts for state {state_id}: {e}")
    return []


def fetch_cities(district_id):
    url = f"{BASE_URL}/Centre/Home/GetCentreCities"
    try:
        resp = requests.get(url, params={"districtId": district_id}, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            elif isinstance(data, list):
                return data
            else:
                return []
        else:
            print(f"⚠️ Failed to fetch cities for district {district_id}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"❌ Exception fetching cities for district {district_id}: {e}")
    return []


def main():
    mapping = {}

    for state_id, state_name in STATE_IDS.items():
        print(f"\n📍 Fetching districts for {state_name} (ID: {state_id})...")
        state_data = {
            "state_name": state_name,
            "districts": []
        }

        districts = fetch_districts(state_id)
        if not districts:
            print(f"⚠️ No districts found for state {state_name} ({state_id})")
            continue

        for dist in districts:
            # Use actual keys for district info
            district_id = dist.get("Value")
            district_name = dist.get("Text")

            if district_id is None or district_name is None:
                print(f"⚠️ Missing district ID or name, skipping district: {dist}")
                continue

            print(f"  ↳ District: {district_name} (ID: {district_id})")

            cities = fetch_cities(district_id)
            city_names = []
            if cities:
                for c in cities:
                    if isinstance(c, dict):
                        name = c.get("Text") or c.get("text")
                        if name:
                            city_names.append(name)
                    elif isinstance(c, str):
                        city_names.append(c)
            else:
                print(f"    ⚠️ No cities found for district {district_name}")

            state_data["districts"].append({
                "DistrictId": district_id,
                "DistrictName": district_name,
                "cities": city_names
            })

            time.sleep(0.3)

        mapping[state_id] = state_data
        time.sleep(0.5)

    with open("state_districts_cities.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print("\n✅ All data saved to 'state_districts_cities.json'.")



main()
