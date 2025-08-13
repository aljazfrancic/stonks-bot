# Environment Variables for Stonks Bot

This document lists all the environment variables needed to run the Stonks Bot on Railway.

## Required Environment Variables

### 1. DISCORD_TOKEN
- **Description**: Your Discord bot token from the Discord Developer Portal
- **How to get**: 
  1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
  2. Create a new application or select existing one
  3. Go to "Bot" section
  4. Copy the token
- **Example**: `DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIz`

### 2. POLYGON
- **Description**: Your Polygon.io API key for stock and cryptocurrency data
- **How to get**:
  1. Go to [Polygon.io](https://polygon.io/)
  2. Sign up for an account
  3. Get your API key from the dashboard
- **Example**: `POLYGON=your_polygon_api_key_here`

## Optional Environment Variables

### 3. LOG_LEVEL
- **Description**: Logging level for the bot
- **Values**: DEBUG, INFO, WARNING, ERROR
- **Default**: INFO
- **Example**: `LOG_LEVEL=INFO`

### 4. ENVIRONMENT
- **Description**: Environment the bot is running in
- **Values**: development, production
- **Default**: development
- **Example**: `ENVIRONMENT=production`

## Setting Environment Variables in Railway

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
railway variables set LOG_LEVEL=INFO
railway variables set ENVIRONMENT=production
```

### Option 3: Railway.toml (if using)
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python bot.py"

[deploy.env]
DISCORD_TOKEN = "your_token_here"
POLYGON = "your_api_key_here"
LOG_LEVEL = "INFO"
ENVIRONMENT = "production"
```

## Security Notes

- **Never commit your .env file** to version control
- **Use Railway's built-in environment variable management** for production
- **Rotate your API keys regularly** for security
- **Use different tokens** for development and production environments

## Testing Environment Variables

After setting the environment variables, you can test them by:

1. **Deploying to Railway** and checking the logs
2. **Running locally** with a .env file (for development only)
3. **Checking the bot's status** in Discord

## Troubleshooting

- **Bot not responding**: Check if DISCORD_TOKEN is correct
- **No stock data**: Verify POLYGON API key is valid
- **Cryptocurrency data works**: CoinGecko doesn't require an API key
- **Logs not showing**: Check LOG_LEVEL setting
