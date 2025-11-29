# test_agent.py

from share_agent import create_market_agent  # Import your agent creation function
import json

# Initialize the agent
agent = create_market_agent()

# ------------------- Test Cases -------------------

# 1. Stock Price Lookup
print("\n=== STOCK PRICE ===")
response = agent.run("Get the latest price for RELIANCE")
print(response)

# 2. Stock History
print("\n=== STOCK HISTORY ===")
response = agent.run('Show 1 month daily history for TCS')
print(response)

# 3. Company Info
print("\n=== COMPANY INFO ===")
response = agent.run("Give me company info for INFY")
print(response)

# 4. Financials
print("\n=== FINANCIALS ===")
response = agent.run("Show financials for TCS")
print(response)

# 5. Dividends
print("\n=== DIVIDENDS ===")
response = agent.run("Get dividends for RELIANCE")
print(response)

# 6. Stock Splits
print("\n=== STOCK SPLITS ===")
response = agent.run("Show splits for TCS")
print(response)

# 7. IPO Calendar
print("\n=== IPO CALENDAR ===")
response = agent.run("Show upcoming IPOs")
print(response)

# 8. Mutual Fund Info
print("\n=== MUTUAL FUND ===")
response = agent.run("Get info for mutual fund scheme code 119551")
print(response)

# 9. Stock News
print("\n=== STOCK NEWS ===")
response = agent.run("Get latest news for RELIANCE")
print(response)

# 10. Market Overview
print("\n=== MARKET OVERVIEW ===")
response = agent.run("Give me current NIFTY, SENSEX, BANKNIFTY prices")
print(response)
