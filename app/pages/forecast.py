from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from utils import get_data, show_pressure, show_footer
from colourtheme import apply_styles

st.set_page_config(page_title="Forecast", layout="wide")

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
st.title("Forecast")

df = get_data()
months_ahead = st.slider("Months ahead", 1, 12, 3)

try:
    from prophet import Prophet

    prophet_df = df[["Period", "Pressure Score"]].rename(
        columns={"Period": "ds", "Pressure Score": "y"}
    )

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=months_ahead, freq="MS")
    forecast = model.predict(future)

    for column in ["yhat", "yhat_lower", "yhat_upper"]:
        forecast[column] = forecast[column].clip(0, 1)

    future_only = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(months_ahead)
    future_only = future_only.rename(columns={
        "ds": "Period",
        "yhat": "Forecast",
        "yhat_lower": "LB",
        "yhat_upper": "UB"
    })

    st.success("Using Prophet forecast.")

except Exception:
    x = np.arange(len(df))
    y = df["Pressure Score"].values

    slope, intercept = np.polyfit(x, y, 1)
    new_x = np.arange(len(df), len(df) + months_ahead)
    forecast_values = np.clip(slope * new_x + intercept, 0, 1)

    dates = pd.date_range(
        df["Period"].max() + pd.offsets.MonthBegin(1),
        periods=months_ahead,
        freq="MS"
    )

    future_only = pd.DataFrame({
        "Period": dates,
        "Forecast": forecast_values,
        "LB": np.clip(forecast_values - 0.05, 0, 1),
        "UB": np.clip(forecast_values + 0.05, 0, 1)
    })

    st.warning("Using linear trend fallback.")

last_forecast = future_only["Forecast"].iloc[-1]
first_forecast = future_only["Forecast"].iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Final", f"{last_forecast * 100:.0f}%")
col2.metric("Average", f"{future_only['Forecast'].mean() * 100:.0f}%")
col3.metric("Change", f"{(last_forecast - first_forecast) * 100:+.0f}%")

show_pressure(last_forecast)

display_df = future_only.copy()
display_df["Period"] = display_df["Period"].dt.strftime("%Y-%m")
for column in ["Forecast", "LB", "UB"]:
    display_df[column] = display_df[column].map(lambda value: f"{value * 100:.0f}%")

st.dataframe(display_df, hide_index=True, use_container_width=True)

fig, ax = plt.subplots(figsize=(8, 4))
forecast_percent = future_only["Forecast"] * 100
ax.plot(forecast_percent, linewidth=2.5)
ax.set_facecolor("white")
fig.patch.set_facecolor("#f5f7fb")

for i, value in enumerate(forecast_percent):
    ax.text(i, value + 0.5, f"{value:.0f}%", ha="center", fontsize=8)

ax.set_title(f"{months_ahead}-month forecast")
ax.set_xlabel("Step")
ax.set_ylabel("Pressure %")
ax.grid(True, alpha=0.3)
st.pyplot(fig)

show_footer("Forecast is a prediction, not real NHS data.")