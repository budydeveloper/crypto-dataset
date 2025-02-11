
# 📊 Crypto Market Datasets

Here you can find CSV datasets of historical data for major cryptocurrencies across different timeframes. The datasets include price, volume, and market cap information, ideal for data analysis, trading strategy backtesting, and building predictive models.

## 📃 Available Datasets & Crypto Ranking

The repository includes historical data for the following major cryptocurrencies:

- **Bitcoin (BTC)**  
- **Ethereum (ETH)**  
- **Ripple (XRP)**  
- **Tether (USDT)**  
- **Solana (SOL)**  
- **Binance Coin (BNB)**  
- **USD Coin (USDC)**  
- **Dogecoin (DOGE)**  
- **Cardano (ADA)**  
- **Polkadot (DOT)**  
- **Litecoin (LTC)**  
- **Avalanche (AVAX)**  
- **Chainlink (LINK)**  
- **Polygon (MATIC)**  

More cryptocurrencies will be added over time.

## 🔄 Timeframes

Datasets are provided in multiple timeframes to suit different analysis needs, including:

### Intraday
- 1m
- 2m
- 5m
- 15m
- 30m
- 60m
- 90m
- 1h
- 4h

### 
- 1d
- 1mo
- 1wk

### Column Definition Format
`Date,Close,High,Low,Open,Volume`

## 💡 Usage

You can easily load the CSV files using Python with pandas:

```python
import pandas as pd

# Load Bitcoin daily data
btc_data = pd.read_csv('path_to_file/XXX.csv')
print(btc_data.head())
```

## 🌎 Data Sources

All data is sourced from reputable cryptocurrency exchanges and public APIs to ensure accuracy and reliability.

## 📅 Updates

Datasets will be updated regularly to include the latest market data.

## 📢 Contributing

Feel free to contribute by submitting pull requests with new datasets or improvements.

---

**Disclaimer:** This data is for educational and research purposes only and should not be considered financial advice.
