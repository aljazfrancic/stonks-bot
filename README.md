# 📈 Stonks Bot

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-green.svg)](https://discordpy.readthedocs.io/)
[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-000000.svg?logo=railway)](https://railway.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Discord bot that creates price comparison charts for cryptocurrencies and stocks using real-time market data.

## 🚀 Quick Start

**Deploy to Railway (Recommended):**
1. Fork this repository → Get [Discord Bot Token](https://discord.com/developers/applications) & [Polygon.io API Key](https://polygon.io/)
2. `railway up` → Set environment variables in Railway dashboard → Invite bot to server

**Run Locally:**
```bash
git clone https://github.com/aljazfrancic/stonks-bot.git
cd stonks-bot && ./scripts/setup.sh
# Edit .env with your API keys, then: python bot.py
```

## 🔧 Setup

**Environment Variables:**
```bash
DISCORD_TOKEN=your_discord_bot_token
POLYGON=your_polygon_api_key
```

**Scripts:**
- `./scripts/setup.sh` - Quick local setup
- `./scripts/deploy.sh` - Deploy to Railway

## 🤖 Deployment

- [Deployment Guide](DEPLOYMENT.md)

## 🔄 CI/CD Behavior

The GitHub Actions workflow automatically updates the stonks images every hour. **Smart Commit Management:**

- **If the last commit is a chore commit** (autopublish): Automatically amends the existing commit instead of creating new ones
- **If the last commit is not a chore commit**: Creates a new commit as usual

This keeps the git history clean by consolidating all autopublish updates into single commits, preventing the repository from being cluttered with hundreds of individual chore commits.

## 📖 Usage

> [!NOTE]
> The following graphs are automagically updated via GitHub Actions, so we're looking at the latest data available wihtout paying any subscriptions.

To use the bot, send it a direct message on Discord or post in any channel the bot has access to on a Discord server that the bot is in. The message should conform to the following guidelines.

> [!TIP]
> You can mix stock and cryptocurrency [tickers](https://polygon.io/quote/tickers) in the same command.

Default settings (365 days, using tickers `X:BTCUSD`, `X:ETHUSD`, `X:XMRUSD`, `X:AVAXUSD`):
```
!stonks
```
will produce:
![example 1](pics/!stonks.png)

Default settings with user-defined number of days:
```
!stonks <number of days>
```
for example:
```
!stonks 3
```
will produce:
![example 2](pics/!stonks_3.png)

```
!stonks 14
```
will produce:
![example 3](pics/!stonks_14.png)

Custom input:
```
!stonks <number of days> <tickers with spaces>
```
for example:
```
!stonks 365 X:BTCUSD GOOG NVDA AAPL
```
will produce:
![example 4](pics/!stonks_365_X-BTCUSD_GOOG_NVDA_AAPL.png)

## 📝 TODO

- [ ] Combine CoinGecko and Polygon tickers
- [ ] Overall code quality improvements
