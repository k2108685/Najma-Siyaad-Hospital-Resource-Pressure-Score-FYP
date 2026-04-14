from pathlib import Path
import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).resolve().parent / "data" / "processed" / "ae_pressure_with_score.csv"

@st.cache_data
def get_data():
    """Load and clean the processed data."""
    if not DATA_FILE.exists():
        raise FileNotFoundError("Run preparedata.py first")

    df = pd.read_csv(DATA_FILE)
    df["Period"] = pd.to_datetime(df["Period"], errors="coerce")
    df = df.dropna(subset=["Period"]).sort_values("Period").reset_index(drop=True)
    return df


def get_pressure(score):
    """Return a pressure label."""
    if score >= 0.75:
        return "Critical"
    elif score >= 0.55:
        return "High"
    elif score >= 0.35:
        return "Moderate"
    else:
        return "Low"


def show_pressure(score):
    """Display a styled pressure level box."""
    if score >= 0.75:
        background_colour = "#fdeaea"
        border_colour = "#f5b5b5"
        text_colour = "#b42318"
        label = "Critical"
    elif score >= 0.55:
        background_colour = "#fff4e5"
        border_colour = "#f7d79f"
        text_colour = "#b54708"
        label = "High"
    elif score >= 0.35:
        background_colour = "#fff8db"
        border_colour = "#f5dd7b"
        text_colour = "#b54708"
        label = "Moderate"
    else:
        background_colour = "#ecfdf3"
        border_colour = "#a6f4c5"
        text_colour = "#067647"
        label = "Low"

    st.markdown(
        f"""
        <div style="
            background:{background_colour};
            border:1px solid {border_colour};
            color:{text_colour};
            padding:14px;
            border-radius:10px;
            font-weight:600;
            margin:10px 0;
        ">
            Pressure Level: {label} {score * 100:.0f}%
        </div>
        """,
        unsafe_allow_html=True
    )


def display_labels(column_name):
    """Shorten names for display."""
    name_map = {
        "Total Attendances": "Attendances",
        "Total Emergency Admissions": "Admissions",
        "Patients Waiting Over 4 Hours for Admission": "Waited for 4+ Hours",
        "Percentage of Patients Seen Within 4 Hours": "Seen within 4 Hours",
        "Occupancy Rate": "Bed Occupancy"
    }
    return name_map.get(column_name, column_name)


def format_value(column_name, value):
    """Format values so they display clearly."""
    if pd.isna(value):
        return "N/A"

    if "Percent" in column_name or "Occupancy" in column_name:
        return f"{float(value):.1%}"

    return f"{int(round(float(value))):,}"


def show_footer(message):
    """Show a footer at the bottom of the page."""
    st.markdown(
        f'<div class="footer-text">{message}</div>',
        unsafe_allow_html=True
    )