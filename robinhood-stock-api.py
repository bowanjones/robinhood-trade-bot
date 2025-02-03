import base64
import datetime
import json
from typing import Any, Dict, Optional
import uuid
import requests
from nacl.signing import SigningKey
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE64_PRIVATE_KEY = os.getenv("BASE64_PRIVATE_KEY")

class APITrading:
    def __init__(self):
        self.api_key = API_KEY
        private_key_seed = base64.b64decode(BASE64_PRIVATE_KEY)
        self.private_key = SigningKey(private_key_seed)
        self.base_url = "https://api.robinhood.com"  # Use Robinhood's base URL

    @staticmethod
    def _get_current_timestamp() -> int:
        return int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

    @staticmethod
    def get_query_params(key: str, *args: Optional[str]) -> str:
        if not args:
            return ""
        params = [f"{key}={arg}" for arg in args]
        return "?" + "&".join(params)

    def make_api_request(self, method: str, path: str, body: str = "") -> Any:
        timestamp = self._get_current_timestamp() - 2
        headers = self.get_authorization_header(method, path, body, timestamp)
        url = self.base_url + path
        try:
            response = requests.request(method, url, headers=headers, json=json.loads(body) if body else None, timeout=10)
            return response.json()
        except requests.RequestException as e:
            print(f"Error making API request: {e}")
            return None

    def get_authorization_header(self, method: str, path: str, body: str, timestamp: int) -> Dict[str, str]:
        message_to_sign = f"{self.api_key}{timestamp}{path}{method}{body}"
        signed = self.private_key.sign(message_to_sign.encode("utf-8"))
        return {
            "x-api-key": self.api_key,
            "x-signature": base64.b64encode(signed.signature).decode("utf-8"),
            "x-timestamp": str(timestamp),
        }

    def get_account(self) -> Any:
        path = "/api/v1/portfolio/"  # Adjusted for stock portfolio
        return self.make_api_request("GET", path)

    def get_orders(self) -> Any:
        path = "/api/v1/orders/"  # Adjusted for stock orders
        return self.make_api_request("GET", path)

    def get_holdings(self, *asset_codes: Optional[str]) -> Any:
        query_params = self.get_query_params("symbol", *asset_codes)  # "symbol" for stock
        path = f"/api/v1/portfolio/holdings/{query_params}"
        return self.make_api_request("GET", path)

    def place_stock_order(self, client_order_id: str, side: str, order_type: str, symbol: str, order_config: Dict[str, str]) -> Any:
        body = {
            "client_order_id": client_order_id,
            "side": side,
            "type": order_type,
            "symbol": symbol,
            f"{order_type}_order_config": order_config,
        }
        path = "/api/v1/orders/"  # Corrected path for stock orders
        return self.make_api_request("POST", path, json.dumps(body))

def main():
    api_trading_client = APITrading()
    print(api_trading_client.get_account())
    
    order = api_trading_client.place_stock_order(
          str(uuid.uuid4()),
          "buy",  # Example: "buy" or "sell"
          "market",  # Order type, e.g., "market"
          "BBAI",  # Stock symbol
          {"quantity": "1"}  # Example: quantity of stock to buy/sell
    )

if __name__ == "__main__":
    main()
