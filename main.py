from flask import Flask, jsonify, request, render_template
import yfinance as yf
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)

def fetch_stock_data():
    # Read tickers from local CSV file
    df = pd.read_csv('companies.csv')
    tickers = df['Ticker'].tolist()

    # Prepare a list to store stock data
    stocks_data = []

    # For each ticker in CSV, fetch the current and previous closing prices
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        # Fetch the last 5 days of data
        history = stock.history(period='5d')

        if history.empty or len(history['Close']) < 2:
            continue

        latest_close = history['Close'].iloc[-1]
        previous_close = history['Close'].iloc[-2]

        price_change = latest_close - previous_close
        percentage_change = (price_change / previous_close) * 100

        stocks_data.append({
            'ticker': ticker,
            'price': round(latest_close, 2),
            'price_change': round(price_change, 2),
            'percentage_change': round(percentage_change, 2)
        })
    
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return stocks_data, last_updated

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_stock_data', methods=['GET'])
def get_stock_data():
    stocks_data, last_updated = fetch_stock_data()
    return jsonify({'stocks': stocks_data, 'last_updated': last_updated})

def scheduled_task():
    fetch_stock_data()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_task, 'interval', seconds=30)
    scheduler.start()
    
    app.run(debug=True)
