import os
import sys
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


def fetch_agencies(state: str):
    url = f"{API_BASE}/agency/byStateAbbr/{state}"
    return requests.get(url, params={"API_KEY": API_KEY}, timeout=30)


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
            print(f"Fetching agencies for {state}...")
            response = fetch_agencies(state)

            if response.status_code != 200:
                print(f"  Failed: HTTP {response.status_code}")
                continue

            try:
                session.execute(
                    text("""
                        INSERT INTO bronze_agencies (state_abbr, response_json, extracted_at)
                        VALUES (:state, :payload, :extracted_at)
                    """),
                    {
                        "state": state,
                        "payload": response.text,
                        "extracted_at": datetime.now(timezone.utc),
                    },
                )
                session.commit()
                print(f"  Landed ({len(response.text)} bytes)")
            except Exception as e:
                session.rollback()  # required in Postgres after a failed statement
                print(f"  Insert failed for {state}: {e}")
    finally:
        session.close()

    print("Done.")


if __name__ == "__main__":
    run()