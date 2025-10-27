# 📈 Stonks Bot

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-green.svg)](https://discordpy.readthedocs.io/)
[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-000000.svg?logo=railway)](https://railway.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Discord bot that creates real-time price comparison charts for cryptocurrencies and stocks

## ⚡ Quick Start

### Deploy to Railway (Recommended)
1. Fork this repository
2. Get your API keys:
   - [Discord Bot Token](https://discord.com/developers/applications) (required)
   - [Polygon.io API Key](https://polygon.io/) (required for stocks, free tier available)
   - [CoinGecko API Key](https://www.coingecko.com/en/api) (optional - for higher crypto rate limits)
3. Run `railway up` and set environment variables in Railway dashboard
4. Invite bot to your Discord server

### Run Locally
```bash
git clone https://github.com/aljazfrancic/stonks-bot.git
cd stonks-bot && ./scripts/setup.sh
# Edit .env with your API keys:
# DISCORD_TOKEN=your_token
# POLYGON=your_polygon_key
# COINGECKO=your_coingecko_key
python bot.py
```

## 📊 Example Charts

> **Note:** These charts are automagically updated via GitHub Actions every hour.

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

### ** BTC and Major Tech Stocks (365 days):**
```text
!stonks 365 BTC X:GOOG X:NVDA X:AAPL X:MSFT
```
![BTC and Tech Stocks](pics/!stonks_365_BTC_X-GOOG_X-NVDA_X-AAPL_X-MSFT.png)

## 🎯 How to Use

### Basic Commands
```bash
!stonks                   # Default portfolio (BTC, ETH, XMR, AVAX)
!stonks 7                 # 7-day chart
!stonks 30 BTC ETH        # 30-day BTC/ETH chart
!stonks 365 X:AAPL X:MSFT # 1-year Apple/Microsoft chart
```

### Supported Tickers
- **Cryptocurrencies**: `BTC`, `ETH`, `SOL` (via CoinGecko)
- **Stocks**: `X:AAPL`, `X:MSFT`, `X:GOOG` (via Polygon.io)

## 🔧 Environment Setup

### Required Variables

```bash
# Discord Bot Token (required)
DISCORD_TOKEN=your_discord_bot_token
# Get from: https://discord.com/developers/applications

# Polygon.io API Key (required for stocks)
POLYGON=your_polygon_api_key
# Get from: https://polygon.io/ (free tier available)
```

### Optional Variables

```bash
# CoinGecko API Key (optional - for higher crypto rate limits)
COINGECKO=your_coingecko_api_key
# Get from: https://www.coingecko.com/en/api (free tier available)
# Note: Also accepts COIN_GECKO variable name

# Environment setting (optional)
ENVIRONMENT=development
# Options: development, production

# Logging level (optional)
LOG_LEVEL=INFO
# Options: DEBUG, INFO, WARNING, ERROR
```

### Get Your API Keys

1. **Discord Bot Token** (required)
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Navigate to "Bot" section
   - Copy the token

2. **Polygon.io API Key** (required for stocks)
   - Go to [Polygon.io](https://polygon.io/)
   - Sign up for a free account
   - Get your API key from the dashboard

3. **CoinGecko API Key** (optional - for higher crypto rate limits)
   - Go to [CoinGecko API](https://www.coingecko.com/en/api)
   - Sign up for a free account
   - Get your API key for higher rate limits

### Requirements
- Python 3.12 or higher
- Discord Bot Token (required)
- Polygon.io API Key (required for stocks)
- CoinGecko API Key (optional - for higher crypto rate limits)

## 🚂 Deployment

### Deploy with Railway (Recommended)
```bash
railway login
railway up
```

### Deploy Manually
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 🧪 Run Tests

```bash
python test_stonks.py
```

## 🌟 Features

- **Dual API Support**: Polygon.io for stocks + CoinGecko for crypto
- **Smart Provider Selection**: Automatically chooses the best API
- **Error Handling**: Clear error messages and rate limit protection
- **Auto-Updates**: Charts update every hour via GitHub Actions
- **High Quality**: Professional 300 DPI chart output

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No data available" | Check ticker symbol or try a different time period |
| "Rate limited" | Wait a moment and try again |
| "Invalid ticker" | Use `X:SYMBOL` for stocks, `SYMBOL` for crypto |
| Bot not responding | Check Railway logs and verify `DISCORD_TOKEN` |

## 📚 Documentation

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Polygon.io API Docs](https://polygon.io/docs/)
- [CoinGecko API Docs](https://www.coingecko.com/en/api/documentation)
- [Railway Documentation](https://docs.railway.app/)
- [Deployment Guide](DEPLOYMENT.md)
