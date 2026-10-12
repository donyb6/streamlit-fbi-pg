import os
import sys
import json

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import get_session

def blank_to_none(value):
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value
