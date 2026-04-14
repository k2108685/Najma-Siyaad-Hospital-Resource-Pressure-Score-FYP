from pathlib import Path
import matplotlib.pyplot as plt
import streamlit as st
from utils import get_data, display_labels, format_value, show_pressure, show_footer
from colourtheme import apply_styles

st.set_page_config(page_title="HRPS Dashboard", layout="wide")

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

st.title("HRPS Dashboard")

df = get_data()
latest = df.iloc[-1]
score = float(latest["Pressure Score"])
previous = float(df.iloc[-2]["Pressure Score"]) if len(df) > 1 else score

col1, col2, col3 = st.columns(3)
col1.metric("Current Pressure Score", f"{score:.2f}")
col2.metric("Current Period", latest["Period"].strftime("%b %Y"))
col3.metric("Previous Period Score", f"{previous:.2f}")

show_pressure(score)

st.subheader("Pressure Score Over Time")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["Period"], df["Pressure Score"], marker="o", linewidth=2)
ax.axhline(0.75, linestyle="--", alpha=0.7, label="Critical")
ax.axhline(0.55, linestyle="--", alpha=0.7, label="High")
ax.set_ylim(0, 1)
ax.set_xlabel("Month")
ax.set_ylabel("Pressure Score")
ax.set_facecolor("white")
fig.patch.set_facecolor("#f5f7fb")
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

indicators = [
    c for c in [
        "Total Attendances",
        "Total Emergency Admissions",
        "Patients Waiting Over 4 Hours for Admission",
        "Percentage of Patients Seen Within 4 Hours",
        "Occupancy Rate"
    ]
    if c in df.columns
]

if indicators:
    tab1, tab2 = st.tabs(["Trends", "Latest"])

    with tab1:
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        for column in indicators:
            ax2.plot(df["Period"], df[column], marker="o", linewidth=2, label=display_labels(column))
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Value")
        ax2.set_title("Underlying Indicators")
        ax2.set_facecolor("white")
        fig2.patch.set_facecolor("#f5f7fb")
        ax2.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig2)

    with tab2:
        st.dataframe(
            [{"Indicator": display_labels(column), "Latest": format_value(column, latest[column])} for column in indicators],
            hide_index=True,
            use_container_width=True
        )

show_footer("Data: NHS England")