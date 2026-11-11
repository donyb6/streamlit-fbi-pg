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


# load options and create lookup dictionaries for state and offense names/codes
states_df, offenses_df, all_years = load_options()
abbr_to_name = dict(zip(states_df["state_abbr"], states_df["state_name"]))
offense_to_code = dict(zip(offenses_df["offense_name"], offenses_df["offense_code"]))


# session state for user selections
if "states" not in st.session_state:
    from_url =[s for s in st.query_params.get("states", "").split(",") if s in abbr_to_name]
    st.session_state["states"] = from_url or list(abbr_to_name)
    

YEAR_OPTIONS = ["All"] + [str(y) for y in all_years]

# session state for year selection
if "year_pick" not in st.session_state:
    st.session_state["year_pick"] = ["All"]
    st.session_state["_year_prev"] = ["All"]

def tidy_year_pills():
    """Make 'All' and individual years mutually exclusive"""
    sel = st.session_state["year_pick"]
    prev = st.session_state["_year_prev"]
    if "All" in sel and len(sel) > 1:
        sel = ["All"] if "All" not in prev else [s for s in sel if s != "All"]
    elif not sel:
        sel = ["All"]
    st.session_state["year_pick"] = sel
    st.session_state["_year_prev"] = sel
    
    
# page header
st.title(":material/query_stats: Crime Data Explorer")
st.caption("Compare states or offenses on annualised rates per 100,000 people.")