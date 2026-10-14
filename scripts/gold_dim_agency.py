import os
import sys

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import get_session

UPSERT_SQL = text("""
    INSERT INTO gold_dim_agency
                (ori, agency_name, agency_type_name, county, state_abbr,
                 latitude, longitude, is_nibrs, nibrs_start_date)
            SELECT
                ori, agency_name, agency_type_name, county, state_abbr,
                latitude, longitude, is_nibrs, nibrs_start_date
            FROM silver_agencies
            ON CONFLICT (ori) DO UPDATE SET
                agency_name = EXCLUDED.agency_name,
                agency_type_name = EXCLUDED.agency_type_name,
                county = EXCLUDED.county,
                state_abbr = EXCLUDED.state_abbr,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                is_nibrs = EXCLUDED.is_nibrs,
                nibrs_start_date = EXCLUDED.nibrs_start_date
""")

def run():
    session = get_session()
    try:
        result = session.execute(UPSERT_SQL)
        session.commit()
        print(f"Done. {result.rowcount} agency dimension rows affected.")
    except Exception as e:
        session.rollback()
        print(f"Failed to load agency dimension: {e}")
    finally:
        session.close()
        
if __name__ == "__main__":
    run()