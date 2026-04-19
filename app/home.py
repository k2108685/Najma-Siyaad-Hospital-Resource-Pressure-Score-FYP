from pathlib import Path
import streamlit as st
from utils import get_data, show_pressure, show_footer
from colourtheme import apply_styles

st.set_page_config(
    page_title="Hospital Resource Pressure",
    layout="wide",
    menu_items={"Get Help": None}
)

apply_styles()

LOGO = Path(__file__).parent / "logo" / "nhs_logo.png"

#navigation bar 

nav1, nav2, nav3, nav4, nav5 = st.columns([1.2, 1, 1, 1, 1.2])

with nav1:
    if LOGO.exists():
        st.image(str(LOGO), width=90)
    else:
        st.markdown('<div class="custom-logo">NHS</div>', unsafe_allow_html=True)

with nav2:
    st.page_link("home.py", label="Home", width="stretch")
with nav3:
    st.page_link("pages/dashboard.py", label="Dashboard", width="stretch")
with nav4:
    st.page_link("pages/monthly_filter.py", label="Check by Month", width="stretch")
with nav5:
    st.page_link("pages/forecast.py", label="Forecast", width="stretch")

st.markdown("---")

st.title("Hospital Resource Pressure System")
st.write(
    "This system brings together key hospital performance indicators into one pressure score. "
    "It helps show current pressure levels, reviews past data monthly , and estimates future trends."
)

st.markdown("## Pressure Level Guide")
st.markdown(
"""
<div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px;">
<div style="background:#2e7d32; color:white; padding:10px 14px; border-radius:8px; font-weight:600;">
Low: 0% - 34%
</div>
<div style="background:#f9a825; color:black; padding:10px 14px; border-radius:8px; font-weight:600;">
Moderate: 35% - 54%
</div>
<div style="background:#ef6c00; color:white; padding:10px 14px; border-radius:8px; font-weight:600;">
High: 55% - 74%
</div>
<div style="background:#c62828; color:white; padding:10px 14px; border-radius:8px; font-weight:600;">
Critical: 75% - 100%
</div>
</div>
""",
unsafe_allow_html=True,
)
#load the data and show lastest
try:
    df = get_data()
    latest = df.iloc[-1]
    current_score = float(latest["Pressure Score"])
    previous_score = float(df.iloc[-2]["Pressure Score"]) if len(df) > 1 else current_score

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Current", f"{current_score * 100:.0f}%", delta=f"{(current_score - previous_score) * 100:+.0f}%")
    metric2.metric("Period", latest["Period"].strftime("%b %Y"))
    metric3.metric("Records", len(df))

    show_pressure(current_score)

except FileNotFoundError:
    st.info("Run preparedata.py first.")
except Exception as error:
    st.error(f"Could not load data: {error}")

st.markdown("## Pages")

card1, card2, card3 = st.columns(3)

with card1:
    st.markdown("### Dashboard")
    st.write(
        "View the overall pressure score and key trends across the full dataset. "
        "This page shows the main pressure score graph and the underlying indicators over time."
    )
    st.page_link("pages/dashboard.py", label="Open Dashboard", width="stretch")

with card2:
    st.markdown("### Check Date By Months")
    st.write(
        "Select a specific month to review its pressure score, see the main indicator values, "
        "and compare that month with the previous ones."
    )
    st.page_link("pages/monthly_filter.py", label="Open Check by Month", width="stretch")

with card3:
    st.markdown("### Forecast")
    st.write(
        "Predict future hospital pressure levels using the past pressure score trend. "
        "This page shows a forecast table, graph, and short explantion."
    )
    st.page_link("pages/forecast.py", label="Open Forecast", width="stretch")

st.markdown("## Purpose")

st.write("""
The HRPS is designed to make hospital pressure easier for people to understand by
providing a single score that combines all of the different indicators of hospital
pressure. This allows for people to  easily compare hospital pressure across
different time periods, as well as to help people to estimate the pressure
that hospitals may experience in the future.
""")

show_footer("NHS England open data")