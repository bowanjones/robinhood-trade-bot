import yfinance as yf
import pandas as pd
import plotly.express as px

# Define the symbol (EUR/USD forex pair)
symbol = 'GOOG'

# Download historical data (daily data, adjust the period as needed)
df = yf.download(symbol, period="1y", interval="1d")  # Adjust period and interval as needed

# Display first few rows of data
print(df.head())

# Calculate RSI (Relative Strength Index)
rsi_period = 14

# Calculate daily gains and losses
df['gain'] = df['Close'].diff().clip(lower=0)  # Clip negative values to 0 for gains
df['loss'] = -df['Close'].diff().clip(upper=0)  # Clip positive values to 0 and negate for losses

# Exponential Moving Averages of gains and losses
df['ema_gain'] = df['gain'].ewm(span=rsi_period, min_periods=rsi_period).mean()
df['ema_loss'] = df['loss'].ewm(span=rsi_period, min_periods=rsi_period).mean()

# Relative Strength (RS)
df['rs'] = df['ema_gain'] / df['ema_loss']

# RSI Calculation
df['rsi_14'] = 100 - (100 / (df['rs'] + 1))

# Display results
print(df[['Close', 'rsi_14', 'rs', 'ema_gain', 'ema_loss']].tail())

# You can also plot the data (optional)
import plotly.graph_objects as go

fig = go.Figure()

# Add the candlestick chart
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name="Price"
))

# Add the RSI
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['rsi_14'],
    mode='lines',
    name='RSI',
    line=dict(color='orange', width=2),
    yaxis='y2'
))

# Update layout
fig.update_layout(
    title=f'{symbol} Price and RSI',
    xaxis_title='Date',
    yaxis_title='Price',
    yaxis2=dict(
        title='RSI',
        overlaying='y',
        side='right'
    ),
    xaxis_rangeslider_visible=False
)

fig.show()
