import os
import sys
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import get_session

load_dotenv()

API_BASE = os.getenv("API_BASE")
API_KEY = os.getenv("FBI_API_KEY")
STATES = [s.strip().upper() for s in os.getenv("STATES", "").split(",") if s.strip()]

OFFENSES = ["V", "P", "HOM", "RPE", "ROB", "ASS", "BUR", "LAR", "MVT", "ARS"]

FROM_DATE = "01-2020"
TO_DATE = "01-2026"

SLEEP_BETWEEN_CALLS = 0.5

def fetch_summarized(state: str, offense: str):
    url = f"{API_BASE}/summarized/state/{state}/{offense}"
    params = {"from": FROM_DATE, "to": TO_DATE, "API_KEY": API_KEY}
    return requests.get(url, params=params, timeout=30)

def run():
    if not API_KEY:
        print("Missing FBI_API_KEY in .env")
        return
    if not API_BASE:
        print("Missing API_BASE in .env")
        return
    if not STATES:
        print("Missing STATES in .env")
        return

    session = get_session()
    try:
        for state in STATES:
            for offense in OFFENSES:
                print(f"fetching {state}/{offense}...")
                response = fetch_summarized(state, offense)
                
                payload = response.text if response.status_code == 200 else None
                if response.status_code != 200:
                    print(f"  Failed: HTTP {response.status_code}")
                    
                try:
                    session.execute(
                        text("""
                             INSERT INTO bronze_summarized_offenses
                                (state_abbr, offense_code, from_date, to_date,
                                 response_json, http_status, extracted_at)
                            VALUES (:state, :offense, :from_date, :to_date,
                                    :payload, :http_status, :extracted_at)
                        """),
                        {
                            "state": state,
                            "offense": offense,
                            "from_date": FROM_DATE,
                            "to_date": TO_DATE,
                            "payload": payload,
                            "http_status": response.status_code,
                            "extracted_at": datetime.now(timezone.utc),
                        }
                    )
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print(f"  Insert failed for {state}/{offense}: {e}")
                    continue
                
                if response.status_code == 200:
                    print(f"  Landed ({len(response.text)} bytes)")
                    
                    time.sleep(SLEEP_BETWEEN_CALLS)
    finally:
        session.close()
    
    print("Done.")
    
if __name__ == "__main__":
    run()