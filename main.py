import streamlit as st
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import BDay
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Función para ajustar fechas a días hábiles
def adjust_to_business_day(date):
    if pd.Timestamp(date).weekday() >= 5:  # Si es sábado o domingo
        return pd.Timestamp(date) + BDay(1)  # Mover al siguiente día hábil
    return pd.Timestamp(date)

# Función para descargar datos con fallback en fechas
@st.cache_data
def fetch_data_with_fallback(symbol, start_date, end_date, interval):
    attempts = 3
    for _ in range(attempts):
        data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
        if not data.empty:
            return data
        # Ajustar fechas si no hay datos
        start_date -= timedelta(days=2)
        end_date += timedelta(days=2)
    return pd.DataFrame()  # Devuelve un DataFrame vacío si no encuentra datos

# Sidebar settings
default_currencies = ["USDBRL=X", "Dolar Financiero (GGAL)", "USDCNY=X", "EUR=X", "USDJPY=X"]
st.sidebar.header("Settings")

# Rango de fechas
default_end_date = datetime.today()
default_start_date = default_end_date - timedelta(days=365)
date_range = st.sidebar.date_input("Select Date Range", [default_start_date, default_end_date])

start_date = adjust_to_business_day(date_range[0] if len(date_range) > 0 else default_start_date)
end_date = adjust_to_business_day(date_range[1] if len(date_range) > 1 else default_end_date)

# Intervalo de tiempo
timeframe = st.sidebar.selectbox("Select Timeframe", ["1d", "1wk", "1mo"], index=0)

# Selección de monedas
st.sidebar.header("Select Currencies")
currencies = [
    "USDBRL=X", "USDARS=X", "USDCNY=X", "EURUSD=X", "USDJPY=X", "GBPUSD=X", "AUDUSD=X", "USDZAR=X",
    "USDINR=X", "USDMXN=X", "USDRUB=X", "Dolar Financiero (GGAL)", "EUR=X"
]

selected_currencies = [
    st.sidebar.selectbox(f"Currency {i+1}", currencies, index=currencies.index(default))
    for i, default in enumerate(default_currencies)
]

# Descargar datos del índice DXY
dxy = fetch_data_with_fallback("DX-Y.NYB", start_date, end_date, interval=timeframe)

if 'Adj Close' in dxy.columns:
    dxy_adj_close = dxy['Adj Close']
else:
    st.warning("No 'Adj Close' data available for DXY.")
    dxy_adj_close = None

# Descargar datos de las monedas seleccionadas
currency_data = {}
for currency in selected_currencies:
    try:
        if currency == "Dolar Financiero (GGAL)":
            adr_data = fetch_data_with_fallback("GGAL", start_date, end_date, interval=timeframe)
            local_data = fetch_data_with_fallback("GGAL.BA", start_date, end_date, interval=timeframe)
            if not adr_data.empty and not local_data.empty:
                currency_data[currency] = adr_data['Adj Close'] / local_data['Adj Close']
            else:
                st.warning(f"No data available for {currency}.")
        else:
            data = fetch_data_with_fallback(currency, start_date, end_date, interval=timeframe)
            if 'Adj Close' in data.columns:
                currency_data[currency] = data['Adj Close']
            else:
                st.warning(f"No 'Adj Close' data available for {currency}.")
    except Exception as e:
        st.error(f"Error downloading data for {currency}: {e}")

# Gráficos con Plotly
st.write("### DXY Index and Selected Currencies")
figs = []

# Gráfico para el índice DXY
if dxy_adj_close is not None:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dxy.index, y=dxy_adj_close, mode='lines', name="DXY", line=dict(color='blue')))
    fig.update_layout(
        title="DXY Index",
        xaxis_title="Date",
        yaxis_title="Value",
        template="plotly_white"
    )
    figs.append(fig)

# Gráficos para las monedas seleccionadas
for currency, data in currency_data.items():
    if data is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines', name=currency))
        fig.update_layout(
            title=currency,
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_white"
        )
        figs.append(fig)

# Mostrar gráficos en una cuadrícula
cols = 2
rows = (len(figs) + 1) // cols
for i in range(rows):
    cols_to_plot = figs[i * cols:(i + 1) * cols]
    col1, col2 = st.columns(2)
    for j, col in enumerate([col1, col2]):
        if j < len(cols_to_plot):
            with col:
                st.plotly_chart(cols_to_plot[j], use_container_width=True)

# Tabla de datos crudos
st.write("### Raw Data")
all_data = pd.DataFrame()

if dxy_adj_close is not None:
    all_data['DXY'] = dxy_adj_close
for currency, data in currency_data.items():
    if data is not None:
        all_data[currency] = data

all_data = all_data[::-1]  # Invertir el orden
st.dataframe(all_data)

# Tabla de correlación
st.write("### Correlation Table")
correlation_data = all_data.corr()
st.dataframe(correlation_data)
