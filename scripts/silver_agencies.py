import os
import sys
import json

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import get_session

def blank_to_none(value):
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value

def flatten_agencies(raw_json: dict, state_abbr: str) -> list[dict]:
    rows = []
    for county, agencies in raw_json.items():
        for agency in agencies:
            rows.append({
                "ori": agency.get("ori"),
                "agency_name": agency.get("agency_name"),
                "agency_type_name": agency.get("agency_type_name"),
                "county": county,
                "state_abbr": state_abbr,
                "state_name": agency.get("state_name"),
                "latitude": blank_to_none(agency.get("latitude")),
                "longitude": blank_to_none(agency.get("longitude")),
                "is_nibrs": agency.get("is_nibrs"),
                "nibrs_start_date": blank_to_none(agency.get("nibrs_start_date")),
            })
    return rows