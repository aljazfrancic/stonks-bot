# 🌟 Features

## 🔗 Multi-API Support

- **Polygon.io**: Stocks and major cryptocurrencies (requires API key)
- **CoinGecko**: 1000+ cryptocurrencies (free, no API key required)
- **Automatic Provider Selection**: Bot automatically chooses the best API based on ticker format

## 📊 Enhanced Chart Quality

- High-resolution charts (300 DPI)
- Better error handling and user feedback
- Improved chart styling and readability
- Support for up to 10 tickers simultaneously

## 🛡️ Robust Error Handling

- Comprehensive error messages
- Rate limiting protection
- Network error recovery
- Input validation

## ⚙️ Configuration Management

- Centralized configuration file
- Environment-based settings
- Easy customization without code changes

## 🔄 CI/CD Behavior

The GitHub Actions workflow automatically updates the stonks images every hour. **Smart Commit Management:**

- **If the last commit is a chore commit** (autopublish): Automatically amends the existing commit instead of creating new ones
- **If the last commit is not a chore commit**: Creates a new commit as usual

This keeps the git history clean by consolidating all autopublish updates into single commits, preventing the repository from being cluttered with hundreds of individual chore commits.

## 📈 Chart Capabilities

- **Time Periods**: 1 day to 1 year
- **Ticker Support**: Up to 10 simultaneous tickers
- **Mixed Portfolios**: Combine stocks and crypto in one chart
- **High Resolution**: 300 DPI output for professional quality
- **Real-time Data**: Latest market information from multiple sources
