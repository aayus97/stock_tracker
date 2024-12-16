import streamlit as st
from tracker import MeroLaganiStockTracker
import plotly.express as px


# Initialize tracker
tracker = MeroLaganiStockTracker()

st.title("Mero Lagani Stock Tracker")
st.sidebar.header("Settings")

# User inputs
stocks_to_track = st.sidebar.text_input("Stocks to Track (comma-separated)", "NABIL, NRIC, PRVU").split(",")
threshold_price = st.sidebar.number_input("Threshold Price", min_value=0.0, value=1000.0)

# Display all stock prices
if st.button("Fetch Latest Prices"):
    stock_data = tracker.get_stock_prices()
    if stock_data is not None:
        st.write("All Stock Prices", stock_data)
    else:
        st.error("Failed to fetch stock data.")

# Display tracked stocks
if st.button("Track Selected Stocks"):
    tracked_data = tracker.track_stocks(stocks_to_track)
    if tracked_data is not None:
        st.write(f"Tracked Stocks: {stocks_to_track}", tracked_data)
    else:
        st.warning("No data found for the selected stocks.")

# Set alerts for stocks
if st.button("Set Alerts"):
    for stock in stocks_to_track:
        tracker.set_alert(stock, threshold_price, direction="up")
        st.success(f"Alert set for {stock} at price {threshold_price}")


# Add historical tracking
if st.sidebar.checkbox("Enable Historical Tracking"):
    if st.button("Save Current Data to History"):
        stock_data = tracker.get_stock_prices()
        if stock_data is not None:
            tracker.save_to_history(stock_data)
            st.success("Stock data saved to history.")
        else:
            st.error("Failed to fetch stock data for saving.")

# Visualize historical data
if st.sidebar.checkbox("Show Historical Trends"):
    history_data = tracker.load_history()
    if history_data is not None:
        # Filter for tracked stocks
        tracked_history = history_data[history_data["Symbol"].isin(stocks_to_track)]

        # Plot historical trends
        if not tracked_history.empty:
            st.subheader("Stock Price Trends")
            fig = px.line(
                tracked_history,
                x="Date",  # Ensure the 'Date' column is included in saved data
                y="LTP",
                color="Symbol",
                title="Stock Price Trends Over Time",
            )
            st.plotly_chart(fig)
        else:
            st.warning("No historical data available for selected stocks.")
    else:
        st.warning("No historical data found.")