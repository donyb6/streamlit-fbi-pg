import os
import sys

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import get_session

STATE_DIMENSION = [
    {"state_abbr": "CA", "state_name": "California", "region": "West"},
    {"state_abbr": "TX", "state_name": "Texas",       "region": "South"},
    {"state_abbr": "WY", "state_name": "Wyoming",      "region": "West"},
    {"state_abbr": "VT", "state_name": "Vermont",      "region": "Northeast"},
]

UPSERT_SQL = text("""
    INSERT INTO gold_dim_state (state_abbr, state_name, region)
    VALUES (:state_abbr, :state_name, :region)
    ON CONFLICT (state_abbr) DO UPDATE SET
        state_name = EXCLUDED.state_name,
        region = EXCLUDED.region
""")

def run():
    session = get_session()
    try:
        session.execute(UPSERT_SQL, STATE_DIMENSION)
        session.commit()
        print(f"Done. {len(STATE_DIMENSION)} state rows written.")
    except Exception as e:
        session.rollback()
        print(f"Failed to write state dimension: {e}")
    finally:
        session.close()
        
if __name__ == "__main__":
    run()
        