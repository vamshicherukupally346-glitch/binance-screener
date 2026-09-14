import streamlit as st
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# ==========================================
# WEB PAGE SETUP
# ==========================================
st.set_page_config(page_title="Binance Screener", layout="wide")
st.title("🚀 Binance USDT Perpetual Screener")

# ==========================================
# USER CONTROLS ON WEBSITE
# ==========================================
st.sidebar.header("Screener Settings")
timeframe = st.sidebar.selectbox("Present Timeframe to Check", ["live", "1m", "5m", "15m", "1h", "4h"])
min_percent = st.sidebar.slider("Minimum Past Day % Change", 1.0, 20.0, 4.0, 0.5)
min_price = st.sidebar.number_input("Minimum Past Day Close Price", value=0.1, step=0.1)

# NEW: Dropdown to change how strict the current price check is
present_condition = st.sidebar.selectbox(
    "Present Price Condition (Find more coins)",
    ["Above Yesterday's High", "Above Yesterday's Close", "Above Yesterday's Low"]
)

BASE_URL = "https://fapi.binance.com"

def get_all_usdt_perpetuals():
    try:
        response = requests.get(f"{BASE_URL}/fapi/v1/exchangeInfo")
        data = response.json()
        symbols = [
            s['symbol'] for s in data['symbols']
            if s['quoteAsset'] == 'USDT' and s['contractType'] == 'PERPETUAL' and s['status'] == 'TRADING'
        ]
        return symbols
    except:
        return []

def check_symbol(symbol):
    try:
        r_daily = requests.get(f"{BASE_URL}/fapi/v1/klines?symbol={symbol}&interval=1d&limit=2")
        r_daily.raise_for_status()
        daily_data = r_daily.json()
        
        yesterday = daily_data[0]
        yest_open = float(yesterday[1])
        yest_high = float(yesterday[2])
        yest_low = float(yesterday[3])
        yest_close = float(yesterday[4])
        
        if yest_close <= min_price: return None
            
        pct_change = ((yest_close - yest_open) / yest_open) * 100
        if pct_change < min_percent: return None
            
        if timeframe == "live":
            r_price = requests.get(f"{BASE_URL}/fapi/v1/ticker/price?symbol={symbol}")
            r_price.raise_for_status()
            current_price = float(r_price.json()['price'])
        else:
            r_tf = requests.get(f"{BASE_URL}/fapi/v1/klines?symbol={symbol}&interval={timeframe}&limit=1")
            r_tf.raise_for_status()
            tf_data = r_tf.json()
            current_price = float(tf_data[0][4])
            
        # CHECK CONDITION BASED ON USER DROPDOWN
        condition_met = False
        if present_condition == "Above Yesterday's High":
            condition_met = current_price > yest_high
        elif present_condition == "Above Yesterday's Close":
            condition_met = current_price > yest_close
        elif present_condition == "Above Yesterday's Low":
            condition_met = current_price > yest_low
            
        if condition_met:
            return {
                "Symbol": symbol,
                "Yesterday Close": yest_close,
                "Yesterday % Change": round(pct_change, 2),
                "Yesterday High": yest_high,
                "Yesterday Low": yest_low,
                "Current Price": current_price,
                "Condition Met": present_condition
            }
    except:
        return None

# ==========================================
# RUN BUTTON
# ==========================================
if st.button("🔍 Scan Binance Market Now", type="primary"):
    with st.spinner("Scanning all Binance USDT Perpetual coins... Please wait."):
        symbols = get_all_usdt_perpetuals()
        if not symbols:
            st.error("Could not connect to Binance API.")
        else:
            matched_coins = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(check_symbol, symbols))
            
            matched_coins = [res for res in results if res is not None]
            
            if matched_coins:
                df = pd.DataFrame(matched_coins)
                df = df.sort_values(by="Yesterday % Change", ascending=False)
                
                st.success(f"Found {len(matched_coins)} coins matching your criteria!")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("❌ No coins matched your criteria at this exact moment. Try changing the 'Present Price Condition' on the left to 'Above Yesterday's Close' to find more coins.")