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

UPSERT_SQL = text("""
    INSERT INTO silver_agencies
        (ori, agency_name, agency_type_name, county, state_abbr,
         state_name, latitude, longitude, is_nibrs, nibrs_start_date)
    VALUES
        (:ori, :agency_name, :agency_type_name, :county, :state_abbr,
         :state_name, :latitude, :longitude, :is_nibrs, :nibrs_start_date)
    ON CONFLICT (ori) DO UPDATE SET
        agency_name = EXCLUDED.agency_name,
        agency_type_name = EXCLUDED.agency_type_name,
        county = EXCLUDED.county,
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        is_nibrs = EXCLUDED.is_nibrs,
        nibrs_start_date = EXCLUDED.nibrs_start_date
""")

def run():
    session = get_session()
    total_processed = 0
    
    try:
        bronze_rows = session.execute(text("""
                                           SELECT DISTINCT ON (state_abbr) state_abbr, response_json
                                           FROM bronze_agencies
                                           ORDER BY state_abbr, extracted_at DESC
                                           """)).fetchall()
        for state_abbr, response_json in bronze_rows:
            raw_json = json.loads(response_json)
            agency_rows = flatten_agencies(raw_json, state_abbr)
            
            if not agency_rows:
                print(f"{state_abbr}: no agencies found, skipping")
                continue
            
            try:
                session.execute(UPSERT_SQL, agency_rows)
                session.commit()
                
            except Exception as e:
                session.rollback()
                print(f"{state_abbr}: upsert failed: {e}")
                continue
            
            total_processed += len(agency_rows)
            print(f"{state_abbr}: upserted {len(agency_rows)} agencies")
    finally:
        session.close()
        
    print(f"Done. {total_processed} agency rows processed.")