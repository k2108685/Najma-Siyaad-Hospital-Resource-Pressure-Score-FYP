from pathlib import Path
import matplotlib.pyplot as plt
import streamlit as st

from utils import get_data, show_pressure, display_labels, format_value, show_footer
from colourtheme import apply_styles


st.set_page_config(page_title="Dashboard", layout="wide")
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
st.title("HRPS Dashboard")

#load data and get lastest data 
df = get_data()
latest = df.iloc[-1]
current_score = float(latest["Pressure Score"])
previous_score = float(df.iloc[-2]["Pressure Score"]) if len(df) > 1 else current_score

colA, colB, colC = st.columns(3)
colA.metric("Current Pressure", f"{current_score:.2f}")
colB.metric("Current Period", latest["Period"].strftime("%b %Y"))
colC.metric("Previous Pressure", f"{previous_score:.2f}")

show_pressure(current_score)

st.subheader("Pressure Score Over Time")
#plot the score over time on graph

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["Period"], df["Pressure Score"], marker="o", linewidth=1.5)
ax.axhline(0.75, linestyle="--", linewidth=1, label="Critical")
ax.axhline(0.55, linestyle="--", linewidth=1, label="High")
ax.set_ylim(0, 1)
ax.set_xlabel("Month")
ax.set_ylabel("Pressure Score")
ax.set_facecolor("#f5f7fb")
fig.patch.set_facecolor("#f5f7fb")
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

indicator_columns = [
    "Total Attendances",
    "Total Emergency Admissions",
    "Patients Waiting Over 4 Hours for Admission",
    "Percentage of Patients Seen Within 4 Hours",
    "Occupancy Rate"
]

indicator_columns = [col for col in indicator_columns if col in df.columns]

#individual graphs for each indicator
if indicator_columns:
    tab1, tab2, tab3 = st.tabs(["Combined Trends", "Individual Graphs", "Latest"])

    with tab1:
        fig, ax = plt.subplots(figsize=(10, 4))

        for col in indicator_columns:
            ax.plot(df["Period"], df[col], marker="o", linewidth=1.5, label=display_labels(col))

        ax.set_title("Indicator Trends Over Time")
        ax.set_xlabel("Month")
        ax.set_ylabel("Value")
        ax.set_facecolor("#f5f7fb")
        fig.patch.set_facecolor("#f5f7fb")
    
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

    with tab2:
        for col in indicator_columns:
            st.markdown(f"### {display_labels(col)}")

            fig, ax = plt.subplots(figsize=(10, 3.5))
            ax.plot(df["Period"], df[col], marker="o", linewidth=1.5)
            ax.set_title(display_labels(col))
            ax.set_xlabel("Month")
            ax.set_ylabel(display_labels(col))
            ax.set_facecolor("#f5f7fb")
            fig.patch.set_facecolor("#f5f7fb")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

    with tab3:
        latest_table = {
            "Indicator": [display_labels(col) for col in indicator_columns],
            "Latest Value": [format_value(col, latest[col]) for col in indicator_columns]
        }
        st.table(latest_table)

show_footer("Data: NHS England")