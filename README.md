# 📈 Stonks Bot

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.0+-green.svg)](https://discordpy.readthedocs.io/)
[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-000000.svg?logo=railway)](https://railway.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Discord bot that creates price comparison charts for cryptocurrencies and stocks using real-time market data.

## 🚀 Quick Start

### Deploy to Railway (Recommended)
```bash
# Fork this repo, then:
railway up
```

### Run Locally
```bash
git clone https://github.com/yourusername/stonks-bot.git
cd stonks-bot
pip install -r requirements.txt
python bot.py
```

## 📖 Usage

To use the bot, send it a direct message on Discord or post in any channel the bot has access to on a Discord server that the bot is in. The message should conform to the following guidelines.

### Default settings (365 days, using tickers `X:BTCUSD`, `X:ETHUSD`, `X:XMRUSD`, `X:AVAXUSD`):
```
!stonks
```
will produce:
![example 1](pics/!stonks.png)

### Default settings with user-defined number of days:
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

### Custom input:
```
!stonks <number of days> <tickers with spaces>
```
for example:
```
!stonks 365 X:BTCUSD GOOG NVDA AAPL
```
will produce:
![example 4](pics/!stonks_365_X-BTCUSD_GOOG_NVDA_AAPL.png)

> [!TIP]  
> In terms of [tickers](https://polygon.io/quote/tickers), mixing cryptocurrencies and stocks is allowed!

## 🔧 Setup

### Environment Variables
Create `.env` file:
```bash
DISCORD_TOKEN=your_discord_bot_token
POLYGON=your_polygon_api_key
```

### Prerequisites
- [Discord Bot Token](https://discord.com/developers/applications)
- [Polygon.io API Key](https://polygon.io/) (free tier)

## 📁 Project Structure

```
stonks-bot/
├── bot.py               # Main Discord bot
├── stonks.py            # Chart generation logic
├── requirements.txt     # Python dependencies
├── scripts/             # Utility scripts
│   ├── setup.sh         # Quick setup script
│   └── deploy.sh        # Railway deployment
├── docs/                # Documentation
│   └── DEPLOYMENT.md    # Detailed deployment guide
└── pics/                # Example charts
```

## 🛠️ Scripts

### Quick Setup
```bash
./scripts/setup.sh
```

### Deploy to Railway
```bash
./scripts/deploy.sh
```

## 📚 Documentation

- [📖 Full Deployment Guide](docs/DEPLOYMENT.md)
- [🔧 Troubleshooting](docs/DEPLOYMENT.md#troubleshooting)
- [🔒 Security Best Practices](docs/DEPLOYMENT.md#security-best-practices)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 TODO

- [ ] Revert back to CoinGecko
- [ ] Overall code quality improvements

---

**Need help?** [Open an issue](https://github.com/yourusername/stonks-bot/issues) or check the [full documentation](docs/DEPLOYMENT.md).
