import os
import sys
import json

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import get_session

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}

def flatten_offenses(raw_json: dict, state_abbr: str) -> list[dict]:
    state_name = STATE_NAMES.get(state_abbr)
    if not state_name:
        print(f"Warning: no full name mapping for {state_abbr}, skipping")
        return []
    
    actuals = raw_json.get("offenses", {}).get("actuals", {})
    rates = raw_json.get("offenses", {}).get("rates", {})
    populations = raw_json.get("populations", {})

    state_actuals = actuals.get(f"{state_name} Offenses", {})
    state_clearance_actuals = actuals.get(f"{state_name} Clearances", {})
    us_actuals = actuals.get("United States Offenses", {})
    us_clearance_actuals = actuals.get("United States Clearances", {})

    state_rates = rates.get(f"{state_name} Offenses", {})
    state_clearance_rates = rates.get(f"{state_name} Clearances", {})

    population = populations.get("population", {}).get(state_name, {})
    participated_population = populations.get("participated_population", {}).get(state_name, {})

    rows = []
    for month_key in state_actuals.keys():
        month_str, year_str = month_key.split("-")

        rows.append({
            "state_abbr": state_abbr,
            "offense_code": offense_code,
            "year": int(year_str),
            "month": int(month_str),
            "state_actual_count": state_actuals.get(month_key),
            "state_clearance_count": state_clearance_actuals.get(month_key),
            "state_rate_per_100k": state_rates.get(month_key),
            "state_clearance_rate_per_100k": state_clearance_rates.get(month_key),
            "us_actual_rate": us_actuals.get(month_key),
            "us_clearance_rate": us_clearance_actuals.get(month_key),
            "population": population.get(month_key),
            "participated_population": participated_population.get(month_key),
        })
    return rows

UPSERT_SQL = text("""
    INSERT INTO silver_summarized_offenses
        (state_abbr, offense_code, year, month,
         state_actual_count, state_clearance_count,
         state_rate_per_100k, state_clearance_rate_per_100k,
         us_actual_rate, us_clearance_rate,
         population, participated_population)
    VALUES
        (:state_abbr, :offense_code, :year, :month,
         :state_actual_count, :state_clearance_count,
         :state_rate_per_100k, :state_clearance_rate_per_100k,
         :us_actual_rate, :us_clearance_rate,
         :population, :participated_population)
    ON CONFLICT (state_abbr, offense_code, year, month) DO UPDATE SET
        state_actual_count = EXCLUDED.state_actual_count,
        state_clearance_count = EXCLUDED.state_clearance_count,
        state_rate_per_100k = EXCLUDED.state_rate_per_100k,
        state_clearance_rate_per_100k = EXCLUDED.state_clearance_rate_per_100k,
        us_actual_rate = EXCLUDED.us_actual_rate,
        us_clearance_rate = EXCLUDED.us_clearance_rate,
        population = EXCLUDED.population,
        participated_population = EXCLUDED.participated_population
""")

def run():
    session = get_session()
    total_processed = 0
    
    try:
        bronze_rows = session.execute(text("""
                                           SELECT DISTINCT ON (state_abbr, offense_code)
                   state_abbr, offense_code, response_json
            FROM bronze_summarized_offenses
            WHERE http_status = 200
            ORDER BY state_abbr, offense_code, extracted_at DESC
        """)).fetchall()
        
        for state_abbr, offense_code, response_json in bronze_rows:
            raw_json = json.loads(response_json)
            offense_rows = flatten_offenses(raw_json, state_abbr)
            
            if not offense_rows:
                 print(f"{state_abbr}/{offense_code}: nothing to load, skipping")
                continue
            
            try:
                session.execute(UPSERT_SQL, offense_rows)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"{state_abbr}/{offense_code}: upsert failed: {e}")
                continue