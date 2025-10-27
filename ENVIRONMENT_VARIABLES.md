# 🔧 Environment Variables

Reference for all environment variables used by Stonks Bot.

## 📋 Required Environment Variables

### 1. DISCORD_TOKEN
- **Description**: Your Discord bot token from the Discord Developer Portal
- **Required**: Yes
- **How to get**: 
  1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
  2. Create a new application or select existing one
  3. Go to "Bot" section
  4. Copy the token
- **Example**: `DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIz`

### 2. POLYGON
- **Description**: Your Polygon.io API key for stock and cryptocurrency data
- **Required**: Yes (for stock queries)
- **How to get**:
  1. Go to [Polygon.io](https://polygon.io/)
  2. Sign up for an account (free tier available)
  3. Get your API key from the dashboard
- **Example**: `POLYGON=your_polygon_api_key_here`

## 🔧 Optional Environment Variables

### 3. COINGECKO / COIN_GECKO
- **Description**: CoinGecko API key for higher cryptocurrency rate limits
- **Required**: No (CoinGecko works without key, but with lower limits)
- **Note**: The bot accepts both `COINGECKO` and `COIN_GECKO` variable names
- **How to get**:
  1. Go to [CoinGecko API](https://www.coingecko.com/en/api)
  2. Sign up for a free account
  3. Get your API key from the dashboard
- **Benefits**: 
  - Higher rate limits for crypto data
  - Better API performance
  - Access to premium features
- **Example**: `COINGECKO=your_coingecko_api_key_here` or `COIN_GECKO=your_coingecko_api_key_here`

### 4. LOG_LEVEL
- **Description**: Logging level for the bot
- **Values**: DEBUG, INFO, WARNING, ERROR
- **Default**: INFO
- **Example**: `LOG_LEVEL=INFO`

### 5. ENVIRONMENT
- **Description**: Environment the bot is running in
- **Values**: development, production
- **Default**: development
- **Example**: `ENVIRONMENT=production`

## 🚀 Setting Environment Variables in Railway

### Option 1: Railway Dashboard (Recommended)
1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add each environment variable with its value
5. Click "Add" to save

### Option 2: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Set environment variables
railway variables set DISCORD_TOKEN=your_token_here
railway variables set POLYGON=your_api_key_here
railway variables set COINGECKO=your_coingecko_api_key_here
railway variables set LOG_LEVEL=INFO
railway variables set ENVIRONMENT=production
```

### Option 3: Automated Setup (Easiest)

Run the setup script to automate the process:

```bash
python setup_railway.py
```

**Prerequisites:**
1. Create a `.env` file in your project root:
   ```bash
   DISCORD_TOKEN=your_actual_discord_token
   POLYGON=your_actual_polygon_api_key
   COINGECKO=your_coingecko_api_key
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   ```
2. Run the script: `python setup_railway.py`
3. Follow the generated instructions

### Option 4: Railway.toml

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python bot.py"

[deploy.env]
DISCORD_TOKEN = "your_token_here"
POLYGON = "your_api_key_here"
COINGECKO = "your_coingecko_key_here"
LOG_LEVEL = "INFO"
ENVIRONMENT = "production"
```

## 🔒 Security

- Never commit `.env` files to version control
- Use Railway's environment variable management for production
- Rotate API keys regularly
- Use different tokens for development and production

## 🧪 Testing

Test your setup by:
1. Deploying to Railway and checking logs
2. Running locally with a `.env` file
3. Checking bot status in Discord

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not responding | Check if `DISCORD_TOKEN` is correct |
| No stock data | Verify `POLYGON` API key is valid |
| Rate limits | Add `COINGECKO` API key for higher limits |
| Variable name | Use `COINGECKO` or `COIN_GECKO` (both work) |
| Logs not showing | Check `LOG_LEVEL` setting |
| Script errors | Ensure Python installed and `.env` file exists |
