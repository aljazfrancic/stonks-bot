# 🔧 Setup Guide

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

## 📋 Prerequisites

- Python 3.12+
- Discord Bot Token
- Polygon.io API Key (optional, for stocks)
- Railway account (for deployment)

## 🔑 Environment Variables

```bash
DISCORD_TOKEN=your_discord_bot_token
POLYGON=your_polygon_api_key
ENVIRONMENT=development  # Optional: development/production
LOG_LEVEL=INFO          # Optional: DEBUG/INFO/WARNING/ERROR
```

## 📁 Scripts

- `./scripts/setup.sh` - Quick local setup
- `./scripts/deploy.sh` - Deploy to Railway

## 🔗 Related Documentation

- [Deployment Guide](../DEPLOYMENT.md)
- [Environment Variables Guide](../ENVIRONMENT_VARIABLES.md)
- [Testing Guide](TESTING.md)
- [Development Guide](DEVELOPMENT.md)
