# """
# 🧩 Test File for All 12 ShareBot Tools
# Run:  python tool_test.py (from src/sharebot/tools/ directory)
#       OR python -m src.sharebot.tools.tool_test (from project root)
# Make sure:
#   1️⃣ market_tools.py is in the same directory.
#   2️⃣ .env file has a valid GNEWS_API_KEY.
# """

# try:
#     # Try importing from same directory (when running from tools/)
#     from market_tools import (
#         get_price,
#         get_history,
#         get_company_info,
#         get_financials,
#         get_stock_news,
#         get_market_overview,
#         get_stock_analysis,
#         track_portfolio,
#         get_ipo_calendar,
#         get_dividends,
#         get_splits,
#         get_mutual_fund_info,
#     )
# except ImportError:
#     # Try importing as module (when running from project root)
#     from src.sharebot.tools.market_tools import (
#         get_price,
#         get_history,
#         get_company_info,
#         get_financials,
#         get_stock_news,
#         get_market_overview,
#         get_stock_analysis,
#         track_portfolio,
#         get_ipo_calendar,
#         get_dividends,
#         get_splits,
#         get_mutual_fund_info,
#     )

# def run_tests():
#     print("\n=================== 🧠 SHAREBOT TOOL TESTS START ===================\n")

#     # Test get_price with various companies to test fallback mechanisms
#     print("🔹 Testing: get_price (Fallback Testing)")
#     print("=" * 70)
    
#     price_test_companies = [
#         # Companies with aliases (should work directly)
#         "INFY",
#         "INFOSYS", 
#         "TCS",
#         "RELIANCE",
#         "HDFC BANK",
        
#         # Companies with aliases but different formats
#         "HCL",
#         "HCL TECH",
#         "BHARTI AIRTEL",
#         "AIRTEL",
#         "ADANIENT",
#         "ADANI ENTERPRISES",
        
#         # Companies NOT in aliases (will test fallback to historical data)
#         "ZEEL",           # Zee Entertainment
#         "JSWSTEEL",       # JSW Steel
#         "VEDL",           # Vedanta
#         "TECHM",          # Tech Mahindra
#         "LT",             # Larsen & Toubro
#         "COALINDIA",      # Coal India
#         "GRASIM",         # Grasim Industries
#         "DIVISLAB",       # Divis Laboratories
#         "BRITANNIA",      # Britannia Industries
#         "HEROMOTOCO",     # Hero MotoCorp
#         "BAJAJFINSV",     # Bajaj Finserv
#         "CIPLA",          # Cipla
#         "DRREDDY",        # Dr. Reddy's
#         "HINDALCO",       # Hindalco Industries
#         "JINDALSAW",      # Jindal SAW
#         "WIPRO",          # Already in aliases but testing
#         "SBIN",           # State Bank - already in aliases
#         "ICICIBANK",      # Already in aliases
#         "INDIGO",         # InterGlobe Aviation (IndiGo)
#         "PAYTM",          # One 97 Communications
#         "ZOMATO",         # Zomato
#         "NYKAA",          # FSN E-Commerce (Nykaa)
        
#         # Test with .NS suffix directly
#         "RELIANCE.NS",
#         "INFY.NS",
#     ]
    
#     for company in price_test_companies:
#         print(f"\n📊 Testing: {company}")
#         print("-" * 70)
#         try:
#             result = get_price(company)
#             print(result)
#         except Exception as e:
#             print(f"❌ Failed: {e}")
    
#     print("\n" + "=" * 70)
#     print("\n🔹 Testing: Other Tools")
#     print("=" * 70)

#     tests = [
#         ("get_history", lambda: get_history("TCS,3mo,1d")),
#         ("get_company_info", lambda: get_company_info("Infosys")),
#         ("get_financials", lambda: get_financials("TCS")),
#         ("get_dividends", lambda: get_dividends("HDFC Bank")),
#         ("get_splits", lambda: get_splits("Wipro")),
#         ("get_ipo_calendar", lambda: get_ipo_calendar()),
#         ("get_mutual_fund_info", lambda: get_mutual_fund_info("119551")),  # SBI Bluechip example
#         ("get_stock_news", lambda: get_stock_news("Infosys,3")),
#         ("get_market_overview", lambda: get_market_overview()),
#         ("get_stock_analysis", lambda: get_stock_analysis("Reliance,6mo,1d")),
#         ("track_portfolio", lambda: track_portfolio("TCS:5, Reliance:3, Infosys:4")),
#     ]

#     for name, func in tests:
#         print(f"\n🔹 Testing: {name}")
#         print("------------------------------------------------------------")
#         try:
#             result = func()
#             print(result)
#         except Exception as e:
#             print(f"❌ {name} failed: {e}")
#         print("\n============================================================\n")

#     print("=================== ✅ ALL TESTS COMPLETED ===================\n")


# if __name__ == "__main__":
#     run_tests()






