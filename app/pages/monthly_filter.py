from pathlib import Path
import streamlit as st
from utils import get_data, display_labels, format_value, show_pressure, show_footer
from colourtheme import apply_styles

st.set_page_config(page_title="Check Month", layout="wide")

apply_styles()

LOGO = Path(__file__).parent.parent / "logo" / "nhs_logo.png"

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
st.title("Check by Month")

df = get_data()
df["PeriodStr"] = df["Period"].dt.strftime("%Y-%m")

selected_month = st.selectbox("Month", df["PeriodStr"], index=len(df) - 1)
row = df[df["PeriodStr"] == selected_month]

if row.empty:
    st.stop()

record = row.iloc[0]
score = float(record["Pressure Score"])

col1, col2 = st.columns(2)
col1.metric("Period", selected_month)
col2.metric("Pressure Score", f"{score * 100:.0f}%")

show_pressure(score)

display_columns = [
    c for c in [
        "Total Attendances",
        "Total Emergency Admissions",
        "Patients Waiting Over 4 Hours for Admission",
        "Percentage of Patients Seen Within 4 Hours",
        "Occupancy Rate"
    ]
    if c in df.columns
]

if display_columns:
    st.dataframe(
        [{"Indicator": display_labels(c), "Value": format_value(c, record[c])} for c in display_columns],
        hide_index=True,
        use_container_width=True
    )

row_index = row.index[0]
if row_index > 0:
    previous = df.iloc[row_index - 1]
    previous_score = float(previous["Pressure Score"])
    change = score - previous_score

    col1, col2, col3 = st.columns(3)
    col1.metric("Prev Month", f"{previous_score * 100:.0f}%")
    col2.metric("Change", f"{change * 100:+.0f}%")
    col3.metric("Direction", "Up" if change > 0 else "Down" if change < 0 else "Same")

    if change > 0:
        st.warning("Pressure increased compared with the previous month.")
    elif change < 0:
        st.success("Pressure decreased compared with the previous month.")
    else:
        st.info("Pressure was unchanged compared with the previous month.")

show_footer("Data: NHS England")