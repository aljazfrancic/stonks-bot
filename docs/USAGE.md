# 📖 Usage Guide

## 🎯 Basic Commands

To use the bot, send it a direct message on Discord or post in any channel the bot has access to on a Discord server that the bot is in.

> [!TIP]
> You can mix stock and cryptocurrency tickers in the same command! Use `X:SYMBOL` for stocks/Polygon data and `SYMBOL` for CoinGecko cryptocurrencies.

### **Default Settings (365 days)**
```text
!stonks
```
Uses default mixed portfolio: `BTC`, `ETH`, `XMR`, `AVAX`

### **Custom Time Periods**
```text
!stonks 3    # Last 3 days
!stonks 14   # Last 2 weeks
!stonks 30   # Last month
!stonks 365  # Last year
```

### **Custom Ticker Combinations**

**Stocks only:**
```text
!stonks 30 X:GOOG X:NVDA X:AAPL X:MSFT
```

**Cryptocurrencies only:**
```text
!stonks 7 BTC ETH SOL ADA DOT
```

**Mixed portfolio:**
```text
!stonks 90 X:BTCUSD ETH X:GOOG X:NVDA
```

## 🔤 Supported Ticker Formats

### **Polygon.io (Stocks & Major Crypto):**
- `X:BTCUSD` - Bitcoin
- `X:ETHUSD` - Ethereum  
- `X:GOOG` - Google
- `X:AAPL` - Apple
- `X:NVDA` - NVIDIA
- `X:MSFT` - Microsoft
- `X:TSLA` - Tesla
- `X:AMZN` - Amazon

### **CoinGecko (Cryptocurrencies):**
- `BTC` - Bitcoin
- `ETH` - Ethereum
- `SOL` - Solana
- `ADA` - Cardano
- `DOT` - Polkadot
- `MATIC` - Polygon
- `UNI` - Uniswap
- `AAVE` - Aave
- `COMP` - Compound
- `MKR` - Maker
- And 1000+ more!

## 💡 Pro Tips

1. **Mix and Match**: Combine stocks and crypto for diverse portfolios
2. **Time Optimization**: Use shorter periods (3-14 days) for active trading, longer (90-365) for trend analysis
3. **Portfolio Size**: Keep portfolios under 10 tickers for optimal chart readability
4. **API Limits**: Polygon.io has rate limits, CoinGecko is more generous
5. **Ticker Accuracy**: Use exact ticker symbols for best results

## 🚨 Common Issues

- **"No data available"**: Check ticker symbol or try different time period
- **"Rate limited"**: Wait a moment and try again
- **"Invalid ticker"**: Verify ticker format (X:SYMBOL for stocks, SYMBOL for crypto)
