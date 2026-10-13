# Railway Deployment Guide

Step-by-step guide for deploying Stonks Bot to Railway.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Deploy](#quick-deploy)
- [Manual Deploy](#manual-deploy)
  - [Option A: Deploy via Railway Dashboard](#option-a-deploy-via-railway-dashboard)
  - [Option B: Deploy via Railway CLI](#option-b-deploy-via-railway-cli)
- [Configure Discord Bot](#configure-discord-bot)
- [Verify Deployment](#verify-deployment)
- [Monitor and Maintain](#monitor-and-maintain)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
- [Cost Considerations](#cost-considerations)
- [Additional Resources](#additional-resources)

## Prerequisites

Before you begin, make sure you have:

- [Railway account](https://railway.com/)
- [Discord application and bot token](https://discord.com/developers/applications) (see [Configure Discord Bot](#configure-discord-bot))
- [Polygon.io (now Massive) API key](https://massive.com/) (free tier available, needed for stocks)
- [CoinGecko API key](https://www.coingecko.com/en/api) (optional - free tier available)
- Your bot code in a Git repository

## Quick Deploy

1. **Fork this repository** to your GitHub account
2. **Connect to Railway**:
   - Go to [Railway Dashboard](https://railway.com/dashboard)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repository
3. **Set environment variables** in Railway dashboard (all variables are described in the [Usage Guide](USAGE.md#configuration)):
   - `DISCORD_TOKEN`: Your Discord bot token
   - `POLYGON`: Your Polygon.io API key
   - `COIN_GECKO`: Your CoinGecko API key (optional)
4. **Deploy** - Railway will automatically build and deploy your bot!

## Manual Deploy

### Option A: Deploy via Railway Dashboard

1. **Connect Repository**
   - Go to [Railway Dashboard](https://railway.com/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Environment Variables**
   - In your Railway project dashboard, go to the "Variables" tab
   - Add the following environment variables (or paste your `.env` file into the "Raw Editor"):
     - `DISCORD_TOKEN`: Your Discord bot token (required)
     - `POLYGON`: Your Polygon.io API key (required for stocks)
     - `COIN_GECKO`: Your CoinGecko API key (optional - for higher crypto limits)

3. **Configure Build Settings**
   - Railway will automatically detect this as a Python project
   - The build installs `requirements.txt`
   - The start command comes from the `Procfile`: `python bot.py`

### Option B: Deploy via Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Railway Project**
   ```bash
   railway init
   ```

4. **Deploy**
   ```bash
   railway up
   ```
   The first deploy also creates the service. The bot exits right away because `DISCORD_TOKEN` isn't set yet; that's expected.

5. **Set Environment Variables**
   ```bash
   railway variables --set "DISCORD_TOKEN=your_discord_bot_token_here" \
                     --set "POLYGON=your_polygon_api_key_here" \
                     --set "COIN_GECKO=your_coingecko_api_key_here"
   ```
   Railway redeploys the bot with the new variables.

## Configure Discord Bot

1. **Create Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Give it a name (e.g., "Stonks Bot")

2. **Get the Bot Token**
   - Go to the "Bot" section in your application
   - Click "Reset Token" and copy the token
   - Add it to Railway environment variables as `DISCORD_TOKEN`

3. **Enable the Message Content Intent**
   - In the same "Bot" section, under "Privileged Gateway Intents", turn on **Message Content Intent**
   - The bot needs it to read `!stonks` messages. Without it, the bot stops at startup with an error asking you to enable it.

4. **Invite Bot to Server**
   - Go to "OAuth2" → "URL Generator"
   - Select the `bot` and `applications.commands` scopes (the second one enables `/stonks`)
   - Select these bot permissions:
     - Send Messages
     - Attach Files
     - Read Message History
   - Use the generated URL to invite the bot to your server

## Verify Deployment

1. **Check Railway Logs**
   - In Railway dashboard, go to your deployment
   - Check the logs to ensure the bot started successfully
   - You should see `Synced 1 slash command(s)` and `<bot name> is online and ready!`

2. **Test Bot Commands**
   In your Discord server, try these commands:
   ```text
   !stonks
   !stonks 7
   !stonks 30 BTC X:GOOG X:NVDA
   /stonks days:14 tickers:SOL DOGE
   ```

## Monitor and Maintain

### Railway Dashboard Monitoring
- **Logs**: Monitor application logs in real-time
- **Metrics**: Track CPU, memory, and network usage
- **Deployments**: View deployment history and rollback if needed

### Environment Variables Management
- Update environment variables through Railway dashboard
- Use Railway CLI: `railway variables --set "VARIABLE_NAME=value"`

### Scaling
- Run exactly **one** instance of the bot. Discord sends every message to every running copy, so extra replicas would answer each command several times.
- A single small instance is enough: charts are generated in the background, at most two at a time.

## Troubleshooting

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Bot stops at startup asking for the Message Content Intent** | Privileged intent not enabled | Enable it in the Developer Portal: Bot → Privileged Gateway Intents |
| **Bot Not Responding** | Invalid token or permissions | Check Railway logs, verify `DISCORD_TOKEN`, ensure bot has proper permissions |
| **"Couldn't upload the chart"** | Missing permission | Give the bot the Attach Files permission in that channel |
| **`/stonks` doesn't show up** | Bot invited without the `applications.commands` scope | Re-invite the bot with both scopes, then restart it |
| **Some tickers are skipped** | Unknown ticker, API limit or missing key | The bot's reply lists each skipped ticker with the reason |
| **API Rate Limits** | Polygon.io free tier limits | Wait a minute, or upgrade your Polygon.io plan |
| **Crypto Rate Limits** | CoinGecko free tier limits | Add a `COIN_GECKO` API key for higher limits |
| **Build Failures** | Missing dependencies | Check `requirements.txt`, ensure all files are committed |
| **Environment Variables Not Set** | Missing or incorrect variables | Verify variables in Railway dashboard, check case sensitivity |

For more detail in the logs, set `LOG_LEVEL=DEBUG`.

### Debug Commands

```bash
# Check Railway status
railway status

# View real-time logs
railway logs

# Restart the bot (without rebuilding)
railway restart

# Deploy your local code
railway up

# Check environment variables
railway variables
```

### Getting Help

If you're still experiencing issues:

1. **Check the logs** in Railway dashboard
2. **Verify your API keys** are correct and active
3. **Ensure your Discord bot** has the required permissions
4. **Open an issue** on GitHub with detailed error information

## Security Best Practices

### API Key Security

1. **Never commit sensitive data**
   - Keep `.env` files in `.gitignore`
   - Use Railway environment variables for secrets
   - Never share API keys in public repositories

2. **Regular token rotation**
   - Periodically regenerate Discord bot tokens
   - Update Railway environment variables accordingly
   - Monitor for unusual bot activity

3. **Monitor usage**
   - Track API usage to avoid rate limits
   - Monitor bot activity for unusual patterns
   - Set up alerts for high usage

### Discord Bot Security

- **Minimal permissions**: Only grant necessary bot permissions
- **Server restrictions**: Limit bot access to trusted servers
- **Token protection**: Keep bot tokens secure and private

## Cost Considerations

### Free Tier Limits

Prices and limits change, so check each provider's pricing page before relying on these.

| Service | Free Option | Notes |
|---------|-------------|-------|
| **Railway** | Trial credit | The bot needs one small always-on instance ([pricing](https://railway.com/pricing)) |
| **Polygon.io (now Massive)** | Free tier with a low per-minute call limit | Each stock ticker in a chart is one API call ([pricing](https://massive.com/pricing)) |
| **CoinGecko** | Works without a key; free Demo key for higher limits | Free plans only cover the last 365 days |
| **Discord** | Free | |

### Cost Optimization Tips

- **Use Railway's trial or smallest plan**: the bot needs very little CPU and memory
- **Monitor Polygon.io usage** to stay within free limits
- **Consider paid plans** only for high-traffic production bots

## Additional Resources

### Documentation
- [Railway Documentation](https://docs.railway.com/) - Complete Railway deployment guide
- [Discord.py Documentation](https://discordpy.readthedocs.io/) - Discord bot development
- [Polygon.io (Massive) API Documentation](https://massive.com/docs) - Market data API reference

### Development Tools
- [Discord Developer Portal](https://discord.com/developers/applications) - Create and manage Discord applications
- [Polygon.io (Massive) Dashboard](https://massive.com/dashboard) - Monitor API usage and manage keys
- [Railway Dashboard](https://railway.com/dashboard) - Deploy and monitor your applications

### Community & Support
- [Discord.py Community](https://discord.gg/dpy) - Official Discord server
- [Railway Community](https://discord.gg/railway) - Railway support and discussions
- [GitHub Issues](https://github.com/aljazfrancic/stonks-bot/issues) - Report bugs and request features
