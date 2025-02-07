import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# Function to calculate RSI
def calculate_rsi(df, rsi_period=14):
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

    return df['rsi_14'].iloc[-1]  # Return the latest RSI value


def fetch_and_analyze(symbol):
    # Get the current timestamp
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Download data for different timeframes (daily, weekly, hourly)
    try:
        df_daily = yf.download(symbol, period="200d", interval="1d", progress=False)  # Daily data
        df_weekly = yf.download(symbol, period="200d", interval="1wk", progress=False)  # Weekly data
        df_hourly = yf.download(symbol, period="200d", interval="1mo", progress=False)  # hourly data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None  # Skip if there's an error in fetching the data

    if df_daily.empty or df_weekly.empty or df_hourly.empty:
        print(f"No data for {symbol}. Skipping...")
        return None  # Skip if no data

    # Calculate RSI for daily, weekly, and hourly
    latest_rsi_daily = calculate_rsi(df_daily)
    latest_rsi_weekly = calculate_rsi(df_weekly)
    latest_rsi_hourly = calculate_rsi(df_hourly)
    
    # Calculate 200-Day Exponential Moving Average (EMA)
    df_daily['ema_200'] = df_daily['Close'].ewm(span=200, adjust=False).mean()

    # Calculate MACD (Moving Average Convergence Divergence)
    df_daily['ema_12'] = df_daily['Close'].ewm(span=12, adjust=False).mean()
    df_daily['ema_26'] = df_daily['Close'].ewm(span=26, adjust=False).mean()
    df_daily['macd'] = df_daily['ema_12'] - df_daily['ema_26']
    df_daily['macd_signal'] = df_daily['macd'].ewm(span=9, adjust=False).mean()

    # Calculate Bollinger Bands
    df_daily['rolling_mean'] = df_daily['Close'].rolling(window=20).mean()
    df_daily['rolling_std'] = df_daily['Close'].rolling(window=20).std()
    df_daily['bollinger_upper'] = df_daily['rolling_mean'] + (df_daily['rolling_std'] * 2)
    df_daily['bollinger_lower'] = df_daily['rolling_mean'] - (df_daily['rolling_std'] * 2)

    # Get the latest values for all indicators
    latest_ema_200 = df_daily['ema_200'].iloc[-1].item()  # Access last element and ensure it's a scalar
    latest_macd = df_daily['macd'].iloc[-1].item()  # Access last element and ensure it's a scalar
    latest_macd_signal = df_daily['macd_signal'].iloc[-1].item()  # Access last element and ensure it's a scalar
    latest_bollinger_upper = df_daily['bollinger_upper'].iloc[-1].item()  # Access last element and ensure it's a scalar
    latest_bollinger_lower = df_daily['bollinger_lower'].iloc[-1].item()  # Access last element and ensure it's a scalar
    latest_close = df_daily['Close'].iloc[-1].item()  # Access last element and ensure it's a scalar

    # Check for Buy/Sell conditions
    if latest_rsi_daily < 30 and latest_close > latest_ema_200 and latest_macd > latest_macd_signal:
        # Print values for all timeframes
        print(f"\t{symbol} Latest RSI Daily: {latest_rsi_daily:.4f}, Weekly: {latest_rsi_weekly:.4f}, Hourly: {latest_rsi_hourly:.4f}")
        print(f"\t{symbol} Latest 200-day EMA: {latest_ema_200:.4f}, MACD: {latest_macd:.4f}, Signal: {latest_macd_signal:.4f}")
        print(f"\t{symbol} Bollinger Bands - Upper: {latest_bollinger_upper:.4f}, Lower: {latest_bollinger_lower:.4f}")
        print(f"\t\033[92m{symbol}: Buy signal! RSI below 30, above 200-day EMA, MACD bullish crossover. (Timestamp: {current_timestamp})\033[0m")
        return "buy"
        
    elif latest_rsi_daily > 70 and latest_close < latest_ema_200 and latest_macd < latest_macd_signal:
        # Print values for all timeframes
        print(f"\t{symbol} Latest RSI Daily: {latest_rsi_daily:.4f}, Weekly: {latest_rsi_weekly:.4f}, Hourly: {latest_rsi_hourly:.4f}")
        print(f"\t{symbol} Latest 200-day EMA: {latest_ema_200:.4f}, MACD: {latest_macd:.4f}, Signal: {latest_macd_signal:.4f}")
        print(f"\t{symbol} Bollinger Bands - Upper: {latest_bollinger_upper:.4f}, Lower: {latest_bollinger_lower:.4f}")
        print(f"\t\033[91m{symbol}: Sell signal! RSI above 70, below 200-day EMA, MACD bearish crossover. (Timestamp: {current_timestamp})\033[0m")
        return "sell"

    # Check for Bollinger Bands breakout conditions
    elif latest_close > latest_bollinger_upper:
        # Print values for all timeframes
        print(f"\t{symbol} Latest RSI Daily: {latest_rsi_daily:.4f}, Weekly: {latest_rsi_weekly:.4f}, Hourly: {latest_rsi_hourly:.4f}")
        print(f"\t{symbol} Latest 200-day EMA: {latest_ema_200:.4f}, MACD: {latest_macd:.4f}, Signal: {latest_macd_signal:.4f}")
        print(f"\t{symbol} Bollinger Bands - Upper: {latest_bollinger_upper:.4f}, Lower: {latest_bollinger_lower:.4f}")
        print(f"\t\033[91m{symbol}: Sell signal! Price above upper Bollinger Band. Possible overbought condition. (Timestamp: {current_timestamp})\033[0m")
        return "sell"
    elif latest_close < latest_bollinger_lower:
        # Print values for all timeframes
        print(f"\t{symbol} Latest RSI Daily: {latest_rsi_daily:.4f}, Weekly: {latest_rsi_weekly:.4f}, Hourly: {latest_rsi_hourly:.4f}")
        print(f"\t{symbol} Latest 200-day EMA: {latest_ema_200:.4f}, MACD: {latest_macd:.4f}, Signal: {latest_macd_signal:.4f}")
        print(f"\t{symbol} Bollinger Bands - Upper: {latest_bollinger_upper:.4f}, Lower: {latest_bollinger_lower:.4f}")
        print(f"\t\033[92m{symbol}: Buy signal! Price below lower Bollinger Band. Possible oversold condition. (Timestamp: {current_timestamp})\033[0m")
        return "buy"
    else:
        return "hold"


def analyze_multiple_symbols(symbols):
    for symbol in symbols:
        action = fetch_and_analyze(symbol)
        if action:
            print(f"{symbol}: {action}")
        else:
            print(f"No action for {symbol}")

# List of symbols to analyze
symbols_to_analyze = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'OKLO', 'SOUN', 'BBAI', 'WW', 'GM', 'JOBY', 'ACHR', 'APLD', 'QUBT', 'QBTS', 'ARBE', 'PLTR']

# Run the analysis on all symbols in the list
while True:
    print("Starting a new iteration...")
    analyze_multiple_symbols(symbols_to_analyze)
    time.sleep(60)  # Sleep for 60 seconds (1 minute) before fetching again
