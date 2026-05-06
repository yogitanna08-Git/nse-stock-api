from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import time
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Nifty 50 symbols
NIFTY_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "HINDUNILVR.NS", "AXISBANK.NS",
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS",
    "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
    "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS",
    "POWERGRID.NS", "SBILIFE.NS", "SUNPHARMA.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
    "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"
]

def get_sma_200(symbol):
    """Calculate 200-day Simple Moving Average"""
    try:
        ticker = yf.Ticker(symbol)
        # Get last 250 days of data (more than enough for 200-day SMA)
        hist = ticker.history(period="1y")
        
        if len(hist) >= 200:
            # Calculate 200-day SMA
            sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
            return round(sma_200, 2)
        elif len(hist) > 0:
            # Not enough data, use available data with a fallback
            return round(hist['Close'].mean(), 2)
        else:
            return None
    except Exception as e:
        print(f"Error calculating SMA for {symbol}: {e}")
        return None

@app.route('/')
def home():
    return jsonify({
        "status": "NSE Stock API Running",
        "endpoints": ["/stocks", "/stocks/detailed"],
        "message": "Use /stocks for LTP only, /stocks/detailed for LTP + SMA-200"
    })

@app.route('/stocks')
def get_all_stocks():
    """Fast endpoint - LTP only"""
    results = []
    for symbol in NIFTY_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            ltp = info.get('regularMarketPrice', info.get('currentPrice', 0))
            
            if ltp and ltp > 0:
                results.append({
                    "symbol": symbol.replace('.NS', ''),
                    "ltp": round(ltp, 2)
                })
        except Exception as e:
            pass
        time.sleep(0.05)
    
    return jsonify(results)

@app.route('/stocks/detailed')
def get_all_stocks_detailed():
    """Detailed endpoint - includes SMA-200 for accurate envelope calculation"""
    results = []
    total = len(NIFTY_SYMBOLS)
    
    for i, symbol in enumerate(NIFTY_SYMBOLS):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get LTP
            ltp = info.get('regularMarketPrice', info.get('currentPrice', 0))
            
            # Get SMA-200 from historical data
            sma_200 = get_sma_200(symbol)
            
            if ltp and ltp > 0 and sma_200 and sma_200 > 0:
                results.append({
                    "symbol": symbol.replace('.NS', ''),
                    "ltp": round(ltp, 2),
                    "sma200": sma_200
                })
            elif ltp and ltp > 0:
                # Fallback: estimate SMA if calculation failed
                results.append({
                    "symbol": symbol.replace('.NS', ''),
                    "ltp": round(ltp, 2),
                    "sma200": round(ltp * 0.94, 2)  # Rough estimate
                })
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
        
        time.sleep(0.1)  # Rate limiting
    
    return jsonify({
        "data": results,
        "count": len(results),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
