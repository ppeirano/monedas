import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Title and description
#st.title("Currency Comparison with DXY Index")
#st.write("Analyze and compare the DXY index with various global and emerging market currencies.")

# Default currencies to display
default_currencies = ["USDBRL=X", "Dolar Financiero (GGAL)", "USDCNY=X", "EUR=X", "USDJPY=X"]

# Sidebar controls
st.sidebar.header("Settings")

# Date range selection
default_end_date = datetime.today()
default_start_date = default_end_date - timedelta(days=365)
date_range = st.sidebar.date_input("Select Date Range", [default_start_date, default_end_date])
start_date = date_range[0] if len(date_range) > 0 else default_start_date
end_date = date_range[1] if len(date_range) > 1 else default_end_date

# Timeframe selection
timeframe = st.sidebar.selectbox("Select Timeframe", ["1d", "1wk", "1mo"], index=0)

# Dropdown menus for currencies
st.sidebar.header("Select Currencies")
currencies = [
    "USDBRL=X", "Dolar Financiero (GGAL)", "USDCNY=X", "EURUSD=X", "USDJPY=X", "GBPUSD=X", "AUDUSD=X", "USDZAR=X",
    "USDINR=X", "USDMXN=X", "USDRUB=X", "EUR=X", "USDARS=X"
]

selected_currencies = [
    st.sidebar.selectbox(f"Currency {i+1}", currencies, index=currencies.index(default))
    for i, default in enumerate(default_currencies)
]

# Load DXY Index data
dxy = yf.download("DX-Y.NYB", start=start_date, end=end_date, interval=timeframe)

# Download data for selected currencies and calculate Dolar Financiero
currency_data = {}
for currency in selected_currencies:
    if currency == "Dolar Financiero (GGAL)":
        adr_data = yf.download("GGAL", start=start_date, end=end_date, interval=timeframe)
        local_data = yf.download("GGAL.BA", start=start_date, end=end_date, interval=timeframe)
        currency_data[currency] = local_data['Adj Close'] / adr_data['Adj Close'] * 10
    else:
        data = yf.download(currency, start=start_date, end=end_date, interval=timeframe)
        currency_data[currency] = data['Adj Close']

# Plot the data
st.write("### DXY Index and Selected Currencies")
num_plots = len(selected_currencies) + 1
rows = (num_plots + 1) // 2  # Calculate rows needed for a grid
fig, axs = plt.subplots(rows, 2, figsize=(12, rows * 4))

# Flatten axes for easy iteration
axs = axs.flatten()

# Plot DXY Index
axs[0].plot(dxy.index, dxy['Adj Close'], label="DXY", color="blue")
axs[0].set_title("DXY Index")
axs[0].legend()

# Plot selected currencies
for i, currency in enumerate(selected_currencies):
    axs[i+1].plot(currency_data[currency].index, currency_data[currency], label=currency, color="green")
    axs[i+1].set_title(currency)
    axs[i+1].legend()

# Remove unused subplots if any
for i in range(num_plots, len(axs)):
    fig.delaxes(axs[i])

fig.tight_layout()
st.pyplot(fig)

# Additional Data Table
st.write("### Raw Data")
all_data = pd.DataFrame()

all_data['DXY'] = dxy['Adj Close']
for currency in selected_currencies:
    all_data[currency] = currency_data[currency]

all_data = all_data[::-1]  # Reverse the order of the table
st.dataframe(all_data)
