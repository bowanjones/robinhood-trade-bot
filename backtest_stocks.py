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
def simple_backtest(symbol, start_date, end_date, initial_cash=10000, investment_per_stock=1000):
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
    
    # Track the number of active positions in the portfolio (max 5)
    active_stocks = 0
    max_active_stocks = 5

    total_gain_loss = 0  # Variable to track total gain/loss

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
        if cash >= investment_per_stock and position == 0 and current_rsi < 30 and active_stocks < max_active_stocks:
            position = investment_per_stock / current_close  # Buy the stock with $1,000 investment
            buy_price = current_close  # Store the buy price
            cash -= investment_per_stock  # Deduct $1,000 from cash
            active_stocks += 1  # Increase the active stock count
            cash_spent = buy_price * position
            print(f"\t\033[92mBuy\033[0m at {current_close:.2f} on {current_date}, Position: {position} shares, Cash Spent: \033[91m{cash_spent:.2f}\033[0m")

        # Sell when RSI is above 70
        elif position > 0 and current_rsi > 70:
            # Calculate the total cash from selling all shares
            cash_flow = current_close * position
            cash += cash_flow  # Add cash to portfolio from the sale
            gain_loss = (current_close - buy_price) * position  # Calculate the gain/loss on the sale
            total_gain_loss += gain_loss  # Add this transaction's gain/loss to total

            position = 0  # No position left
            active_stocks -= 1  # Decrease the active stock count

            # Print the sell result with cash gained
            if gain_loss > 0:
                print(f"\t\033[91mSell\033[0m at {current_close:.2f} on {current_date}, \033[92mGain:\033[0m {gain_loss:.2f}, Cash Flow: {cash_flow:.2f}, Total Cash: {cash:.2f}")
            elif gain_loss < 0:
                print(f"\t\033[91mSell\033[0m at {current_close:.2f} on {current_date}, \033[91mLoss:\033[0m {abs(gain_loss):.2f}, Cash Flow: {cash_flow:.2f}, Total Cash: {cash:.2f}")
            else:
                print(f"\t\033[91mSell\033[0m at {current_close:.2f} on {current_date}, \033[93mNo gain or loss, Cash Flow:\033[0m {cash_flow:.2f}, Total Cash: {cash:.2f}")

        # Append portfolio info for analysis
        history.append({'date': current_date, 'cash': cash, 'position': position, 'portfolio_value': portfolio_value})

    # In the 'simple_backtest' function, modify the final row calculation
    final_row = {
        'date': df.index[-1],  # Last date in the dataset
        'cash': cash,
        'position': position,  # Final stock position
        'portfolio_value': portfolio_value  # Final portfolio value (includes unsold stocks)
    }
    history.append(final_row)

    # Calculate the final portfolio value including unsold stocks
    if position > 0:
        # Calculate value of unsold stock at the current close price
        final_portfolio_value = cash + (position * df['Close'].iloc[-1].item())  # Value of unsold stocks + cash
    else:
        final_portfolio_value = cash  # If no stocks are left, just return cash

    # Calculate the percentage return
    percentage_return = ((final_portfolio_value - initial_cash) / initial_cash) * 100

    return pd.DataFrame(history), final_portfolio_value, total_gain_loss, percentage_return  # Return percentage return

# Function to backtest multiple stocks
def backtest_multiple_stocks(symbols, start_date, end_date, initial_cash=10000, investment_per_stock=1000):
    all_results = []  # To store the results for all stocks
    final_balances = {}  # To store the final portfolio values for each stock

    total_gain_loss_all = 0  # Variable to track the total gain/loss across all symbols
    symbol_percentage_returns = {}  # To store percentage returns for each symbol

    for symbol in symbols:
        print(f"\nStarting backtest for {symbol}...")
        df, final_value, total_gain_loss, percentage_return = simple_backtest(symbol, start_date, end_date, initial_cash, investment_per_stock)
        
        total_gain_loss_all += total_gain_loss  # Sum the total gain/loss for each stock

        # Store the percentage return for this symbol
        symbol_percentage_returns[symbol] = percentage_return

    # Print summary of all percentage returns at the end
    print("\nSummary of Percentage Returns for All Stocks:")
    for symbol, percentage_return in symbol_percentage_returns.items():
        print(f"{symbol}: {percentage_return:.2f}%")

    return total_gain_loss_all

# List of symbols to backtest
symbols = ['DOGE-USD']#['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'OKLO', 'SOUN', 'BBAI', 'GM', 'JOBY', 'ACHR', 'QUBT', 'QBTS', 'PLTR']

# Set the start and end dates for the backtest period
start_date = "2024-01-01"
end_date = "2025-02-07"

# Set initial cash and investment per stock as variables
initial_cash = 10000  
investment_per_stock = initial_cash * .2 #20% per max for risk management

# Run the backtest
total_gain_loss_all = backtest_multiple_stocks(symbols, start_date, end_date, initial_cash=initial_cash, investment_per_stock=investment_per_stock)+initial_cash
annual_growth = ((total_gain_loss_all-initial_cash)/initial_cash)*100
# Output total portfolio gain/loss from all symbols
print(f"\nTotal Portfolio Gain/Loss (all symbols): {total_gain_loss_all:.2f}")
print(f"Annual Growth Rate: {annual_growth:.2f}%")