from pathlib import Path
import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).resolve().parent / "data" / "processed" / "ae_pressure_with_score.csv"


@st.cache_data
#loads thes data once and caches it 
def get_data():
    
    if not DATA_FILE.exists():
        raise FileNotFoundError("Run preparedata.py first")

    df = pd.read_csv(DATA_FILE)
    df["Period"] = pd.to_datetime(df["Period"], errors="coerce")
    df = df.dropna(subset=["Period"]).sort_values("Period").reset_index(drop=True)
    return df

#convert the pressure score into labels 
def get_pressure(score):
  
    if score >= 0.75:
        return "Critical"
    elif score >= 0.55:
        return "High"
    elif score >= 0.35:
        return "Moderate"
    else:
        return "Low"

#show the pressure score as a coloured box 
def show_pressure(score):
    
    if score >= 0.75:
        background_colour = "#9a0101"
        label = "Critical"
        text_colour = "white"
    elif score >= 0.55:
        background_colour = "#ef6c00"
        label = "High"
        text_colour = "white"
    elif score >= 0.35:
        background_colour = "#f9a825"
        label = "Moderate"
        text_colour = "black"
    else:
        background_colour = "#2e7d32"
        label = "Low"
        text_colour = "white"

    st.markdown(
        f"""
        <div style="
            background:{background_colour};
            color:{text_colour};
            padding:14px;
            border-radius:10px;
            font-weight:700;
            margin:10px 0;
        ">
            Pressure: {label} ({score * 100:.0f}%)
        </div>
        """,
        unsafe_allow_html=True
    )

#shorten names 
def display_labels(column_name):
    
    name_map = {
        "Total Attendances": "Attendances",
        "Total Emergency Admissions": "Admissions",
        "Patients Waiting Over 4 Hours for Admission": "Waited for 4+ Hours",
        "Percentage of Patients Seen Within 4 Hours": "Seen within 4 Hours",
        "Occupancy Rate": "Bed Occupancy"
    }
    return name_map.get(column_name, column_name)

#formats values as a percentage 
def format_value(column_name, value):
    
    if pd.isna(value):
        return "N/A"

    if "Occupancy" in column_name:
        return f"{value:.1%}"

    if "Seen within 4 Hours" in column_name or "Percentage of Patients Seen Within 4 Hours" in column_name:
        return f"{value * 100:.1f}"

    return f"{int(round(float(value))):,}"


def show_footer(message):
    
    st.markdown(
        f'<div class="footer-text">{message}</div>',
        unsafe_allow_html=True
    )