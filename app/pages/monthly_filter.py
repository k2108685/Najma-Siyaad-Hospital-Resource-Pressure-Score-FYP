from pathlib import Path
import streamlit as st
import pandas as pd

from utils import get_data, get_pressure, show_pressure, display_labels, format_value, show_footer
from colourtheme import apply_styles


st.set_page_config(page_title="Check by Month", layout="wide")
apply_styles()


BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "logo" / "nhs_logo.png"


# Top navigation
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

with col1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=100)
    else:
        st.markdown('<div class="custom-logo">NHS</div>', unsafe_allow_html=True)

with col2:
    st.page_link("home.py", label="Home")

with col3:
    st.page_link("pages/dashboard.py", label="Dashboard")

with col4:
    st.page_link("pages/monthly_filter.py", label="Check by Month")

with col5:
    st.page_link("pages/forecast.py", label="Forecast")


st.markdown("---")

st.title("Check Data by Month")
st.write("Choose a month to see the hospital pressure score for that month and the month before.")

# Load data
try:
    df = get_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

required_columns = ["Period", "Pressure Score"]
for col in required_columns:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

# Month dates to  British
month_options = df["Period"].dt.strftime("%b %Y").tolist()

selected_month = st.selectbox(
    "Select Month",
    options=month_options,
    index=len(month_options) - 1
)

# Filter by selected month
selected_df = df[df["Period"].dt.strftime("%b %Y") == selected_month]

if selected_df.empty:
    st.warning("No data found for the selected month.")
    st.stop()

row = selected_df.iloc[0]
score = float(row["Pressure Score"])


colA, colB = st.columns(2)
colA.metric("Selected Month", selected_month)
colB.metric("Pressure Score", f"{score * 100:.0f}%")

show_pressure(score)

st.subheader("Indicators")

indicator_columns = [
    "Total Attendances",
    "Total Emergency Admissions",
    "Patients Waiting Over 4 Hours for Admission"
]

if "Percentage of Patients Seen Within 4 Hours" in df.columns:
    indicator_columns.append("Percentage of Patients Seen Within 4 Hours")

if "Occupancy Rate" in df.columns:
    indicator_columns.append("Occupancy Rate")

indicator_columns = [col for col in indicator_columns if col in df.columns]

if indicator_columns:
    left_col, right_col = st.columns(2)

    for i, col in enumerate(indicator_columns):
        value = row[col]
        label = display_labels(col)
        formatted_value = format_value(col, value)

        if i % 2 == 0:
            left_col.metric(label, formatted_value)
        else:
            right_col.metric(label, formatted_value)

st.subheader("Compare With Previous Month")

idx = selected_df.index[0]

if idx > 0:
    prev_row = df.iloc[idx - 1]
    prev_score = float(prev_row["Pressure Score"])
    change = score - prev_score

    col1, col2, col3 = st.columns(3)
    col1.metric("Previous Month Score", f"{prev_score * 100:.0f}%")
    col2.metric("Change", f"{change * 100:+.0f}%")

    if change > 0:
        trend_text = "Increased"
    elif change < 0:
        trend_text = "Decreased"
    else:
        trend_text = "No Change"

    col3.metric("Direction", trend_text)
else:
    st.info("No previous month available for comparison.")

st.markdown(
    f"""
    <div style="
        margin-top: 16px;
        padding: 14px 16px;
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        font-size: 18px;
        color: #1f2937;
        font-weight: 500;
    ">
        <strong>{selected_month}</strong> — Pressure was <strong>{get_pressure(score)}</strong>
    </div>
    """,
    unsafe_allow_html=True
)

show_footer("Data: NHS England")