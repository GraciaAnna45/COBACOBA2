import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression

st.title("SEASONALITY & FORECASTING")

# ----------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------
@st.cache_data
def load_monthly():
    df = pd.read_csv("monthly_attributes_weighted_filtered.csv")
    df = df.sort_values("month").reset_index(drop=True)
    df["t"] = np.arange(len(df))
    return df

df = load_monthly()

TARGETS = [
    "avg_rating",
    "taste_weighted_sentiment",
    "price_weighted_sentiment",
    "service_weighted_sentiment",
    "ambience_weighted_sentiment",
    "hygiene_weighted_sentiment",
    "staff_weighted_sentiment"
]

st.sidebar.header("Forecast Settings")
target = st.sidebar.selectbox("Choose variable to forecast:", TARGETS)

# ----------------------------------------------------------
# FULL HISTORICAL TREND
# ----------------------------------------------------------
st.markdown("### Historical Trend (2015–2021)")

fig_hist = px.line(
    df, x="month", y=target, markers=True
)
fig_hist.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_hist, use_container_width=True)

# ----------------------------------------------------------
# FORECASTING
# ----------------------------------------------------------
st.markdown("### Forecast: Next 12 Months")

HORIZON = 12
TEST_SIZE = 12

train = df[:-TEST_SIZE]
test = df[-TEST_SIZE:]

model = LinearRegression()
model.fit(train[["t"]], train[target])

test_pred = model.predict(test[["t"]])

# metrics
MAE = mean_absolute_error(test[target], test_pred)
RMSE = np.sqrt(mean_squared_error(test[target], test_pred))
MAPE = np.mean(np.abs((test[target] - test_pred) / test[target])) * 100

# forecast future
last_t = df["t"].iloc[-1]
future_t = np.arange(last_t + 1, last_t + HORIZON + 1)
future_pred = model.predict(future_t.reshape(-1, 1))

future_df = pd.DataFrame({
    "month": [f"F+{i+1}" for i in range(HORIZON)],
    target: future_pred,
    "type": "Forecast"
})

hist_tail = df.tail(24)[["month", target]].copy()
hist_tail["type"] = "History"

plot_df = pd.concat([hist_tail, future_df])

fig_fc = px.line(
    plot_df,
    x="month",
    y=target,
    color="type",
    markers=True
)

fig_fc.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_fc, use_container_width=True)

# ----------------------------------------------------------
# INSIGHT SUMMARY CARD (PREMIUM)
# ----------------------------------------------------------

st.markdown("### Summary Insight")

# determine trend
trend = future_pred[-1] - future_pred[0]

if trend > 0.001:
    trend_label = "Increasing"
    trend_color = "#2ecc71"
elif trend < -0.001:
    trend_label = "Decreasing"
    trend_color = "#e74c3c"
else:
    trend_label = "Stable"
    trend_color = "#f1c40f"

# determine importance
last_value = df[target].iloc[-1]

if last_value > df[target].quantile(0.66):
    importance = "High"
elif last_value < df[target].quantile(0.33):
    importance = "Low"
else:
    importance = "Medium"

# determine action
if importance == "High" and trend_label == "Increasing":
    action = "Strong priority — improve & maintain consistency."
elif importance == "High" and trend_label == "Stable":
    action = "Maintain quality; monitor for early shifts."
elif importance == "Medium" and trend_label == "Increasing":
    action = "Potential future priority — keep an eye on it."
elif importance == "Low" and trend_label == "Increasing":
    action = "Growing but not urgent — observe trend."
elif importance == "High" and trend_label == "Decreasing":
    action = "Warning: important but declining — investigate issues."
else:
    action = "Low priority — limited impact for now."

# pretty card
st.markdown(f"""
<div style="
    padding:18px;
    background-color:#f8f9fa;
    border-radius:10px;
    border-left:6px solid {trend_color};
    font-size:16px;">
<b>Variable:</b> {target.replace('_', ' ').title()}<br>
<b>Trend:</b> {trend_label}<br>
<b>Current Importance:</b> {importance}<br>
<b>Model Error (MAPE):</b> {MAPE:.2f}%<br><br>
<b>Recommended Action:</b><br>
{action}
</div>
""", unsafe_allow_html=True)
