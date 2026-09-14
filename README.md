🚀 Binance USDT Perpetual Screener

A Streamlit-based Binance USDT Perpetual Screener that scans Binance Futures markets and identifies coins based on previous-day price performance and the current price condition.

Features
Scans Binance USDT perpetual contracts
Checks previous-day percentage change
Supports multiple timeframes
Checks current price against:
Yesterday's High
Yesterday's Close
Yesterday's Low
Minimum previous-day percentage filter
Minimum previous-day closing price filter
Displays matching coins in a table
Uses parallel processing to scan multiple symbols
Requirements
Python 3
Streamlit
Requests
Pandas
Run Locally

Install the required packages:

pip install streamlit requests pandas


Run the application:

python -m streamlit run screener.py

Disclaimer

This project is for educational and informational purposes only. It is not financial advice. Cryptocurrency trading involves significant risk.
