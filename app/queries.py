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

def get_rates(states, years, months, offenses, group_by):
    """"Annualised rate per 100k, totals and clearance rate for a filter selection"""
    if not group_by:
        raise ValueError("group_by needs at least one column")
    
# V/P are the sums of the individual offenses, so adding them together double counts
# its only a problem when offenses get combined into one number. if "offense" is a group-by column, every offense stays on its own row
    
    if "offense" not in group_by:
        has_totals = any(o in TOTAL_CODES for o in offenses)
        has_individual = any(o not in TOTAL_CODES for o in offenses)
        if has_totals and has_individual:
            raise ValueError("Choose either V/P totals or individual offenses, not both")
        
    cols = [GROUP_COLUMNS[g] for g in group_by]
    select_cols = ", ".join(f"{expr} AS {alias}" for expr, alias in cols)
    group_exprs = ", ".join(expr for expr, _ in cols)

    sql = f"""
        SELECT {select_cols},
        SUM(f.actual_count) AS total_offenses,
               ROUND(SUM(f.actual_count)::numeric
                     / NULLIF(SUM(f.population), 0) * 100000 * 12, 2) AS annual_rate_per_100k,
               ROUND(SUM(f.clearance_count)::numeric
                     / NULLIF(SUM(f.actual_count), 0), 3) AS clearance_rate
        FROM gold_offense_facts f
        JOIN gold_dim_state s ON f.state_abbr = s.state_abbr
        JOIN gold_dim_offense o ON f.offense_code = o.offense_code
        WHERE f.state_abbr   = ANY(:states)
          AND f.year         = ANY(:years)
          AND f.month        = ANY(:months)
          AND f.offense_code = ANY(:offenses)
        GROUP BY {group_exprs}
        ORDER BY {group_exprs}
    """
    params = {"states": list(states), "years": list(years),
              "months": list(months), "offenses": list(offenses)}
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)