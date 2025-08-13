# 📈 Stonks Bot

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-green.svg)](https://discordpy.readthedocs.io/)
[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-000000.svg?logo=railway)](https://railway.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Advanced Discord bot that creates price comparison charts for cryptocurrencies and stocks using real-time market data from multiple APIs.

## ⚡ Quick Start

**Deploy to Railway (Recommended):**
1. Fork this repository → Get [Discord Bot Token](https://discord.com/developers/applications) & [Polygon.io API Key](https://polygon.io/)
2. `railway up` → Set environment variables in Railway dashboard → Invite bot to server

**Run Locally:**
```bash
git clone https://github.com/aljazfrancic/stonks-bot.git
cd stonks-bot && ./scripts/setup.sh
# Edit .env with your API keys, then: python bot.py
```

## 📊 Demo Charts

> [!NOTE]
> The following graphs are automagically updated via GitHub Actions, so we're looking at the latest data available without paying any subscriptions.

### **Default Portfolio (365 days):**
```text
!stonks
```
![Default Portfolio](pics/!stonks.png)

### **Short-term Analysis (3 days):**
```text
!stonks 3
```
![3-Day Chart](pics/!stonks_3.png)

### **Medium-term Analysis (14 days):**
```text
!stonks 14
```
![14-Day Chart](pics/!stonks_14.png)

### **🚂 BTC and Major Tech Stocks (365 days):**
```text
!stonks 365 BTC X:GOOG X:NVDA X:AAPL X:MSFT
```
![BTC and Tech Stocks](pics/!stonks_365_BTC_X-GOOG_X-NVDA_X-AAPL_X-MSFT.png)

## 🎯 Basic Usage

```bash
!stonks                    # Default portfolio (BTC, ETH, XMR, AVAX)
!stonks 7                 # 7-day chart
!stonks 30 BTC ETH        # 30-day BTC/ETH chart
!stonks 365 X:AAPL X:MSFT # 1-year Apple/Microsoft chart
```

**Ticker Formats:**
- **Crypto**: `BTC`, `ETH`, `SOL` (CoinGecko)
- **Stocks**: `X:AAPL`, `X:MSFT`, `X:GOOG` (Polygon.io)

## 🔧 Setup

**Environment Variables:**
```bash
DISCORD_TOKEN=your_discord_bot_token
POLYGON=your_polygon_api_key
ENVIRONMENT=development  # Optional: development/production
LOG_LEVEL=INFO          # Optional: DEBUG/INFO/WARNING/ERROR
```

## 📚 Documentation

📖 **[Full Documentation](docs/README.md)** - Complete guides and setup instructions

## 🚂 Deploy

**Railway (Recommended):**
```bash
railway login
railway up
```

**Manual Setup:** See [DEPLOYMENT.md](DEPLOYMENT.md)

## 🧪 Testing

```bash
python test_stonks.py
```
