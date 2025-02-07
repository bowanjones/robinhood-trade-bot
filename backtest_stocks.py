import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Function to calculate 14-period RSI
def calculate_rsi(df, period=14):
    delta = df['Close'].diff()  # Calculate price changes
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()  # Calculate gains
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()  # Calculate losses
    rs = gain / loss  # Calculate relative strength
    rsi = 100 - (100 / (1 + rs))  # Calculate RSI
    df['RSI'] = rsi
    return df

# Simple function to simulate a backtest with cash value and strategy conditions
def simple_backtest(symbol, start_date, end_date, initial_cash=10000):
    # Download historical data for the backtest period
    df = yf.download(symbol, start=start_date, end=end_date, progress=False)
    
    if df.empty:
        print(f"No data for {symbol}. Skipping...")
        return None

    # Calculate RSI
    df = calculate_rsi(df)

    # Initialize the portfolio and cash tracking
    cash = initial_cash
    position = 0
    portfolio_value = cash  # Start with initial cash
    history = []  # To track the cash and portfolio value at each step
    buy_price = 0  # To store the price when a buy is made

    print(f"Data for {symbol} from {start_date} to {end_date}:")

    # Loop through the historical data and simulate buying/selling actions
    for i in range(1, len(df)):
        current_date = df.index[i]
        current_close = df['Close'].iloc[i]
        current_rsi = df['RSI'].iloc[i]

        # Ensure that the values are scalars (not pandas Series)
        current_close = current_close.item() if isinstance(current_close, pd.Series) else current_close
        current_rsi = current_rsi.item() if isinstance(current_rsi, pd.Series) else current_rsi

        # Track the portfolio value (cash + value of current holdings)
        portfolio_value = cash + (position * current_close)

        # Ensure cash is treated as a scalar and no ambiguity occurs
        if isinstance(cash, pd.Series):
            cash = cash.item()  # Convert to scalar if it's a Series

        # Buy when RSI is below 30 and there's enough cash to buy
        if cash >= current_close and position == 0 and current_rsi < 30:
            position = cash / current_close  # Buy the stock
            buy_price = current_close  # Store the buy price
            cash = 0  # All cash is used for buying
            cash_spent = buy_price * position
            print(f"\t\033[92mBuy at {current_close}, Position: {position} shares, Cash Spent: {cash_spent:.2f} \033[0m")

        # Sell when RSI is above 70
        elif position > 0 and current_rsi > 70:
            cash = position * current_close  # Sell all stock at the current close price
            position = 0  # No position left

            # Calculate the gain/loss on the sale
            gain_loss = cash - (position * buy_price)
            if gain_loss > 0:
                print(f"\t\033[91mSell at {current_close}, Gain: {gain_loss:.2f}, Cash: {cash}\033[0m")
            elif gain_loss < 0:
                print(f"\t\033[91mSell at {current_close}, Loss: {abs(gain_loss):.2f}, Cash: {cash}\033[0m")
            else:
                print(f"\t\033[91mSell at {current_close}, No gain or loss, Cash: {cash}\033[0m")

        # Append portfolio info for analysis
        history.append({'date': current_date, 'cash': cash, 'position': position, 'portfolio_value': portfolio_value})

    return pd.DataFrame(history)

# Function to backtest multiple stocks
def backtest_multiple_stocks(symbols, start_date, end_date, initial_cash=10000):
    all_results = []  # To store the results for all stocks

    for symbol in symbols:
        print(f"\nStarting backtest for {symbol}...")
        df = simple_backtest(symbol, start_date, end_date, initial_cash)

        if df is not None:
            df['symbol'] = symbol  # Add a column to track the symbol
            all_results.append(df)  # Add the result for this stock

    # Combine all results into a single DataFrame
    return pd.concat(all_results, ignore_index=True) if all_results else None

# List of symbols to backtest
symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'OKLO', 'SOUN', 'BBAI', 'WW', 'GM', 'JOBY', 'ACHR', 'APLD', 'QUBT', 'QBTS', 'ARBE', 'PLTR']

# Set the start and end dates for the backtest period
start_date = "2025-02-06"
end_date = "2025-02-07"

# Set initial cash to $10,000
results = backtest_multiple_stocks(symbols, start_date, end_date, initial_cash=1000)

# Print the final results
if results is not None:
    for symbol in symbols:
        symbol_results = results[results['symbol'] == symbol]
        total_return = (symbol_results['portfolio_value'].iloc[-1] - 1000) / 1000 * 100
        print(f"Total Return for {symbol}: {total_return:.2f}%")
