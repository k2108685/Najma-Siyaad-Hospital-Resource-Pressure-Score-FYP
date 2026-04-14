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

nav_cols = st.columns([1.2, 1, 1, 1, 1.2])

with nav_cols[0]:
    if LOGO.exists():
        st.image(str(LOGO), width=90)
    else:
        st.markdown('<div class="custom-logo">NHS</div>', unsafe_allow_html=True)

with nav_cols[1]:
    st.page_link("home.py", label="Home", use_container_width=True)

with nav_cols[2]:
    st.page_link("pages/dashboard.py", label="Dashboard", use_container_width=True)

with nav_cols[3]:
    st.page_link("pages/monthly_filter.py", label="Check by Month", use_container_width=True)

with nav_cols[4]:
    st.page_link("pages/forecast.py", label="Forecast", use_container_width=True)

st.markdown("---")

st.title("Hospital Resource Pressure System")
st.write("One score: 0–100%. Higher values mean more pressure.")

st.markdown("## Pressure Level Guide")

st.markdown(
"""
<div style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:16px;">

<div style="
background:#2e7d32;
color:white;
padding:10px 16px;
border-radius:20px;
font-weight:600;
font-size:14px;
box-shadow:0 2px 6px rgba(0,0,0,0.1);
">
Low 0–34%
</div>

<div style="
background:#f9a825;
color:black;
padding:10px 16px;
border-radius:20px;
font-weight:600;
font-size:14px;
box-shadow:0 2px 6px rgba(0,0,0,0.1);
">
Moderate 35–54%
</div>

<div style="
background:#ef6c00;
color:white;
padding:10px 16px;
border-radius:20px;
font-weight:600;
font-size:14px;
box-shadow:0 2px 6px rgba(0,0,0,0.1);
">
High 55–74%
</div>

<div style="
background:#c62828;
color:white;
padding:10px 16px;
border-radius:20px;
font-weight:600;
font-size:14px;
box-shadow:0 2px 6px rgba(0,0,0,0.1);
">
Critical 75–100%
</div>

</div>
""",
unsafe_allow_html=True
)

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

show_footer("NHS England open data")