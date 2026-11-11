import calendar
import sys
import os

import streamlit as st
import pandas as pd
import altair as alt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.queries import get_options, get_rates

st.set_page_config(page_title="FBI Crime Data", layout="wide")


# cached data loaders
@st.cache_data(ttl=3600)
def load_options():
    return get_options()