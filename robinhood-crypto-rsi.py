import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timezone
import base64
import json
import uuid
import requests
from nacl.signing import SigningKey
import os
from dotenv import load_dotenv
from typing import Any, Dict, Optional

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE64_PRIVATE_KEY = os.getenv("BASE64_PRIVATE_KEY")

if not API_KEY or not BASE64_PRIVATE_KEY:
    raise ValueError("API_KEY or BASE64_PRIVATE_KEY not set in the environment variables.")


# Define CryptoAPITrading class for order placing
class CryptoAPITrading:
    def __init__(self):
        self.api_key = API_KEY
        private_key_seed = base64.b64decode(BASE64_PRIVATE_KEY)
        self.private_key = SigningKey(private_key_seed)
        self.base_url = "https://api.robinhood.com"  # Correct base URL for the API

    @staticmethod
    def _get_current_timestamp() -> int:
        return int(datetime.now(tz=timezone.utc).timestamp())

    @staticmethod
    def get_query_params(key: str, *args: Optional[str]) -> str:
        if not args:
            return ""

        params = []
        for arg in args:
            params.append(f"{key}={arg}")

        return "?" + "&".join(params)

    def make_api_request(self, method: str, path: str, body: str = "") -> Any:
        timestamp = self._get_current_timestamp() - 2
        headers = self.get_authorization_header(method, path, body, timestamp)
        url = self.base_url + path

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=json.loads(body), timeout=10)
            response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx, 5xx)
            return response.json()
        except requests.RequestException as e:
            print(f"Error making API request: {e}")
            return None

    def get_authorization_header(
            self, method: str, path: str, body: str, timestamp: int
    ) -> Dict[str, str]:
        message_to_sign = f"{self.api_key}{timestamp}{path}{method}{body}"
        signed = self.private_key.sign(message_to_sign.encode("utf-8"))

        return {
            "x-api-key": self.api_key,
            "x-signature": base64.b64encode(signed.signature).decode("utf-8"),
            "x-timestamp": str(timestamp),
        }

    def place_order(
            self,
            client_order_id: str,
            side: str,
            order_type: str,
            symbol: str,
            order_config: Dict[str, str],
    ) -> Any:
        body = {
            "client_order_id": client_order_id,
            "side": side,
            "type": order_type,
            "symbol": symbol,
            f"{order_type}_order_config": order_config,
        }
        path = "/api/v1/crypto/trading/orders/"
        return self.make_api_request("POST", path, json.dumps(body))


def fetch_and_analyze(symbol):
    # Get the current timestamp
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Download historical data (daily data instead of minute data)
    df = yf.download(symbol, period="200d", interval="1d")  # Use daily data for proper EMA, MACD, Bollinger Bands
    print(f"Data fetched at: {current_timestamp}")

    if df.empty:
        print("No data fetched. Skipping analysis.")
        return

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
    print(f"Latest RSI: {latest_rsi:.4f}")

    # Calculate 200-Day Exponential Moving Average (EMA)
    df['ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()

    # Calculate MACD (Moving Average Convergence Divergence)
    df['ema_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # Calculate Bollinger Bands
    df['rolling_mean'] = df['Close'].rolling(window=20).mean()
    df['rolling_std'] = df['Close'].rolling(window=20).std()
    df['bollinger_upper'] = df['rolling_mean'] + (df['rolling_std'] * 2)
    df['bollinger_lower'] = df['rolling_mean'] - (df['rolling_std'] * 2)

    # Get the latest values for all indicators
    latest_ema_200 = df['ema_200'].iloc[-1].item()  # Access last element and ensure it's a scalar
    latest_macd = df['macd'].iloc[-1].item()  # Access last element and ensure it's a scalar
    latest_macd_signal = df['macd_signal'].iloc[-1].item()  # Access last element and ensure it's a scalar
    latest_bollinger_upper = df['bollinger_upper'].iloc[-1].item()  # Access last element and ensure it's a scalar
    latest_bollinger_lower = df['bollinger_lower'].iloc[-1].item()  # Access last element and ensure it's a scalar
    latest_close = df['Close'].iloc[-1].item()  # Access last element and ensure it's a scalar


    print(f"Latest 200-day EMA: {latest_ema_200:.4f}")
    print(f"Latest MACD: {latest_macd:.4f}, Signal: {latest_macd_signal:.4f}")
    print(f"Latest Bollinger Bands - Upper: {latest_bollinger_upper:.4f}, Lower: {latest_bollinger_lower:.4f}")
    
    # Check for Buy/Sell conditions
    if latest_rsi < 30 and latest_close > latest_ema_200 and latest_macd > latest_macd_signal:
        print(f"\033[92mRSI below 30, above 200-day EMA, MACD bullish crossover. Buy signal! (Timestamp: {current_timestamp})\033[0m")
        # Place Buy Order
        place_order("buy", symbol)
        
    elif latest_rsi > 70 and latest_close < latest_ema_200 and latest_macd < latest_macd_signal:
        print(f"\033[91mRSI above 70, below 200-day EMA, MACD bearish crossover. Sell signal! (Timestamp: {current_timestamp})\033[0m")
        # Place Sell Order
        place_order("sell", symbol)

    # Check for Bollinger Bands breakout conditions
    elif latest_close > latest_bollinger_upper:
        print(f"\033[91mPrice above upper Bollinger Band. Possible overbought condition. Sell signal! (Timestamp: {current_timestamp})\033[0m")
        # Place Sell Order
        place_order("sell", symbol)
    elif latest_close < latest_bollinger_lower:
        print(f"\033[92mPrice below lower Bollinger Band. Possible oversold condition. Buy signal! (Timestamp: {current_timestamp})\033[0m")
        # Place Buy Order
        place_order("buy", symbol)
    else:
        print(f"RSI in neutral range and no other strong conditions. No action required. (Timestamp: {current_timestamp})")


# Function to place an order (Buy/Sell) using the CryptoAPITrading class
def place_order(side, symbol):
    api_trading_client = CryptoAPITrading()

    # Define order configuration (this example uses market orders)
    order_config = {"asset_quantity": "1"}  # Replace "1" with desired quantity

    # Place order
    order = api_trading_client.place_order(
        str(uuid.uuid4()),
        side,
        "market",
        symbol,
        order_config
    )

    if order:
        print(f"Order placed: {side} {symbol} with order ID {order.get('id')}")
    else:
        print("Failed to place the order.")

# Run the function every minute (adjust sleep for different intervals)
symbol = 'DOGE-USD'
while True:
    fetch_and_analyze(symbol)
    time.sleep(60)  # Sleep for 60 seconds (1 minute) before fetching again
