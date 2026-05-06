from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import time

app = Flask(__name__)
CORS(app)  # This allows your browser to connect

# Nifty 50 symbols with .NS suffix for NSE
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
    return jsonify({
        "status": "NSE Stock API Running",
        "endpoints": ["/stocks", "/stock/<symbol>"],
        "instructions": "Use /stocks to get all Nifty 50 prices"
    })

@app.route('/stocks')
def get_all_stocks():
    """Fetch all Nifty 50 stocks - returns LTP"""
    results = []
    for symbol in NIFTY_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get LTP (last traded price)
            ltp = info.get('regularMarketPrice', info.get('currentPrice', 0))
            
            if ltp and ltp > 0:
                results.append({
                    "symbol": symbol.replace('.NS', ''),
                    "ltp": round(ltp, 2)
                })
            else:
                # Try alternative method
                data = ticker.history(period="1d")
                if not data.empty:
                    ltp = data['Close'].iloc[-1]
                    results.append({
                        "symbol": symbol.replace('.NS', ''),
                        "ltp": round(ltp, 2)
                    })
                else:
                    results.append({
                        "symbol": symbol.replace('.NS', ''),
                        "ltp": 0
                    })
        except Exception as e:
            results.append({
                "symbol": symbol.replace('.NS', ''),
                "ltp": 0,
                "error": str(e)
            })
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    return jsonify({
        "data": results,
        "count": len(results),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/stock/<symbol>')
def get_single_stock(symbol):
    """Fetch single stock price"""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        ltp = info.get('regularMarketPrice', info.get('currentPrice', 0))
        
        if not ltp or ltp == 0:
            data = ticker.history(period="1d")
            if not data.empty:
                ltp = data['Close'].iloc[-1]
        
        return jsonify({
            "symbol": symbol,
            "ltp": round(ltp, 2) if ltp else 0,
            "success": ltp > 0
        })
    except Exception as e:
        return jsonify({
            "symbol": symbol,
            "ltp": 0,
            "success": False,
            "error": str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)