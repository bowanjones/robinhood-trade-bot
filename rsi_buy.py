import yfinance as yf
import pandas as pd
import time
from datetime import datetime

def fetch_and_analyze(symbol):
    # Get the current timestamp
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Download historical data (minute data)
    df = yf.download(symbol, period="1d", interval="1h")  # 1-minute interval for today
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
    
    # Get the latest RSI value
    latest_rsi = df['rsi_14'].iloc[-1]
    print(f"Latest RSI: {latest_rsi:.2f}")
    
    # Check for Buy/Sell conditions based on RSI
    if latest_rsi < 30:
        print(f"\033[92mRSI below 30. Buy signal! (Timestamp: {current_timestamp})\033[0m")
    elif latest_rsi > 70:
        print(f"\033[91mRSI above 70. Sell signal! (Timestamp: {current_timestamp})\033[0m")
    else:
        print(f"RSI is in neutral range. No action required. (Timestamp: {current_timestamp})")

# Define the symbol (you can change this to any symbol)
symbol = 'DOGE-USD'

# Run the function every minute (adjust sleep for different intervals)
while True:
    fetch_and_analyze(symbol)
    time.sleep(60)  # Sleep for 60 seconds (1 minute) before fetching again
