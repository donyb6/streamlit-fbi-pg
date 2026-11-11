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

@st.cache_data(ttl=3600)
def load_series(states: tuple, years: tuple, offense_codes: tuple, by: str) -> pd.DataFrame:
    """One row per (series, month). 'by' is 'state' or 'offense'"""
    df = get_rates(list(states), list(years), range(1, 13), list(offense_codes), [by, 'year', 'month'])
    df = df.rename(columns={by: 'series'}) # series is either state or offense
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    df["rate"] = df["annual_rate_per_100k"].astype(float)
    return df[["series", "date", "rate"]].sort_values(["series", "date"]).reset_index(drop=True)