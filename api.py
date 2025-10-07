# api.py
import requests
from models import Centre

def fetch_centres(state_id, district_id, city_name, start=0, length=100):
    url = "https://iapt.manageexam.com/Centre/Centre/GetCompletedCentres"

    params = {
        "StateId": state_id,
        "DistrictId": district_id,
        "CityId": city_name,
        "draw": 1,
        "start": start,
        "length": length,
        "columns[0][data]": "Code",
        "columns[0][name]": "",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "true",
        "columns[0][search][value]": "",
        "columns[0][search][regex]": "false",
        "columns[1][data]": "Name",
        "columns[1][name]": "",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[1][search][value]": "",
        "columns[1][search][regex]": "false",
        "columns[2][data]": "Address",
        "columns[2][name]": "",
        "columns[2][searchable]": "true",
        "columns[2][orderable]": "true",
        "columns[2][search][value]": "",
        "columns[2][search][regex]": "false",
        "columns[3][data]": "CoordinatorName",
        "columns[3][name]": "",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[3][search][value]": "",
        "columns[3][search][regex]": "false",
        "columns[4][data]": "Subject",
        "columns[4][name]": "",
        "columns[4][searchable]": "false",
        "columns[4][orderable]": "true",
        "columns[4][search][value]": "",
        "columns[4][search][regex]": "false",
        "order[0][column]": 0,
        "order[0][dir]": "asc",
        "search[value]": "",
        "search[regex]": "false",
    }

    headers = {
        "User-Agent": "IAPT-Centre-Finder/1.0",
        "Accept": "*/*",
        "Content-Type": "application/json"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        centres = []
        for c in data.get("data", []):
            centre = Centre(
                code=c.get("Code"),
                name=c.get("Name"),
                address=c.get("Address"),
                coordinator_name=c.get("CoordinatorName"),
                subject=c.get("Subject")
            )
            centres.append(centre)
        return centres
    else:
        print(f"❌ Failed to fetch centres (HTTP {response.status_code}). Response:\n{response.text}")
        return []
