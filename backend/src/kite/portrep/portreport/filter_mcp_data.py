# import asyncio
# import os
# import json
# from datetime import datetime
# from dotenv import load_dotenv

# # Import existing agents
# from src.kite.mcpclient.kite_mcp_client import KiteMCPClient
# from src.kite.portbot.tool.portfolio import PortfolioAgent
# from src.kite.portbot.tool.login import LoginAgent
# from src.kite.portbot.tool.account import AccountAgent   # NEW

# load_dotenv(override=True)

# # ------------------ File Paths ------------------
# RAW_FILE = r"C:\Users\Ganesh.More\Desktop\GaneshMore\KiteInfi\src\kite\portrep\portreport\mcp_raw_output.json"
# FINAL_FILE = r"C:\Users\Ganesh.More\Desktop\GaneshMore\KiteInfi\src\kite\portrep\portreport\mcp_summary.json"


# # ------------------ Save Raw Data ------------------
# def save_raw_output(label, data):
#     existing = []
#     if os.path.exists(RAW_FILE):
#         with open(RAW_FILE, "r") as f:
#             existing = json.load(f)

#     existing.append({label: data})
#     with open(RAW_FILE, "w") as f:
#         json.dump(existing, f, indent=4)
#     print(f"📁 Raw response saved → {RAW_FILE}")


# # ------------------ Filter Final Data ------------------
# def filter_data():
#     try:
#         with open(RAW_FILE, "r") as f:
#             data = json.load(f)

#         # Data is a list of dictionaries, get the latest entries for each type
#         raw_dict = {}
        
#         # Iterate backwards to get the most recent data for each type
#         for entry in reversed(data):
#             for key in ["holdings", "mutual_funds", "profile"]:
#                 if key in entry and key not in raw_dict:
#                     raw_dict[key] = entry[key]
        
#         # Validate we have all required data
#         if "holdings" not in raw_dict or "mutual_funds" not in raw_dict or "profile" not in raw_dict:
#             raise ValueError("Missing required data in raw output. Ensure holdings, mutual_funds, and profile are all fetched.")

#         print(f"✅ Found holdings: {len(raw_dict['holdings']['data'])} items")
#         print(f"✅ Found mutual_funds: {len(raw_dict['mutual_funds']['data'])} items")
#         print(f"✅ Found profile data")

#         final = {
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "profile": {
#                 "user_id": raw_dict["profile"]["data"].get("user_id"),
#                 "name": raw_dict["profile"]["data"].get("user_name"),
#                 "email": raw_dict["profile"]["data"].get("email"),
#                 "broker": raw_dict["profile"]["data"].get("broker"),
#                 "products": raw_dict["profile"]["data"].get("products", []),
#                 "exchanges": raw_dict["profile"]["data"].get("exchanges", []),
#             },
#             "holdings": [],
#             "mutual_funds": []
#         }
        
#         # Process holdings with error handling
#         try:
#             for i, h in enumerate(raw_dict["holdings"]["data"]):
#                 final["holdings"].append({
#                     "symbol": h.get("symbol", "UNKNOWN"),
#                     "qty": h.get("quantity", h.get("qty", 0)),  # Try both field names
#                     "avg": h.get("average_price", h.get("avg", 0)),  # Try both field names
#                     "ltp": h.get("last_price", h.get("ltp", 0)),  # Try both field names
#                     "pnl": h.get("pnl", 0),
#                 })
#             print(f"✅ Processed {len(final['holdings'])} holdings")
#         except Exception as e:
#             print(f"❌ Error processing holdings: {e}")
#             print(f"Holdings data structure: {raw_dict['holdings']['data'][:1] if raw_dict['holdings']['data'] else 'empty'}")
#             raise
        
#         # Process mutual funds with error handling
#         try:
#             for i, m in enumerate(raw_dict["mutual_funds"]["data"]):
#                 final["mutual_funds"].append({
#                     "scheme": m.get("scheme", "UNKNOWN"),
#                     "units": m.get("units", 0),
#                     "avg_nav": m.get("average_nav", m.get("avg_nav", 0)),  # Try both field names
#                     "nav": m.get("current_nav", m.get("nav", 0)),  # Try both field names
#                     "value": m.get("current_value", m.get("value", 0)),  # Try both field names
#                     "gain_pct": m.get("pnl_percentage", m.get("gain_pct", 0)),  # Try both field names
#                 })
#             print(f"✅ Processed {len(final['mutual_funds'])} mutual funds")
#         except Exception as e:
#             print(f"❌ Error processing mutual funds: {e}")
#             print(f"MF data structure: {raw_dict['mutual_funds']['data'][:1] if raw_dict['mutual_funds']['data'] else 'empty'}")
#             raise

#         with open(FINAL_FILE, "w") as f:
#             json.dump(final, f, indent=4)

#         print(f"🎯 Final filtered summary stored → {FINAL_FILE}")
        
#     except Exception as e:
#         print(f"❌ Error in filter_data: {e}")
#         import traceback
#         traceback.print_exc()
#         raise




# # ------------------ Test Functions ------------------
# async def setup_agents():
#     kite_client = KiteMCPClient()
#     login_agent = LoginAgent(kite_client, shared_state={})
#     login_result = await login_agent.run(tool_name="login")

#     if login_result.get("status") != "success":
#         print("❌ Login failed")
#         return None, None

#     print("✅ Login successful")
#     return PortfolioAgent(kite_client), AccountAgent(kite_client)

# async def test_and_save(label, func):
#     result = await func
#     save_raw_output(label, result)


# # ------------------ Main ------------------
# async def main():
#     portfolio_agent, account_agent = await setup_agents()
#     if portfolio_agent is None:
#         return

#     # Collect RAW data + Save automatically
#     await test_and_save("holdings", portfolio_agent._get_holdings())
#     await test_and_save("mutual_funds", portfolio_agent._get_mf_holdings())
#     await test_and_save("profile", account_agent.run("get_profile"))
#     # Once all saved → Now filter
#     filter_data()


# if __name__ == "__main__":
#     asyncio.run(main())









import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Import existing agents
from src.kite.mcpclient.kite_mcp_client import KiteMCPClient
from src.kite.portbot.tool.portfolio import PortfolioAgent
from src.kite.portbot.tool.login import LoginAgent
from src.kite.portbot.tool.account import AccountAgent   # NEW

load_dotenv(override=True)

# ------------------ File Paths ------------------
RAW_FILE = r"C:\Users\lenovo\OneDrive\Desktop\Hrishi\hacks\backend\KiteInfi\src\kite\portrep\portreport\mcp_raw_output.json"
FINAL_FILE = r"C:\Users\lenovo\OneDrive\Desktop\Hrishi\hacks\backend\KiteInfi\src\kite\portrep\portreport\mcp_summary.json"

# Temporary memory during single script execution
RAW_OUTPUT = {}   # <- This replaces append mechanism


# ------------------ Save RAW Data (Overwrite Once) ------------------
def write_raw_file():
    """Write RAW_OUTPUT dict to file (overwrite mode)"""
    with open(RAW_FILE, "w") as f:
        json.dump(RAW_OUTPUT, f, indent=4)
    print(f"📁 Raw response stored (OVERWRITTEN) → {RAW_FILE}")


# ------------------ Filter Final Data ------------------
def filter_data():
    try:
        with open(RAW_FILE, "r") as f:
            raw_dict = json.load(f)

        # Validate presence of core API data
        required = ["holdings", "mutual_funds", "profile"]
        for key in required:
            if key not in raw_dict:
                raise ValueError(f"Missing required data → {key}")

        final = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "profile": {
                "user_id": raw_dict["profile"]["data"].get("user_id"),
                "name": raw_dict["profile"]["data"].get("user_name"),
                "email": raw_dict["profile"]["data"].get("email"),
                "broker": raw_dict["profile"]["data"].get("broker"),
                "products": raw_dict["profile"]["data"].get("products", []),
                "exchanges": raw_dict["profile"]["data"].get("exchanges", []),
            },
            "holdings": [],
            "mutual_funds": []
        }

        # ---------------- HOLDINGS CLEANING ----------------
        for h in raw_dict["holdings"]["data"]:
            final["holdings"].append({
                "symbol": h.get("symbol") or h.get("tradingsymbol") or "UNKNOWN",
                "qty": float(h.get("quantity", h.get("qty", 0))),
                "avg": round(float(h.get("average_price", h.get("avg", 0))), 2),
                "ltp": round(float(h.get("last_price", h.get("ltp", 0))), 2),
                "pnl": round(float(h.get("pnl", 0)), 2),
            })

        # ---------------- MUTUAL FUNDS CLEANING ----------------
        for m in raw_dict["mutual_funds"]["data"]:
            final["mutual_funds"].append({
                "scheme_name": m.get("scheme_name", "MF_Symbol"),
                "units": round(float(m.get("units", 0)), 3),
                "avg_nav": round(float(m.get("average_nav", m.get("avg_nav", 0))), 4),
                "nav": round(float(m.get("current_nav", m.get("nav", 0))), 4),
                "value": round(float(m.get("current_value", m.get("value", 0))), 2),
                "gain_pct": round(float(m.get("pnl_percentage", m.get("gain_pct", 0))), 2),
            })

        # ---------------- WRITE FINAL FILE ----------------
        with open(FINAL_FILE, "w") as f:
            json.dump(final, f, indent=4)

        print(f"🎯 Final filtered summary stored → {FINAL_FILE}")

    except Exception as e:
        print(f"❌ Error in filter_data: {e}")
        import traceback
        traceback.print_exc()
        raise

# ------------------ Test Functions ------------------
async def setup_agents():
    kite_client = KiteMCPClient()
    login_agent = LoginAgent(kite_client, shared_state={})
    login_result = await login_agent.run(tool_name="login")

    if login_result.get("status") != "success":
        print("❌ Login failed")
        return None, None

    print("✅ Login successful")
    return PortfolioAgent(kite_client), AccountAgent(kite_client)


async def test_and_save(label, func):
    """Store result in RAW_OUTPUT dict (AND NOT APPEND TO FILE)"""
    result = await func
    RAW_OUTPUT[label] = result


# ------------------ Main ------------------
async def main():
    portfolio_agent, account_agent = await setup_agents()
    if portfolio_agent is None:
        return

    # API calls — store in RAW_OUTPUT {}
    await test_and_save("holdings", portfolio_agent._get_holdings())
    await test_and_save("mutual_funds", portfolio_agent._get_mf_holdings())
    await test_and_save("profile", account_agent.run("get_profile"))

    write_raw_file()    # Write once — overwrite file
    filter_data()       # Create final summary


if __name__ == "__main__":
    asyncio.run(main())
