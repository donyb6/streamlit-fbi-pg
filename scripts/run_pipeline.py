import os
import sys
import time
import importlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logging_config import get_logger

logger = get_logger("run_pipeline")

PIPELINE_ROUTES = [
    "extract_agencies",
    "extract_summarized",
    "silver_agencies",
    "silver_summarized",
    "gold_dim_offense",
    "gold_dim_state",
    "gold_dim_agency",
    "gold_offense_facts",
]
