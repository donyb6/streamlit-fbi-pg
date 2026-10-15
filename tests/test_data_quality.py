import os
import sys

import pytest
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.db import get_session



@pytest.fixture
def session():
    """A fresh DB session for each test, closed automatically after."""
    s = get_session()
    yield s
    s.close()
    
# bronze layer tests
def test_bronze_agencies_has_four_states(session):
    result = session.execute(text("SELECT COUNT(DISTINCT state_abbr) FROM bronze_agencies")).scalar()
    assert result == 4, f"Expected 4 states in bronze_agencies, found {result}"


def test_bronze_summarized_all_calls_succeeded(session):
    failed = session.execute(
        text("SELECT COUNT(*) FROM bronze_summarized_offenses WHERE http_status != 200")
    ).scalar()
    assert failed == 0, f"{failed} bronze_summarized_offenses rows failed with non-200 status"
    
    
