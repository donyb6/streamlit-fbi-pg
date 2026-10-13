import os
import sys

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import get_session

OFFENSE_DIMENSION = [
    {"offense_code": "V",   "offense_name": "Violent Crime (All)",   "category": "Violent"},
    {"offense_code": "HOM", "offense_name": "Homicide",              "category": "Violent"},
    {"offense_code": "RPE", "offense_name": "Rape",                  "category": "Violent"},
    {"offense_code": "ROB", "offense_name": "Robbery",               "category": "Violent"},
    {"offense_code": "ASS", "offense_name": "Aggravated Assault",    "category": "Violent"},
    {"offense_code": "P",   "offense_name": "Property Crime (All)",  "category": "Property"},
    {"offense_code": "BUR", "offense_name": "Burglary",              "category": "Property"},
    {"offense_code": "LAR", "offense_name": "Larceny-Theft",         "category": "Property"},
    {"offense_code": "MVT", "offense_name": "Motor Vehicle Theft",   "category": "Property"},
    {"offense_code": "ARS", "offense_name": "Arson",                 "category": "Property"},
]

UPSERT_SQL = text("""
    INSERT INTO gold_dim_offense (offense_code, offense_name, category)
    VALUES (:offense_code, :offense_name, :category)
    ON CONFLICT (offense_code) DO UPDATE SET
        offense_name = EXCLUDED.offense_name,
        category = EXCLUDED.category
""")

def run():
    session = get_session()
    try:
        session.execute(UPSERT_SQL, OFFENSE_DIMENSION)
        session.commit()
        print(f"Done. {len(OFFENSE_DIMENSION)} offense rows written.")
    except Exception as e:
        session.rollback()
        print(f"Failed to write offense dimension: {e}")
        
    finally:
        session.close()
        
if __name__ == "__main__":
    run()