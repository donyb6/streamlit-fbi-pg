import os
import sys

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import get_session

UPSERT_SQL = text("""
    INSERT INTO gold_offense_facts
        (state_abbr, offense_code, year, month,
         actual_count, clearance_count, clearance_rate,
         rate_per_100k, population)
    SELECT
        state_abbr, offense_code, year, month,
        state_actual_count,
        state_clearance_count,
        ROUND(state_clearance_count::numeric / NULLIF(state_actual_count, 0), 4),
        state_rate_per_100k,
        population
    FROM silver_summarized_offenses
    ON CONFLICT (state_abbr, offense_code, year, month) DO UPDATE SET
        actual_count = EXCLUDED.actual_count,
        clearance_count = EXCLUDED.clearance_count,
        clearance_rate = EXCLUDED.clearance_rate,
        rate_per_100k = EXCLUDED.rate_per_100k,
        population = EXCLUDED.population
""")

def run():
    session = get_session()
    try:
        result = session.execute(UPSERT_SQL)
        session.commit()
        print(f"Done. {result.rowcount} fact rows affected.")
    except Exception as e:
        session.rollback()
        print(f"Failed to write offense facts: {e}")
    finally:
        session.close()
        
if __name__ == "__main__":
    run()