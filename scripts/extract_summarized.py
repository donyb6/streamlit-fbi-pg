import os
import sys
import time
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

OFFENSES = ["V", "P", "HOM", "RPE", "ROB", "ASS", "BUR", "LAR", "MVT", "ARS"]

FROM_DATE = "01-2020"
TO_DATE = "01-2026"

SLEEP_BETWEEN_CALLS = 0.5