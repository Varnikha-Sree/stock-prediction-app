import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import datetime

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Stock Prediction App", layout="wide")
st.title("📈 Stock Price Prediction Dashboard")

# -------------------------------
# Sidebar Inputs
# -------------------------------
st.sidebar.header("User Input")

# Stock ticker input
ticker_symbol = st.sidebar.text_input("Enter Stock Ticker (e.g. AAPL, TSLA, TCS.NS):", "AAPL")

# Date range
start_date = st.sidebar.date_input("Start Date", datetime.date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# Prediction horizon
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
        # Plot Stock Prices
        # -------------------------------
        st.subheader("Stock Price Chart")
        st.line_chart(data["Close"])

        # -------------------------------
        # Prepare data for prediction
        # -------------------------------
        data = data.reset_index()
        data['Date_ordinal'] = pd.to_datetime(data['Date']).map(datetime.datetime.toordinal)

        X = np.array(data['Date_ordinal']).reshape(-1, 1)
        y = np.array(data['Close'])

        # Train simple linear regression
        model = LinearRegression()
        model.fit(X, y)

        # Predict future
        future_dates = [data['Date'].iloc[-1] + datetime.timedelta(days=i) for i in range(1, days_ahead+1)]
        future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
        future_preds = model.predict(future_ordinals)

        # -------------------------------
        # Show Predictions
        # -------------------------------
        st.subheader("Predicted Prices")
        pred_df = pd.DataFrame({"Date": future_dates, "Predicted Price": future_preds})
        st.write(pred_df)

        # -------------------------------
        # Plot Predictions
        # -------------------------------
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data["Date"], data["Close"], label="Historical Price", color="blue")
        ax.plot(future_dates, future_preds, label="Predicted Price", color="green", linestyle="dashed")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        st.pyplot(fig)

except Exception as e:
    st.error(f"Error fetching data: {e}")
