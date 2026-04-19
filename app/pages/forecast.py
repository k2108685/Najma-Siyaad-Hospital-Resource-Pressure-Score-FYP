from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from utils import get_data, get_pressure, show_pressure, show_footer
from colourtheme import apply_styles

st.set_page_config(page_title="Forecast", layout="wide")
apply_styles()

LOGO = Path(__file__).resolve().parent.parent / "logo" / "nhs_logo.png"

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

st.title("Pressure Forecast")
st.write("This page estimates future hospital pressure levels based on the trends in the historical pressure scores.")

#load the pressure score data 
try:
    df = get_data()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

if "Period" not in df.columns or "Pressure Score" not in df.columns:
    st.error("Processed CSV must contain 'Period' and 'Pressure Score' columns.")
    st.stop()

months_ahead = st.slider(
    "Months to forecast",
    min_value=1,
    max_value=12,
    value=3,
    step=1,
)
#use if prophet is installed or use linear trend
use_prophet = False
try:
    from prophet import Prophet
    use_prophet = True
except ImportError:
    pass

st.caption("Forecast based on historical trends.")

# Prophet uses past  patterns to estimate future scores
if use_prophet:
    prophet_df = df[["Period", "Pressure Score"]].rename(
        columns={"Period": "ds", "Pressure Score": "y"}
    )

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
    )
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=months_ahead, freq="MS")
    forecast_df = model.predict(future)

    forecast_df["yhat"] = forecast_df["yhat"].clip(0, 1)
    forecast_df["yhat_lower"] = forecast_df["yhat_lower"].clip(0, 1)
    forecast_df["yhat_upper"] = forecast_df["yhat_upper"].clip(0, 1)

    future_only = forecast_df[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(months_ahead).copy()
    future_only = future_only.rename(
        columns={
            "ds": "Period",
            "yhat": "Forecast",
            "yhat_lower": "Lower Bound",
            "yhat_upper": "Upper Bound",
        }
    )
    #or use a basic linear trend line as a forecast
else:
    forecast_df_lr = df.copy()
    forecast_df_lr["TimeIndex"] = range(len(forecast_df_lr))

    x = forecast_df_lr["TimeIndex"].values
    y = forecast_df_lr["Pressure Score"].values

    slope, intercept = np.polyfit(x, y, 1)

    future_index_start = len(df)
    future_indices = list(range(future_index_start, future_index_start + months_ahead))
    future_dates = pd.date_range(
        df["Period"].max() + pd.offsets.MonthBegin(1),
        periods=months_ahead,
        freq="MS",
    )

    forecast_values = np.clip(np.array([slope * i + intercept for i in future_indices]), 0, 1)
    lower_bounds = np.clip(forecast_values - 0.05, 0, 1)
    upper_bounds = np.clip(forecast_values + 0.05, 0, 1)

    future_only = pd.DataFrame(
        {
            "Period": future_dates,
            "Forecast": forecast_values,
            "Lower Bound": lower_bounds,
            "Upper Bound": upper_bounds,
        }
    )
#calcaute summary values 
latest_forecast = float(future_only["Forecast"].iloc[-1])
start_forecast = float(future_only["Forecast"].iloc[0])
forecast_change = latest_forecast - start_forecast
avg_forecast = float(future_only["Forecast"].mean())

st.markdown("## Forecast Summary")

c1, c2, c3 = st.columns(3)
c1.metric("Final Forecast", f"{latest_forecast * 100:.0f}%")
c2.metric("Average Forecast", f"{avg_forecast * 100:.0f}%")
c3.metric("Forecast Change", f"{forecast_change * 100:+.0f}%")

show_pressure(latest_forecast)

#plot forecast chart 
st.markdown("## Forecast Chart")

plot_df = future_only.copy()
plot_df["Label"] = plot_df["Period"].dt.strftime("%Y-%m")
plot_df["ForecastPct"] = plot_df["Forecast"] * 100

fig, ax = plt.subplots(figsize=(8, 4), dpi=100)

x = range(len(plot_df))

ax.plot(
    x,
    plot_df["ForecastPct"],
    linewidth=2.5,
    label="Forecast"
)

ax.fill_between(
    x,
    plot_df["Lower Bound"] * 100,
    plot_df["Upper Bound"] * 100,
    alpha=0.2,
    label="Confidence Interval"
)

for i, v in enumerate(plot_df["ForecastPct"]):
    ax.text(i, v + 0.3, f"{v:.0f}%", ha="center", fontsize=9)

ax.set_title(f"HRPS Forecast : Next {months_ahead} Month(s)")
ax.set_xlabel("Forecast Period")
ax.set_ylabel("Pressure Score (%)")
ax.set_xticks(list(x))
ax.set_xticklabels(plot_df["Label"])
ax.set_ylim(
    max(0, plot_df["ForecastPct"].min() - 3),
    min(100, plot_df["ForecastPct"].max() + 3),
)
ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
ax.legend()

plt.xticks(rotation=0)
st.pyplot(fig)
plt.close(fig)



st.markdown("## Forecast Breakdown")

for _, row in future_only.iterrows():
    st.markdown(f"### {row['Period'].strftime('%Y-%m')}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Forecast", f"{row['Forecast'] * 100:.0f}%")
    c2.metric("Lower Bound", f"{row['Lower Bound'] * 100:.0f}%")
    c3.metric("Upper Bound", f"{row['Upper Bound'] * 100:.0f}%")

forecast_change_vs_latest_actual = latest_forecast - float(df["Pressure Score"].iloc[-1])

st.markdown("## Forecast Interpretation")

forecast_change_vs_latest_actual = latest_forecast - float(df["Pressure Score"].iloc[-1])
final_forecast_score = latest_forecast
final_label = get_pressure(final_forecast_score)

if forecast_change_vs_latest_actual > 0:
    st.write(
        f"The forecast suggests that hospital pressure is expected to **increase** over the next "
        f"{months_ahead} months, reaching a predicted score of **{final_forecast_score * 100:.0f}%** "
        f"({final_label}). This shows that demand on emergency services is likely to continue rising. "
        f"NHS planners may need to consider proactive resource allocation in advance of this period."
    )
elif forecast_change_vs_latest_actual < 0:
    st.write(
        f"The forecast suggests that hospital pressure is expected to **decrease** over the next "
        f"{months_ahead} months, reaching a predicted score of **{final_forecast_score * 100:.0f}%** "
        f"({final_label}). This shows a potential easing of demand on emergency services. "
        f"However, forecasts are not certain and things can change rapidly."
    )
else:
    st.write(
        f"The forecast suggests a relatively **stable** pressure level over the next "
        f"{months_ahead} months, with a predicted score of **{final_forecast_score * 100:.0f}%** "
        f"({final_label}). Continued monitoring is recommended as seasonal patterns may cause "
        f"some changes within this period."
    )



show_footer("NHS Hospital Resource Pressure System — Data sourced from NHS England open data")