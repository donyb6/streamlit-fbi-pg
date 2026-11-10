import os
import sys

import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import engine

TOTAL_CODES = ["V", "P"] # all violent/all property rows

# grouping columns and their corresponding sql expressions
GROUP_COLUMNS = {
    "state" : ("s.state_name", "state"),
    "year" : ("f.year", "year"),
    "month" : ("f.month", "month"),
    "offense" : ("o.offense_name", "offense"),
    "category" : ("o.category", "category"),
}

def get_options():
    """Values for the filter widgets"""
    with engine.connect() as conn:
        states = pd.read_sql(text("SELECT state_abbr, state_name FROM gold_dim_state ORDER BY state_name"), conn)
        offenses = pd.read_sql(text("SELECT offense_code, offense_name, category FROM gold_dim_offense ORDER BY category, offense_code"), conn)
        years = pd.read_sql(text("SELECT DISTINCT year FROM gold_offense_facts ORDER BY year"), conn)
    return states, offenses, years["year"].tolist()