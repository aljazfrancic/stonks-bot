# 🚀 Railway Deployment Guide

Complete guide for deploying the Stonks Bot on Railway.

## Prerequisites

Before you begin, make sure you have:

- ✅ [Railway account](https://railway.app/)
- ✅ [Discord application and bot token](https://discord.com/developers/applications)
- ✅ [Polygon.io API key](https://polygon.io/) (free tier available)
- ✅ Your bot code in a Git repository

## Quick Deploy

1. **Fork this repository** to your GitHub account
2. **Connect to Railway**:
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repository
3. **Set environment variables** in Railway dashboard:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `POLYGON`: Your Polygon.io API key
4. **Deploy** - Railway will automatically build and deploy your bot!

## Manual Deploy

### Option A: Deploy via Railway Dashboard

1. **Connect Repository**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Environment Variables**
   - In your Railway project dashboard, go to the "Variables" tab
   - Add the following environment variables:
     - `DISCORD_TOKEN`: Your Discord bot token
     - `POLYGON`: Your Polygon.io API key

3. **Configure Build Settings**
   - Railway will automatically detect this as a Python project
   - The build command will be: `pip install -r requirements.txt`
   - The start command should be: `python bot.py`

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

4. **Set Environment Variables**
   ```bash
   railway variables --set "DISCORD_TOKEN=your_discord_bot_token_here"
   railway variables --set "POLYGON=your_polygon_api_key_here"
   ```

5. **Deploy**
   ```bash
   railway up
   ```

## Configure Discord Bot

1. **Create Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Give it a name (e.g., "Stonks Bot")

2. **Create Bot**
   - Go to the "Bot" section in your application
   - Click "Add Bot"
   - Copy the bot token and add it to Railway environment variables

3. **Set Bot Permissions**
   - In the Bot section, enable these permissions:
     - Send Messages
     - Attach Files
     - Read Message History
     - Use Slash Commands (if implementing slash commands)

4. **Invite Bot to Server**
   - Go to "OAuth2" → "URL Generator"
   - Select "bot" scope
   - Select the permissions mentioned above
   - Use the generated URL to invite the bot to your server

## Verify Deployment

1. **Check Railway Logs**
   - In Railway dashboard, go to your deployment
   - Check the logs to ensure the bot started successfully
   - You should see: `{bot_name} reporting for duty!`

2. **Test Bot Commands**
   In your Discord server, try these commands:
   ```
   !stonks
   !stonks 7
   !stonks 30 X:BTCUSD GOOG NVDA
   ```

## Monitor and Maintain

### Railway Dashboard Monitoring
- **Logs**: Monitor application logs in real-time
- **Metrics**: Track CPU, memory, and network usage
- **Deployments**: View deployment history and rollback if needed

### Environment Variables Management
- Update environment variables through Railway dashboard
- Use Railway CLI: `railway variables --set "VARIABLE_NAME=value"`

### Scaling (if needed)
- Railway automatically scales based on traffic
- For high-traffic bots, consider upgrading to a paid plan

## Troubleshooting

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Bot Not Responding** | Invalid token or permissions | Check Railway logs, verify `DISCORD_TOKEN`, ensure bot has proper permissions |
| **API Rate Limits** | Polygon.io free tier limits | Consider upgrading to paid plan for higher limits |
| **Build Failures** | Missing dependencies | Check `requirements.txt`, ensure all files are committed |
| **Environment Variables Not Set** | Missing or incorrect variables | Verify variables in Railway dashboard, check case sensitivity |

### Debug Commands

```bash
# Check Railway status
railway status

# View real-time logs
railway logs

# Restart deployment
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

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| **Railway** | Limited usage, suitable for development | $5/month for more resources |
| **Polygon.io** | 5 API calls per minute | $29/month for higher limits |
| **Discord** | Unlimited bot usage | Free for all users |

### Cost Optimization Tips

- **Use Railway free tier** for development and small bots
- **Monitor Polygon.io usage** to stay within free limits
- **Consider paid plans** only for high-traffic production bots

## Additional Resources

### Documentation
- [Railway Documentation](https://docs.railway.app/) - Complete Railway deployment guide
- [Discord.py Documentation](https://discordpy.readthedocs.io/) - Discord bot development
- [Polygon.io API Documentation](https://polygon.io/docs/) - Market data API reference

### Development Tools
- [Discord Developer Portal](https://discord.com/developers/applications) - Create and manage Discord applications
- [Polygon.io Dashboard](https://polygon.io/dashboard) - Monitor API usage and manage keys
- [Railway Dashboard](https://railway.app/dashboard) - Deploy and monitor your applications

### Community & Support
- [Discord.py Community](https://discord.gg/dpy) - Official Discord server
- [Railway Community](https://discord.gg/railway) - Railway support and discussions
- [GitHub Issues](https://github.com/aljazfrancic/stonks-bot/issues) - Report bugs and request features 