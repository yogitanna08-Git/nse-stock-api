from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import time

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

@app.route('/')
def home():
    return jsonify({"status": "NSE Stock API Running", "endpoints": ["/stocks", "/stocks/detailed"]})

@app.route('/stocks')
def get_all_stocks():
    """Fast endpoint - LTP only"""
    results = []
    for symbol in NIFTY_SYMBOLS[:20]:  # Limit to 20 stocks for speed
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            ltp = info.get('regularMarketPrice', info.get('currentPrice', 0))
            
            if ltp and ltp > 0:
                results.append({
                    "symbol": symbol.replace('.NS', ''),
                    "ltp": round(ltp, 2)
                })
        except:
            pass
        time.sleep(0.1)
    
    return jsonify(results)

@app.route('/stocks/detailed')
def get_all_stocks_detailed():
    """Simplified endpoint with estimated SMA for speed"""
    results = []
    
    # Use a smaller set for testing first
    test_symbols = NIFTY_SYMBOLS[:20]
    
    for symbol in test_symbols:
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current price
            info = ticker.info
            ltp = info.get('regularMarketPrice', info.get('currentPrice', 0))
            
            if ltp and ltp > 0:
                # Get 200-day SMA from Yahoo (faster than calculating)
                # Use the info dict which sometimes has 'twoHundredDayAverage'
                sma200 = info.get('twoHundredDayAverage', None)
                
                if not sma200 or sma200 == 0:
                    # Fallback: quick calculation with limited data
                    hist = ticker.history(period="6mo")
                    if len(hist) >= 50:
                        sma200 = hist['Close'].tail(50).mean()
                    else:
                        sma200 = ltp * 0.95  # Estimate
                
                results.append({
                    "symbol": symbol.replace('.NS', ''),
                    "ltp": round(ltp, 2),
                    "sma200": round(sma200, 2)
                })
        except Exception as e:
            print(f"Error: {symbol} - {e}")
        
        time.sleep(0.2)
    
    return jsonify({
        "data": results,
        "count": len(results),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
