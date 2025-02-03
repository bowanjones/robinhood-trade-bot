import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

def fetch_and_analyze(symbol):
    # Get the current timestamp
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Download historical data (minute data)
    df = yf.download(symbol, period="1d", interval="1m")  # 1-minute interval for today
    print(f"Data fetched at: {current_timestamp}")
    
    # Calculate RSI (Relative Strength Index)
    rsi_period = 14
    
    # Calculate gains and losses
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

    # Plot the data (optional)
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
        title=f'{symbol} Price and RSI {current_timestamp}',
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

# Define the symbol (you can change this to any symbol)
symbol = 'GOOG'

# Run the function every minute (adjust sleep for different intervals)
while True:
    fetch_and_analyze(symbol)
    time.sleep(60)  # Sleep for 60 seconds (1 minute) before fetching again
