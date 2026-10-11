import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from config.db import get_session

s = get_session()
print(s.execute(text("SELECT version()")).scalar())
s.close()