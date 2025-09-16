import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import datetime

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Stock Prediction App", layout="wide")
st.title("📈 Stock Price Prediction Dashboard (Animated)")

# -------------------------------
# Sidebar Inputs
# -------------------------------
st.sidebar.header("User Input")

ticker_symbol = st.sidebar.text_input("Enter Stock Ticker (e.g. AAPL, TSLA, TCS.NS):", "AAPL")
start_date = st.sidebar.date_input("Start Date", datetime.date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())
days_ahead = st.sidebar.slider("Predict days into future:", 1, 30, 7)

# -------------------------------
# Fetch Data
# -------------------------------
st.subheader(f"Stock Data for {ticker_symbol}")

try:
    data = yf.download(ticker_symbol, start=start_date, end=end_date)

    if data.empty:
        st.error("No data found for this ticker. Try another symbol.")
    else:
        st.write(data.tail())

        # -------------------------------
        # Prediction
        # -------------------------------
        data = data.reset_index()
        data['Date_ordinal'] = pd.to_datetime(data['Date']).map(datetime.datetime.toordinal)

        X = np.array(data['Date_ordinal']).reshape(-1, 1)
        y = np.array(data['Close'])

        model = LinearRegression()
        model.fit(X, y)

        # Predict future
        future_dates = [data['Date'].iloc[-1] + datetime.timedelta(days=i) for i in range(1, days_ahead+1)]
        future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
        future_preds = model.predict(future_ordinals)

        pred_df = pd.DataFrame({"Date": future_dates, "Predicted Price": future_preds})
        st.subheader("Predicted Prices")
        st.write(pred_df)

        # -------------------------------
        # Animated Plotly Chart
        # -------------------------------
        fig = go.Figure()

        # Historical Line
        fig.add_trace(go.Scatter(
            x=data["Date"], y=data["Close"],
            mode="lines",
            name="Historical Price",
            line=dict(color="royalblue", width=2)
        ))

        # Prediction Line (Animated)
        fig.add_trace(go.Scatter(
            x=pred_df["Date"], y=pred_df["Predicted Price"],
            mode="lines+markers",
            name="Predicted Price",
            line=dict(color="limegreen", width=3, dash="dash")
        ))

        # Animation frames (simulate slow stock movement)
        frames = [
            go.Frame(
                data=[go.Scatter(x=pred_df["Date"][:k], y=pred_df["Predicted Price"][:k])],
                name=str(k)
            )
            for k in range(1, len(pred_df)+1)
        ]

        fig.frames = frames

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Stock Price (USD)",
            template="plotly_dark",
            updatemenus=[{
                "type": "buttons",
                "buttons": [
                    {"label": "▶ Play", "method": "animate", "args": [None, {"frame": {"duration": 800, "redraw": True}, "fromcurrent": True}]},
                    {"label": "⏸ Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}]}
                ]
            }]
        )

        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching data: {e}")

