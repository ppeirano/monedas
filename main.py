import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Title and description
#st.title("Currency Comparison with DXY Index")
#st.write("Analyze and compare the DXY index with various global and emerging market currencies.")

# Default currencies to display
default_currencies = ["USDBRL=X", "EUR=X", "USDCNY=X", "EUR=X", "USDJPY=X"]

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
    "USDBRL=X", "USDARS=X", "USDCNY=X", "EURUSD=X", "USDJPY=X", "GBPUSD=X", "AUDUSD=X", "USDZAR=X",
    "USDINR=X", "USDMXN=X", "USDRUB=X", "Dolar Financiero (GGAL)", "EUR=X"
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
        currency_data[currency] = adr_data['Adj Close'] / local_data['Adj Close']
    else:
        data = yf.download(currency, start=start_date, end=end_date, interval=timeframe)
        currency_data[currency] = data['Adj Close']

# Plot the data in a grid layout using Plotly
st.write("### DXY Index and Selected Currencies")
figs = []

# Create a figure for DXY Index
fig = go.Figure()
fig.add_trace(go.Scatter(x=dxy.index, y=dxy['Adj Close'], mode='lines', name="DXY", line=dict(color='blue')))
fig.update_layout(
    title="DXY Index",
    xaxis_title="Date",
    yaxis_title="Value",
    template="plotly_white"
)
figs.append(fig)

# Create figures for each selected currency
for currency in selected_currencies:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=currency_data[currency].index, y=currency_data[currency], mode='lines', name=currency))
    fig.update_layout(
        title=currency,
        xaxis_title="Date",
        yaxis_title="Value",
        template="plotly_white"
    )
    figs.append(fig)

# Display figures in a grid layout (2 columns, 3 rows)
cols = 2
rows = (len(figs) + 1) // cols
for i in range(rows):
    cols_to_plot = figs[i * cols:(i + 1) * cols]
    col1, col2 = st.columns(2)
    for j, col in enumerate([col1, col2]):
        if j < len(cols_to_plot):
            with col:
                st.plotly_chart(cols_to_plot[j], use_container_width=True)

# Additional Data Table
st.write("### Raw Data")
all_data = pd.DataFrame()

all_data['DXY'] = dxy['Adj Close']
for currency in selected_currencies:
    all_data[currency] = currency_data[currency]

all_data = all_data[::-1]  # Reverse the order of the table
st.dataframe(all_data)

# Correlation Table
st.write("### Correlation Table")
correlation_data = all_data.corr()
st.dataframe(correlation_data)
