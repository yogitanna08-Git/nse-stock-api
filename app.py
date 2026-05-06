from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
import time

app = Flask(__name__)
CORS(app)

NIFTY_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "HINDUNILVR.NS", "AXISBANK.NS"
]

@app.route('/')
def home():
    return jsonify({"status": "NSE Stock API Running", "endpoints": ["/stocks"]})

@app.route('/stocks')
def get_stocks():
    results = []
    for symbol in NIFTY_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="2d")
            info = ticker.info
            ltp = info.get('regularMarketPrice', info.get('currentPrice', 0))
            results.append({
                "symbol": symbol.replace('.NS', ''),
                "ltp": round(ltp, 2) if ltp else 0
            })
        except Exception as e:
            results.append({"symbol": symbol.replace('.NS', ''), "ltp": 0})
        time.sleep(0.2)
    return jsonify({"data": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)