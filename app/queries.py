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