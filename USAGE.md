# Usage Guide

## Run Locally
```bash
git clone https://github.com/aljazfrancic/stonks-bot.git
cd stonks-bot && ./scripts/setup.sh   # installs dependencies into .venv and creates .env
# Edit .env with your API keys (see Configuration below)
source .venv/bin/activate
python bot.py
```

## How to Use

### Basic Commands
```text
!stonks                   # Default portfolio (BTC, ETH, XMR, AVAX), 365 days
!stonks 7                 # 7-day chart
!stonks 30 BTC ETH        # 30-day BTC/ETH chart
!stonks 365 X:AAPL X:MSFT # 1-year Apple/Microsoft chart
```

The same options work as a slash command: `/stonks days:30 tickers:BTC ETH`.

- **Days**: 1 to 3650. CoinGecko's free API only covers the last 365 days, so crypto tickers are skipped for longer periods.
- **Tickers**: up to 10 per chart. Tickers that can't be fetched are skipped, and the reply says which ones and why.
- **Cooldown**: each user can request one chart every 10 seconds.

### Supported Tickers
- **Cryptocurrencies** (via CoinGecko): symbols like `BTC`, `ETH`, `SOL` or `DOGE`, in any case. A symbol shared by several coins means the one with the largest market cap. CoinGecko coin ids such as `avalanche-2` work too.
- **Stocks** (via Polygon.io, now Massive): `X:` followed by the stock symbol, e.g. `X:AAPL`, `X:MSFT`, `X:GOOG`.

### Command Line
```bash
python stonks.py 30 BTC X:AAPL                      # show the chart in a window
python stonks.py --save --format svg 30 BTC X:AAPL  # save it as pics/!stonks_30_BTC_X-AAPL.svg
```

The command line reads the same `.env` file as the bot. Other options:

- `--out-dir DIR` saves to another folder instead of `pics/`
- `--strict` exits with an error instead of skipping tickers without data
- `--help` lists all options

## Configuration

Set these in `.env` when running locally, or as variables in your hosting dashboard:

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | Yes | Bot token from the [Discord Developer Portal](https://discord.com/developers/applications) |
| `POLYGON` | For stocks | API key from [Polygon.io (now Massive)](https://massive.com/) |
| `COIN_GECKO` | No | [CoinGecko](https://www.coingecko.com/en/api) Demo API key for higher rate limits (`COINGECKO` also works) |
| `LOG_LEVEL` | No | `DEBUG`, `INFO` (default), `WARNING` or `ERROR` |

Never commit your `.env` file; it is listed in `.gitignore`.

## Requirements
- Python 3.12 or higher
- Discord Bot Token
- Polygon.io API Key (for stocks)
- CoinGecko API Key (optional)

## Testing

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check .
pytest
```

The tests use fake data and never call the real APIs. GitHub Actions runs them on every push.

## GitHub Actions

- **CI** (`.github/workflows/ci.yml`) runs `ruff` and the tests on every push and pull request.
- **Update pics** (`.github/workflows/update_pics.yml`) regenerates the README charts every hour and whenever chart code changes on `main`. It publishes them to the `charts` branch as a single commit that each run replaces, so `main` never changes. If any ticker fails, nothing is published and the previous charts stay up. The workflow needs the `POLYGON` and `COIN_GECKO` repository secrets (Settings → Secrets and variables → Actions).

## Features

- Multi-API support (Polygon.io + CoinGecko)
- Automatic provider selection based on the ticker format
- Skipped tickers are reported along with the reason
- Per-user cooldown to stay within API rate limits
- Auto-updating demo charts
