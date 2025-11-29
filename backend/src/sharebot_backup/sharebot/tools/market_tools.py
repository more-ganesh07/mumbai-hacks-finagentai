import os
import re
import requests
import yfinance as yf
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, Any
from functools import lru_cache
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import feedparser
import re
from datetime import datetime

load_dotenv(override=True)

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------
def _log_tool(name: str, arg: str = ""):
    print(f"🔧 Tool → {name}('{arg}')")

def _to_safe_dict(df: pd.DataFrame) -> list:
    """Convert DataFrame to JSON-safe list of dicts."""
    try:
        df = df.copy()
        df.index = df.index.map(str)
        df.columns = df.columns.map(str)
        for col in df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns:
            df[col] = df[col].astype(str)
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df[col].astype(float)
        return df.reset_index().to_dict(orient="records")
    except Exception:
        return df.reset_index().to_dict(orient="records")

# -------------------------------------------------------------------------
# Symbol Normalization
# -------------------------------------------------------------------------
@lru_cache(maxsize=128)
def _normalize_symbol(symbol: str) -> str:
    aliases = {
        "SENSEX": "^BSESN",
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "INDUS BANK": "INDUSINDBK.NS",
        "INDUSIND BANK": "INDUSINDBK.NS",
        "HDFC BANK": "HDFCBANK.NS",
        "ICICI BANK": "ICICIBANK.NS",
        "AXIS BANK": "AXISBANK.NS",
        "KOTAK BANK": "KOTAKBANK.NS",
        "SBIN": "SBIN.NS",
        "STATE BANK": "SBIN.NS",
        "RELIANCE": "RELIANCE.NS",
        "TATA MOTORS": "TATAMOTORS.NS",
        "TCS": "TCS.NS",
        "INFOSYS": "INFY.NS",
        "INFY": "INFY.NS",
        "WIPRO": "WIPRO.NS",
        "HCL": "HCLTECH.NS",
        "HCL TECH": "HCLTECH.NS",
        "HCL TECHNOLOGIES": "HCLTECH.NS",
        "BHARTI AIRTEL": "BHARTIARTL.NS",
        "BHARTI": "BHARTIARTL.NS",
        "AIRTEL": "BHARTIARTL.NS",
        "ADANI ENTERPRISES": "ADANIENT.NS",
        "ADANIENT": "ADANIENT.NS",
        "ADANI PORTS": "ADANIPORTS.NS",
        "ADANIPORTS": "ADANIPORTS.NS",
        "ITC": "ITC.NS",
        "BAJAJ FINANCE": "BAJFINANCE.NS",
        "BAJFINANCE": "BAJFINANCE.NS",
        "LIC": "LICI.NS",
        "LIC INDIA": "LICI.NS",
        "TITAN": "TITAN.NS",
        "ULTRACEMCO": "ULTRACEMCO.NS",
        "ULTRATECH CEMENT": "ULTRACEMCO.NS",
        "NTPC": "NTPC.NS",
        "ONGC": "ONGC.NS",
        "POWER GRID": "POWERGRID.NS",
        "POWERGRID": "POWERGRID.NS",
        "SUN PHARMA": "SUNPHARMA.NS",
        "SUNPHARMA": "SUNPHARMA.NS",
        "MARUTI": "MARUTI.NS",
        "MARUTI SUZUKI": "MARUTI.NS",
        "NESTLE": "NESTLEIND.NS",
        "NESTLE INDIA": "NESTLEIND.NS",
        "ASIAN PAINTS": "ASIANPAINT.NS",
        "ASIANPAINT": "ASIANPAINT.NS",
        "M&M": "M&M.NS",
        "MAHINDRA": "M&M.NS",
        "TATA CONSULTANCY": "TCS.NS",
        "TATA STEEL": "TATASTEEL.NS",
        "TATASTEEL": "TATASTEEL.NS",
    }
    alias = symbol.strip().upper()
    if alias in aliases:
        return aliases[alias]
    sym = alias.replace(" ", "")
    if not sym.endswith(".NS") and not sym.startswith("^"):
        sym += ".NS"
    return sym

# -------------------------------------------------------------------------
# 1️⃣ Stock Price
# -------------------------------------------------------------------------
def get_price(input_str: str):
    _log_tool("get_price", input_str)
    symbol = _normalize_symbol(input_str)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Try to get current price from info
        price = info.get("currentPrice")
        
        # Fallback 1: Try regularMarketPrice
        if not price:
            price = info.get("regularMarketPrice")
        
        # Fallback 2: Try previousClose if market is closed
        if not price:
            price = info.get("previousClose")
        
        # Fallback 3: Get from historical data (most recent close)
        if not price:
            try:
                hist = ticker.history(period="1d", interval="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
            except:
                pass
        
        # Fallback 4: Try 5-day history
        if not price:
            try:
                hist = ticker.history(period="5d", interval="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
            except:
                pass
        
        if not price:
            # Return detailed error with suggestions
            company_name = info.get("longName") or info.get("shortName") or symbol
            return f"❌ Could not fetch live price for {symbol} ({company_name}). The symbol might be incorrect or the stock might be delisted. Please verify the ticker symbol. Final Answer."
        
        # Get additional info
        day_high = info.get("dayHigh") or info.get("regularMarketDayHigh") or "N/A"
        day_low = info.get("dayLow") or info.get("regularMarketDayLow") or "N/A"
        year_high = info.get("fiftyTwoWeekHigh") or "N/A"
        year_low = info.get("fiftyTwoWeekLow") or "N/A"
        company_name = info.get("longName") or info.get("shortName") or symbol
        
        return (f"💹 {company_name} ({symbol}) current price is ₹{price:.2f}.\n"
                f"Day High: ₹{day_high}, Day Low: ₹{day_low}.\n"
                f"52 Week High: ₹{year_high}, 52 Week Low: ₹{year_low}.\n"
                "Final Answer.")
    except Exception as e:
        return f"❌ Error fetching price for {symbol}: {str(e)}. Please verify the ticker symbol is correct. Final Answer."

# -------------------------------------------------------------------------
# 2️⃣ Stock History
# -------------------------------------------------------------------------
def get_history(input_str: str):
    _log_tool("get_history", input_str)
    parts = input_str.split(",")
    symbol = _normalize_symbol(parts[0].strip())
    period = parts[1].strip() if len(parts) > 1 else "6mo"
    interval = parts[2].strip() if len(parts) > 2 else "1d"
    try:
        hist = yf.Ticker(symbol).history(period=period, interval=interval)
        if hist.empty:
            return f"⚠️ No history data for {symbol}. Final Answer."
        hist_trim = hist.tail(5)
        stats = f"Avg Close ₹{hist['Close'].mean():.2f}, High ₹{hist['Close'].max():.2f}, Low ₹{hist['Close'].min():.2f}"
        return f"📈 {symbol} history ({period}, {interval}) → {stats}\nFinal Answer."
    except Exception as e:
        return f"❌ Error fetching history for {symbol}: {e}. Final Answer."

# -------------------------------------------------------------------------
# 3️⃣ Company Info
# -------------------------------------------------------------------------
def get_company_info(input_str: str):
    _log_tool("get_company_info", input_str)
    symbol = _normalize_symbol(input_str)
    try:
        info = yf.Ticker(symbol).info
        return (f"🏢 {info.get('longName')} ({symbol})\n"
                f"Sector: {info.get('sector')}, Industry: {info.get('industry')}\n"
                f"Website: {info.get('website')}\n"
                f"Summary: {info.get('longBusinessSummary','N/A')[:400]}...\n"
                "Final Answer.")
    except Exception as e:
        return f"❌ Error fetching company info for {symbol}: {e}. Final Answer."

# -------------------------------------------------------------------------
# 4️⃣ Financials
# -------------------------------------------------------------------------
def get_financials(input_str: str):
    _log_tool("get_financials", input_str)
    symbol = _normalize_symbol(input_str)
    try:
        fin = yf.Ticker(symbol).financials
        return f"📊 Financial data for {symbol} fetched successfully. Columns: {list(fin.columns)}. Final Answer."
    except Exception as e:
        return f"❌ Error fetching financials for {symbol}: {e}. Final Answer."


# -------------------------------------------------------------------------
# 5️⃣ Stock News (GNews, Detailed)
# -------------------------------------------------------------------------
def get_stock_news(input_str: str):
    """
    Fetch latest detailed news for a given stock keyword using GNews API.
    Returns title, date, source, and description for top 3 (default) articles.
    """
    _log_tool("get_stock_news", input_str)
    parts = input_str.split(",")
    query = parts[0].strip()
    count = int(parts[1].strip()) if len(parts) > 1 else 3
    API_KEY = os.getenv("GNEWS_API_KEY")

    try:
        url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max={count}&apikey={API_KEY}"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if "articles" not in data or not data["articles"]:
            return f"⚠️ No news found for {query}. Final Answer."

        articles = data["articles"][:count]
        news_lines = []
        for i, a in enumerate(articles, 1):
            title = a.get("title", "No title")
            desc = a.get("description", "No description available.")
            source = a.get("source", {}).get("name", "Unknown Source")
            date = a.get("publishedAt", "N/A")
            url = a.get("url", "")
            news_lines.append(
                f"{i}. 📰 **{title}**\n"
                f"   🗓️ Date: {date}\n"
                f"   🏢 Source: {source}\n"
                f"   📝 {desc}\n"
                f"   🔗 {url}\n"
            )

        return f"🗞️ Latest {len(news_lines)} news articles about **{query}**:\n\n" + "\n".join(news_lines) + "Final Answer."
    except Exception as e:
        return f"❌ Error fetching news for {query}: {e}. Final Answer."


# -------------------------------------------------------------------------
# 6️⃣ Market Overview (Enhanced)
# -------------------------------------------------------------------------
def get_market_overview(_: str = ""):
    _log_tool("get_market_overview")
    try:
        indices = {
            "^NSEI": "NIFTY 50",
            "^BSESN": "SENSEX",
            "^NSEBANK": "BANK NIFTY"
        }
        lines = []
        for sym, name in indices.items():
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="1d")
            last_price = (
                round(hist["Close"].iloc[-1], 2) if not hist.empty else "N/A"
            )
            info = ticker.info
            lines.append(
                f"{name}: ₹{last_price} (High {info.get('dayHigh')}, Low {info.get('dayLow')})"
            )
        return "📊 Market Overview:\n" + "\n".join(lines) + "\nFinal Answer."
    except Exception as e:
        return f"❌ Error fetching market overview: {e}. Final Answer."


# -------------------------------------------------------------------------
# 7️⃣ Stock Analysis (Enhanced)
# -------------------------------------------------------------------------
def get_stock_analysis(input_str: str):
    """
    Perform detailed technical analysis:
    - Last close, open, high, low
    - SMA20, SMA50
    - RSI (real calc)
    - % change and trend
    """
    _log_tool("get_stock_analysis", input_str)
    parts = input_str.split(",")
    symbol = _normalize_symbol(parts[0].strip())
    period = parts[1].strip() if len(parts) > 1 else "6mo"
    interval = parts[2].strip() if len(parts) > 2 else "1d"

    try:
        hist = yf.Ticker(symbol).history(period=period, interval=interval)
        if hist.empty:
            return f"⚠️ No data for {symbol}. Final Answer."

        last = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else last
        close, open_, high, low = last["Close"], last["Open"], last["High"], last["Low"]
        change = ((close - prev["Close"]) / prev["Close"]) * 100

        # Calculate SMA20 and SMA50
        sma20 = hist["Close"].rolling(20).mean().iloc[-1]
        sma50 = hist["Close"].rolling(50).mean().iloc[-1]

        # Calculate RSI
        delta = hist["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1])) if not np.isnan(rs.iloc[-1]) else "N/A"

        trend = "📈 Uptrend" if close > sma20 > sma50 else "📉 Downtrend" if close < sma20 < sma50 else "➖ Sideways"

        return (
            f"📊 Technical Summary for {symbol}:\n"
            f"• Last Close: ₹{close:.2f} ({change:+.2f}%)\n"
            f"• Open: ₹{open_:.2f}, High: ₹{high:.2f}, Low: ₹{low:.2f}\n"
            f"• SMA20: ₹{sma20:.2f}, SMA50: ₹{sma50:.2f}\n"
            f"• RSI(14): {rsi if isinstance(rsi, str) else f'{rsi:.1f}'}\n"
            f"• Trend: {trend}\n"
            "Final Answer."
        )
    except Exception as e:
        return f"❌ Error analyzing {symbol}: {e}. Final Answer."



# -------------------------------------------------------------------------
# 8️⃣ Portfolio Tracker (Enhanced)
# -------------------------------------------------------------------------
def track_portfolio(input_str: str):
    """
    Track multiple holdings.
    Input format: "TCS:5, Reliance:3, Infosys:4"
    Shows per-stock current price, value, and total portfolio summary.
    """
    _log_tool("track_portfolio", input_str)
    try:
        holdings = [i.strip() for i in input_str.split(",") if i.strip()]
        total_value = 0
        details = []

        for item in holdings:
            sym, qty = item.split(":")
            symbol = sym.strip()
            qty = float(qty)
            yf_symbol = _normalize_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            price = info.get("currentPrice")

            if not price:
                hist = ticker.history(period="1d")
                price = hist["Close"].iloc[-1] if not hist.empty else 0

            value = price * qty
            total_value += value
            change = info.get("regularMarketChangePercent", 0)
            details.append(f"{symbol} x{int(qty)} → ₹{price:.2f} ({change:+.2f}%) | Value ₹{value:,.2f}")

        avg_change = np.mean([float(re.findall(r"[-+]?\d*\.\d+|\d+", d.split('(')[-1])[0]) if '(' in d else 0 for d in details])
        summary = (
            "\n".join(details)
            + f"\n\n💼 Total Portfolio Value: ₹{total_value:,.2f}\n"
            + f"📈 Avg Daily Change: {avg_change:+.2f}%\n"
            + "Final Answer."
        )
        return summary
    except Exception as e:
        return f"❌ Error in portfolio tracking: {e}. Final Answer."



# -------------------------------------------------------------------------
# 🆕 IPO Calendar
# -------------------------------------------------------------------------

# def get_ipo_calendar(_: str = "") -> Dict[str, Any]:
#     """Scrape and return upcoming IPO details from Screener.in"""
#     _log_tool("get_ipo_calendar")
#     url = "https://www.screener.in/ipo/"
#     try:
#         resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
#         resp.raise_for_status()
#         soup = BeautifulSoup(resp.text, "html.parser")
#         table = soup.find("table")
#         if not table:
#             return "⚠️ IPO table not found. Final Answer."
#         rows = table.find_all("tr")[1:]
#         ipo_list = []
#         for row in rows:
#             cols = [td.get_text(strip=True) for td in row.find_all("td")]
#             if len(cols) >= 4:
#                 ipo_list.append(f"{cols[0]} — Period: {cols[1]}, Listing: {cols[2]}")
#         if not ipo_list:
#             return "⚠️ No active IPO listings found. Final Answer."
#         joined = "\n".join(ipo_list[:5])
#         return f"📅 Upcoming IPOs:\n{joined}\nFinal Answer."
#     except Exception as e:
#         return f"❌ Failed to fetch IPO calendar: {e}. Final Answer."


def get_ipo_calendar(_: str = "") -> str:
    """
    Fetch current and upcoming IPO details from Indian markets.
    Returns comprehensive IPO information including names, dates, prices, lot sizes, and subscription status.
    
    Usage: Call this function when user asks about IPOs, new listings, or market issues.
    """
    # _log_tool("get_ipo_calendar")  # Uncomment if you have logging
    
    ipos = []
    
    # Fetch RSS feed
    try:
        feed = feedparser.parse("https://ipowatch.in/feed/")
        for entry in feed.entries[:15]:
            name = (entry.title
                   .replace(" IPO Date, Review, Price, Allotment Details", "")
                   .replace(" IPO Allotment Status Online", "")
                   .replace(" IPO Subscription Status", "")
                   .replace(" – IPO Open", ""))
            
            ipo_data = {
                "name": name,
                "published": entry.published if hasattr(entry, 'published') else "N/A",
                "link": entry.link
            }
            
            # Extract details if subscription status page
            if "subscription-status" in entry.link:
                try:
                    resp = requests.get(entry.link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "html.parser")
                    text = soup.get_text()
                    
                    # Extract price range
                    price_match = re.search(r'₹\s*(\d+)\s*to\s*₹\s*(\d+)', text)
                    if price_match:
                        ipo_data["price_range"] = f"Rs {price_match.group(1)}-{price_match.group(2)}"
                    
                    # Extract lot size
                    lot_match = re.search(r'(\d+,?\d*)\s*shares', text)
                    if lot_match:
                        ipo_data["lot_size"] = f"{lot_match.group(1)} shares"
                    
                    # Extract application amount
                    amount_match = re.search(r'₹\s*(\d+,?\d*,?\d+)\s*application amount', text)
                    if amount_match:
                        ipo_data["application_amount"] = f"Rs {amount_match.group(1)}"
                    
                    # Extract dates
                    date_pattern = r'(\d{1,2}\s+\w+\s+\d{4})'
                    dates = re.findall(date_pattern, text)
                    if len(dates) >= 2:
                        ipo_data["open_date"] = dates[0]
                        ipo_data["close_date"] = dates[1]
                    
                    # Extract subscription status
                    subscription_match = re.search(r'subscribed\s+(?:over\s+)?(\d+\.?\d*)\s*x', text, re.IGNORECASE)
                    if subscription_match:
                        ipo_data["subscription"] = f"{subscription_match.group(1)}x subscribed"
                    
                    # Extract category
                    if "SME" in text:
                        ipo_data["category"] = "SME"
                    elif "Mainboard" in text or "Main Board" in text:
                        ipo_data["category"] = "Mainboard"
                    
                    # Extract listing exchange
                    if "NSE SME" in text:
                        ipo_data["listing"] = "NSE SME"
                    elif "BSE SME" in text:
                        ipo_data["listing"] = "BSE SME"
                    elif "NSE" in text:
                        ipo_data["listing"] = "NSE"
                    elif "BSE" in text:
                        ipo_data["listing"] = "BSE"
                except:
                    pass
            
            ipos.append(ipo_data)
    except:
        pass
    
    # Fetch from Screener.in
    try:
        resp = requests.get("https://www.screener.in/ipo/", timeout=10, 
                          headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table")
        
        if table:
            for row in table.find_all("tr")[1:10]:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    name = cols[0].get_text(strip=True)
                    if name and "Total" not in name and len(name) > 3:
                        ipos.append({
                            "name": name,
                            "open_date": cols[1].get_text(strip=True),
                            "close_date": cols[2].get_text(strip=True),
                            "listing_date": cols[3].get_text(strip=True) if len(cols) > 3 else "N/A"
                        })
    except:
        pass
    
    # Remove duplicates
    seen = set()
    unique_ipos = []
    for ipo in ipos:
        clean_name = ipo["name"].lower().replace("ipo", "").strip()[:30]
        if clean_name not in seen and len(clean_name) > 2:
            seen.add(clean_name)
            unique_ipos.append(ipo)
    
    # Return if no data
    if not unique_ipos:
        return "No IPO data available. Check manually at https://ipowatch.in/. Final Answer."
    
    # Format output
    lines = ["IPO Calendar:", "=" * 70]
    
    # Categorize
    ongoing = [ipo for ipo in unique_ipos if "subscription" in ipo.get("name", "").lower() or ipo.get("subscription")]
    upcoming = [ipo for ipo in unique_ipos if "upcoming" in ipo.get("name", "").lower()]
    others = [ipo for ipo in unique_ipos if ipo not in ongoing and ipo not in upcoming]
    
    # Ongoing IPOs
    if ongoing:
        lines.append("\nONGOING IPOs (Currently Open):")
        lines.append("-" * 70)
        for i, ipo in enumerate(ongoing[:8], 1):
            lines.append(f"\n{i}. {ipo['name']}")
            
            if ipo.get("open_date") and ipo.get("close_date"):
                lines.append(f"   Period: {ipo['open_date']} to {ipo['close_date']}")
            
            if ipo.get("price_range"):
                lot_info = f" | Lot: {ipo['lot_size']}" if ipo.get("lot_size") else ""
                lines.append(f"   Price: {ipo['price_range']}{lot_info}")
            
            if ipo.get("application_amount"):
                lines.append(f"   Min Application: {ipo['application_amount']}")
            
            if ipo.get("subscription"):
                lines.append(f"   Status: {ipo['subscription']}")
            
            if ipo.get("category"):
                listing = f" | {ipo['listing']}" if ipo.get("listing") else ""
                lines.append(f"   Type: {ipo['category']}{listing}")
            
            if ipo.get("link"):
                lines.append(f"   Details: {ipo['link']}")
    
    # Upcoming IPOs
    if upcoming:
        lines.append("\n\nUPCOMING IPOs:")
        lines.append("-" * 70)
        for i, ipo in enumerate(upcoming[:8], 1):
            lines.append(f"\n{i}. {ipo['name']}")
            
            if ipo.get("open_date"):
                close = f" to {ipo['close_date']}" if ipo.get("close_date") else ""
                lines.append(f"   Opens: {ipo['open_date']}{close}")
            
            if ipo.get("price_range"):
                lines.append(f"   Price: {ipo['price_range']}")
            
            if ipo.get("link"):
                lines.append(f"   Details: {ipo['link']}")
    
    # Recent Updates
    if others:
        lines.append("\n\nRECENT IPO UPDATES:")
        lines.append("-" * 70)
        for i, ipo in enumerate(others[:8], 1):
            lines.append(f"\n{i}. {ipo['name']}")
            
            if ipo.get("open_date"):
                close = f" to {ipo['close_date']}" if ipo.get("close_date") else ""
                lines.append(f"   Period: {ipo['open_date']}{close}")
            
            if ipo.get("listing_date"):
                lines.append(f"   Listing: {ipo['listing_date']}")
            
            if ipo.get("link"):
                lines.append(f"   Details: {ipo['link']}")
    
    lines.append("\n" + "=" * 70)
    lines.append(f"Total: {len(unique_ipos)} | Ongoing: {len(ongoing)} | Upcoming: {len(upcoming)} | Updates: {len(others)}")
    lines.append("=" * 70)
    lines.append("Final Answer.")
    
    return "\n".join(lines)

# -------------------------------------------------------------------------
# 9️⃣ Dividends
# -------------------------------------------------------------------------
def get_dividends(input_str: str):
    """Fetch recent dividend history for a stock."""
    _log_tool("get_dividends", input_str)
    symbol = _normalize_symbol(input_str)
    try:
        ticker = yf.Ticker(symbol)
        dividends = ticker.dividends
        if dividends.empty:
            return f"⚠️ No dividend history found for {symbol}. Final Answer."
        last_divs = dividends.tail(5)
        div_lines = [f"{idx.date()} → ₹{amt:.2f}" for idx, amt in last_divs.items()]
        return "💰 Recent Dividends:\n" + "\n".join(div_lines) + "\nFinal Answer."
    except Exception as e:
        return f"❌ Error fetching dividends for {symbol}: {e}. Final Answer."


# -------------------------------------------------------------------------
# 🔟 Stock Splits
# -------------------------------------------------------------------------
def get_splits(input_str: str):
    """Fetch recent stock split history."""
    _log_tool("get_splits", input_str)
    symbol = _normalize_symbol(input_str)
    try:
        ticker = yf.Ticker(symbol)
        splits = ticker.splits
        if splits.empty:
            return f"⚠️ No split data found for {symbol}. Final Answer."
        split_lines = [f"{idx.date()} → {val} for 1" for idx, val in splits.items()]
        return "📉 Stock Splits:\n" + "\n".join(split_lines) + "\nFinal Answer."
    except Exception as e:
        return f"❌ Error fetching splits for {symbol}: {e}. Final Answer."


# -------------------------------------------------------------------------
# 1️⃣1️⃣ Mutual Fund Info (Enhanced)
# -------------------------------------------------------------------------
def get_mutual_fund_info(input_str: str):
    """Fetch mutual fund info by fund code from ValueResearchOnline."""
    _log_tool("get_mutual_fund_info", input_str)
    fund_code = input_str.strip()
    urls = [
        f"https://www.valueresearchonline.com/funds/{fund_code}/",
        f"https://www.valueresearchonline.com/funds/{fund_code}/overview/",
    ]
    try:
        for url in urls:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            name_tag = soup.find("h1")
            fund_name = name_tag.get_text(strip=True) if name_tag else f"Fund {fund_code}"
            desc = soup.find("p").get_text(strip=True) if soup.find("p") else "No description available."

            # Extract NAV or fallback
            nav_value = "N/A"
            nav_text = soup.find(string=re.compile(r"NAV", re.IGNORECASE))
            if nav_text:
                match = re.search(r"₹?([\d,]+(\.\d+)?)", nav_text)
                if match:
                    nav_value = match.group(1)

            return (
                f"🏦 Mutual Fund: {fund_name}\n"
                f"Fund Code: {fund_code}\n"
                f"Latest NAV: ₹{nav_value}\n"
                f"Summary: {desc[:300]}...\n"
                "Final Answer."
            )

        return f"⚠️ Could not fetch data for fund {fund_code}. Final Answer."
    except Exception as e:
        return f"❌ Error fetching mutual fund info for {fund_code}: {e}. Final Answer."
