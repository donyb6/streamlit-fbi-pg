import calendar
import sys
import os
import base64

import streamlit as st
import pandas as pd
import altair as alt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.queries import get_options, get_rates
from pathlib import Path

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

@st.cache_data(ttl=3600)
def load_summary(states: tuple, years: tuple, months: tuple,
                 offense_codes: tuple, by: str) -> pd.DataFrame:
    """Pooled figures over the whole selection: one row per state or offense.
    Same formulas as the views (total offenses / total population, total clearances /
    total offenses), so the numbers are exact rather than averages of monthly values."""
    df = get_rates(list(states), list(years), list(months), list(offense_codes), [by])
    df = df.rename(columns={by: "series"})
    df["rate"] = df["annual_rate_per_100k"].astype(float)
    df["clearance"] = df["clearance_rate"].astype(float)
    return df[["series", "rate", "clearance", "total_offenses"]]


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
    
# About me
AVATAR_URL = "data:image/jpeg;base64," + base64.b64encode(
    (Path(__file__).parent.parent / "app" / "avatar.jpg").read_bytes()).decode()

st.markdown("""
<style>
.st-key-about_me {
    position: fixed;
    bottom: 1.25rem;
    right: 1.25rem;
    z-index: 1000;
    width: auto;
}
.st-key-about_me button {
    width: 3.6rem;
    height: 3.6rem;
    padding: 0;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.85);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
    background-image: url("__AVATAR__");
    background-size: cover;
    background-position: center;
    color: transparent;
}
.st-key-about_me button [data-testid="stIconMaterial"] {
    display: none;
}
</style>
""".replace("__AVATAR__", AVATAR_URL), unsafe_allow_html=True)

with st.container(key="about_me"):
    with st.popover("About me"):
        st.markdown("### Hello, I'm Desmond Boako Obeng!")
        st.caption("A level 400 Bsc Data Science student at Ghana Communication Technology University. ")
        st.write(
            "I like data and data engineering. "
            "Outside the data work, I have a knack for networking and computer hardware. "
            "This app is the end of a pipeline I built step by step: FBI Crime Data Explorer API, "
            "then bronze, silver and gold layers in PostgreSQL, then this Streamlit app on Neon."
        )
        st.markdown(
            "[GitHub](https://github.com/donyb6) · "
            "[obengdboako@gmail.com](mailto:obengdboako@gmail.com) · "
            "[Snapchat](https://www.snapchat.com/@d.onyb)"
        )
        st.caption("FBI Crime Data Explorer")
        

# page header
st.title(":material/query_stats: FBI Crime Data Explorer")
st.caption("Compare states or offenses on annualised rates per 100,000 people.")

left, right = st.columns([1, 3])

#left column: filters
with left:
    with st.container (border = True):
        picked = st.multiselect("States", options=list(abbr_to_name), key="states", format_func=abbr_to_name.get)
        
        mode = st.radio("Compare by", ["States", "Offenses"], horizontal=True)
        log_scale = False
        if mode == "States":
            offense_names = [st.selectbox("Offense", list(offense_to_code), index=list(offense_to_code).index("Violent Crime (All)"))]
        else:
            offense_names = st.multiselect(
                "Offense", list(offense_to_code), default=["Violent Crime (All)", "Property Crime (All)"])
            st.caption("Selected states are pooled into one combined rate.")
            log_scale = st.checkbox("Log scale (helps when rates differ a lot)")
            
        year_pick = st.pills("Years", options=YEAR_OPTIONS, selection_mode = "multi",
                             key = "year_pick", on_change = tidy_year_pills) or ["All"]
        include_2021 = False
        if "All" in year_pick:
            include_2021 = st.checkbox("Include 2021 (reported anomaly year)", value=False)
            
        smooth = st.toggle(
    "Smooth (12-month average)", value=True,
    help="Averages each month with the 11 before it, but never across a gap, "
         "so an excluded year cannot leak into the months after it.")
        
        with st.expander("More filters"):
            months = st.multiselect("Months", list(range(1, 13)), default=list(range(1, 13)),
                                    format_func=lambda m: calendar.month_abbr[m])

if not picked or not months or not offense_names:
    st.warning("Please select at least one state, month, and offense.")
    st.stop()

# Determine which years to include in the query
if "All" in year_pick:
    years_sel = [y for y in all_years if include_2021 or y != 2021]
else:
    years_sel = [int(y) for y in year_pick]
    
by = "state" if mode == "States" else "offense"
codes = tuple(offense_to_code[o] for o in offense_names)
  
# data
df = load_series(tuple(picked), tuple(all_years), tuple(offense_to_code[o] for o in offense_names),
                 "state" if mode == "States" else "offense")

df = df[df["date"].dt.year.isin(years_sel)]
df =  df[df["date"].dt.month.isin(months)]

if df.empty:
    st.warning("No data for this combination of filters")
    st. stop()
    
# A "segment" is an unbroken run of months. A gap (an excluded year, unticked months)
# starts a new segment, so lines are not drawn across it and smoothing never averages
# across it (otherwise an excluded year leaks into the months after it)
month_no = df["date"].dt.year * 12 + df["date"].dt.month
seg_of, seg, prev = {}, 0, None
for m in sorted(month_no.unique()):
    if prev is not None and m - prev != 1:
        seg += 1
    seg_of[m] = seg
    prev = m
df = df.assign(segment=month_no.map(seg_of))

if smooth:
    df["rate"] = df.groupby(["series", "segment"])["rate"].transform(
        lambda s: s.rolling(12, min_periods=1).mean()
    )

summary = load_summary(tuple(picked), tuple(years_sel), tuple(months), codes, by)
summary = summary.dropna(subset=["rate"])

order = sorted(set(df["series"]) | set(summary["series"]))
color_scale = alt.Scale(domain=order)

# summary metrics
ranked = summary.sort_values("rate")
with left:
    with st.container(border=True):
        c1, c2 = st.columns(2)
        hi, lo = ranked.iloc[-1], ranked.iloc[0]
        c1.metric("Highest rate", hi["series"], f"{hi['rate']:,.0f} per 100k", delta_color="off")
        c2.metric("Lowest rate", lo["series"], f"{lo['rate']:,.0f} per 100k", delta_color="off")
        
        
# right column: chart
with right:
    with st.container(border=True):
        chart = (
            alt.Chart(df).mark_line().encode(
                 x=alt.X("date:T", title="Date"),
                y=alt.Y("rate:Q", title="Annualised rate per 100k",
                        scale=alt.Scale(type="log") if log_scale else alt.Scale(zero=False)),
                color=alt.Color("series:N", title="State" if mode == "States" else "Offense"),
                detail=alt.Detail("segment:N"),
            )
            .properties(
                width = "container",
                height = 380)
        )
        st.altair_chart(chart)
        
    bar_order = summary.sort_values("rate", ascending=False)["series"].tolist()
    bar_height = max(170, 34 * len(summary))
    b1, b2 = st.columns(2)
    
    with b1.container(border=True, height="content"):
        st.markdown("**Rate per 100k, whole selection**")
        st.altair_chart(
            alt.Chart(summary).mark_bar().encode(
                y=alt.Y("series:N", sort=bar_order, title=None),
                x=alt.X("rate:Q", title="Annualised rate per 100k"),
                color=alt.Color("series:N", scale=color_scale, legend=None),
                tooltip=[alt.Tooltip("series:N", title="Series"),
                         alt.Tooltip("rate:Q", title="Rate per 100k", format=",.1f"),
                         alt.Tooltip("total_offenses:Q", title="Offenses", format=",")],
            ).properties(width="container", height=bar_height))
    
    with b2.container(border=True, height="content"):
        st.markdown("**Clearance rate, whole selection**")
        st.altair_chart(
             alt.Chart(summary.dropna(subset=["clearance"])).mark_bar().encode(
                y=alt.Y("series:N", sort=bar_order, title=None),
                x=alt.X("clearance:Q", title="Share of offenses cleared",
                        axis=alt.Axis(format=".0%")),
                color=alt.Color("series:N", scale=color_scale, legend=None),
                tooltip=[alt.Tooltip("series:N", title="Series"),
                         alt.Tooltip("clearance:Q", title="Clearance rate", format=".1%")],
            ).properties(width="container", height=bar_height))
    
        

if 2021 in years_sel:
    st.caption("2021 is included. The tier-comparison and offense-rate views leave it out.")
    
    
# state vs peer average
if mode == "Offenses":
    st.stop()
    
st.subheader("Individual states vs peer average")
st.caption('For each state, the "peer average" is the simple average of the other '
           'selected states, excluding that state itself.')    

if len(picked) < 2:
    st.info("Select at least two states to see the peer comparison.")
    st.stop()

wide = df.pivot(index="date", columns="series", values="rate")
wide = wide.reindex(pd.date_range(wide.index.min(), wide.index.max(), freq="MS"))
wide.index.name = "date"  # missing months are now NaN rows, which break the lines
names = list(wide.columns)

for i in range(0, len(names), 2):
    cols = st.columns(4)
    for j, name in enumerate(names[i:i + 2]):
        peers = wide.drop(columns=name).mean(axis=1)
        
        compare = pd.DataFrame({"date" : wide.index,
                                "own" : wide[name].values,
                                "peer" : peers.values})
        compare["delta"] = compare["own"] - compare["peer"]
        
        base = alt.Chart(compare).encode(x = alt.X("date:T", title = "Date"))
        shared_y = alt.Scale(zero=False)
        
        with cols[2 * j].container(border=True):
            st.markdown(f"**{name} vs peer average**  \n:red[● {name}] · :gray[● Peer average]")
            st.altair_chart(
                (base.mark_line(color="red").encode(
                    y=alt.Y("own:Q", title="Rate per 100k", scale=shared_y))
                 + base.mark_line(color="gray").encode(
                     y=alt.Y("peer:Q", title="Rate per 100k", scale=shared_y))
                 ).properties(width="container", height=250)
            )
            
        with cols[2 * j + 1].container(border=True):
            st.markdown(f"**{name} minus peer average**")
            st.altair_chart(
                base.mark_area(color="#7fc4ff").encode(
                    y=alt.Y("delta:Q", title="Delta"),
                ).properties(width="container", height=250))