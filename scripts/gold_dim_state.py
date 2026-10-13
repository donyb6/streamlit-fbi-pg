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