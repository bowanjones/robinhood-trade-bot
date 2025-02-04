# Crypto Trading Bot

A Python-based trading bot for executing cryptocurrency trades using the Robinhood API.

Navigate to lines 136-139 of the robinhood-api.py file to select your crypto for trading. For example:
          "sell",
          "market",
          "DOGE-USD",
          {"asset_quantity": "1"}

## Prerequisites

Before running the bot, make sure you have the following:

0. **Visual Studio Code:**
  - This is a personal preference but I find VS Code to be very user friendly. Download using the following:
  https://code.visualstudio.com/download

1. **Python 3.x**:
   Ensure you have Python 3.x installed. You can check this by running the following in bash/cmd/powershell:
   python --version
   - If this is not installed, run the following and install python from the microsoft store:
   python
   - Once installed you can now use python. Run the following command to test again:
   python --version
   
2. **Run key.py to generate your public and private keys:**
   - Command:
   python .\keys.py
   - Add these keys to your .env file to save for later
   - Use the following naming convention for the Private Key:
   BASE64_PRIVATE_KEY = ""
   
4. **Navigate to Robinhood and Generate an API Key:**
   - https://robinhood.com/account/crypto
   - select expiration date less than 1 year from today
   - select the actions you prefer (I selected all API actions)
   - Add your public key
   - save

5. **Save your API_KEY to .env:**
   - Add this newly generated API_KEY to your .env file
   - Use the following naming convention:
   API_KEY = ""

### Additional Info
https://docs.robinhood.com/crypto/trading/#section/Getting-Started

