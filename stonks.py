"""
Stonks Bot - Cryptocurrency and Stock Price Comparison Tool

This module provides functionality to fetch historical price data from multiple APIs
(Polygon.io and CoinGecko) and create normalized price comparison charts.
"""

import argparse
import asyncio
import datetime
import gc
import io
import json
import logging
import math
import os
import re
import sys
import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from urllib.parse import quote

import matplotlib.patheffects as pe
import matplotlib.style
import numpy as np
import urllib3
from dotenv import load_dotenv
from matplotlib.figure import Figure
from urllib3.exceptions import HTTPError

logger = logging.getLogger(__name__)

# Configuration
matplotlib.style.use("dark_background")
COMMAND_PREFIX = "!stonks"
DEFAULT_TICKERS = ["BTC", "ETH", "XMR", "AVAX"]
DEFAULT_DAYS = 365
MIN_DAYS = 1
MAX_DAYS = 3650
MAX_TICKERS = 10
TICKS_NUM = 11
STOCK_PREFIX = "X:"
# Letters, digits and . : _ - (e.g. BTC, avalanche-2, X:BRK.B)
TICKER_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9.:_-]{0,39}")

# API Configuration
POLYGON_BASE_URL = "https://api.polygon.io/v2/aggs"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
# CoinGecko's free (public and demo) API only serves the last 365 days
COINGECKO_MAX_DAYS = 365
HTTP_TIMEOUT = urllib3.Timeout(connect=5, read=20)
# Retry connection problems and server errors, but not hung reads or rate limits
HTTP_RETRIES = urllib3.Retry(
    total=2,
    read=0,
    backoff_factor=0.5,
    status_forcelist=(500, 502, 503, 504),
    raise_on_status=False,
)
DAY_MS = 24 * 60 * 60 * 1000

# CoinGecko coin ids for common tickers; other symbols are looked up via the API
COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "XMR": "monero",
    "AVAX": "avalanche-2",
    "ADA": "cardano",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "XRP": "ripple",
    "SOL": "solana",
    "DOGE": "dogecoin",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "BNB": "binancecoin",
    "TRX": "tron",
    "SHIB": "shiba-inu",
    "XLM": "stellar",
}


class StonksError(Exception):
    """Custom exception for Stonks bot errors."""


@dataclass
class Series:
    """Price history of one ticker."""

    label: str
    timestamps: np.ndarray  # milliseconds since the epoch (UTC)
    prices: np.ndarray


class DataProvider:
    """Base class for data providers."""

    name = "API"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        # API keys travel in headers, never in URLs, so they can't leak into error messages or logs
        self.http = urllib3.PoolManager(
            timeout=HTTP_TIMEOUT, retries=HTTP_RETRIES, headers=self._auth_headers()
        )

    def _auth_headers(self) -> dict[str, str]:
        """Headers that authenticate requests to this provider."""
        return {}

    def _get_json(self, url: str, fields: dict[str, object] | None = None):
        """GET a JSON document, turning every failure into a StonksError."""
        try:
            response = self.http.request("GET", url, fields=fields)
        except HTTPError as e:
            logger.warning("%s request failed: %s", self.name, e)
            raise StonksError(f"could not reach {self.name}") from e

        if response.status == 429:
            raise StonksError(f"{self.name} rate limit hit, try again in a minute")
        if response.status in (401, 403):
            raise StonksError(f"{self.name} refused the request (check the API key and plan)")
        if response.status == 404:
            raise StonksError(f"not found on {self.name}")
        if response.status != 200:
            raise StonksError(f"{self.name} returned HTTP {response.status}")

        try:
            return json.loads(response.data)
        except ValueError as e:
            raise StonksError(f"invalid response from {self.name}") from e


class PolygonProvider(DataProvider):
    """Polygon.io data provider for stocks."""

    name = "Polygon.io"

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def get_historical_data(self, symbol: str, days: int) -> tuple[np.ndarray, np.ndarray]:
        """Get (timestamps, close prices) for a stock symbol such as AAPL."""
        if not self.api_key:
            raise StonksError("POLYGON API key not set")
        if not symbol:
            raise StonksError(f"missing stock symbol after {STOCK_PREFIX}")

        end_time = int(time.time() * 1000)
        start_time = end_time - days * DAY_MS
        interval = "day" if days > 60 else "minute"
        url = f"{POLYGON_BASE_URL}/ticker/{quote(symbol, safe='')}/range/1/{interval}/{start_time}/{end_time}"

        data = self._get_json(url, {"limit": 50000})
        results = data.get("results") if isinstance(data, dict) else None
        if not results:
            logger.debug("Polygon.io response for %s: %s", symbol, data)
            raise StonksError("no data for this period (unknown symbol or market closed?)")
        if data.get("next_url"):
            logger.warning("Polygon.io returned only the first %d bars for %s", len(results), symbol)

        try:
            timestamps = np.array([result["t"] for result in results], dtype=float)
            prices = np.array([result["c"] for result in results], dtype=float)
        except (KeyError, TypeError, ValueError) as e:
            raise StonksError(f"unexpected response from {self.name}") from e
        return timestamps, prices


class CoinGeckoProvider(DataProvider):
    """CoinGecko data provider for cryptocurrencies."""

    name = "CoinGecko"

    def __init__(self, api_key: str | None = None):
        super().__init__(api_key)
        self._looked_up: dict[str, str] = {}

    def _auth_headers(self) -> dict[str, str]:
        return {"x-cg-demo-api-key": self.api_key} if self.api_key else {}

    def resolve_coin_ids(self, tickers: Sequence[str]) -> dict[str, str]:
        """Map tickers (symbols like DOGE, or CoinGecko ids like avalanche-2) to coin ids."""
        coin_ids = {}
        unknown = []
        for ticker in tickers:
            coin_id = COINGECKO_IDS.get(ticker.upper()) or self._looked_up.get(ticker.upper())
            if coin_id:
                coin_ids[ticker] = coin_id
            else:
                unknown.append(ticker)

        if unknown:
            found = self._lookup_symbols(unknown)
            for ticker in unknown:
                coin_id = found.get(ticker.lower())
                if coin_id:
                    self._looked_up[ticker.upper()] = coin_id
                # Not a known symbol: treat the ticker itself as a coin id
                coin_ids[ticker] = coin_id or ticker.lower()
        return coin_ids

    def _lookup_symbols(self, symbols: Sequence[str]) -> dict[str, str]:
        """Find the coin with the largest market cap for each symbol."""
        try:
            coins = self._get_json(
                f"{COINGECKO_BASE_URL}/coins/markets",
                {
                    "vs_currency": "usd",
                    "symbols": ",".join(symbol.lower() for symbol in symbols),
                    "include_tokens": "top",
                },
            )
        except StonksError as e:
            logger.warning("CoinGecko symbol lookup failed: %s", e)
            return {}

        found: dict[str, str] = {}
        for coin in coins if isinstance(coins, list) else []:
            if isinstance(coin, dict) and coin.get("symbol") and coin.get("id"):
                # Results are sorted by market cap, so keep the first match
                found.setdefault(str(coin["symbol"]).lower(), str(coin["id"]))
        return found

    def get_historical_data(self, coin_id: str, days: int) -> tuple[np.ndarray, np.ndarray]:
        """Get (timestamps, prices) in USD for a CoinGecko coin id."""
        if days > COINGECKO_MAX_DAYS:
            raise StonksError(f"CoinGecko's free API only covers the last {COINGECKO_MAX_DAYS} days")

        url = f"{COINGECKO_BASE_URL}/coins/{quote(coin_id, safe='')}/market_chart"
        data = self._get_json(url, {"vs_currency": "usd", "days": days})

        try:
            points = [point for point in data.get("prices") or [] if point[1] is not None]
            if not points:
                raise StonksError("no data for this period")
            timestamps, prices = np.array(points, dtype=float).T
        except (AttributeError, IndexError, KeyError, TypeError, ValueError) as e:
            raise StonksError(f"unexpected response from {self.name}") from e
        return timestamps, prices


def is_stock(ticker: str) -> bool:
    """Stocks are written as X:SYMBOL and fetched from Polygon.io; everything else is crypto."""
    return ticker.upper().startswith(STOCK_PREFIX)


def parse_days(value: str) -> int:
    """Parse and validate the number of days."""
    try:
        days = int(value)
    except ValueError:
        days = None
    if days is None or not MIN_DAYS <= days <= MAX_DAYS:
        raise StonksError(f"Days must be a whole number between {MIN_DAYS} and {MAX_DAYS}.")
    return days


def parse_tickers(values: Sequence[str]) -> list[str]:
    """Validate tickers, normalize them to upper case and drop duplicates."""
    tickers: list[str] = []
    for value in values:
        if not TICKER_PATTERN.fullmatch(value):
            raise StonksError("Tickers may only contain letters, digits and . : _ - (e.g. BTC or X:AAPL).")
        ticker = value.upper()
        if ticker not in tickers:
            tickers.append(ticker)
    if len(tickers) > MAX_TICKERS:
        raise StonksError(f"At most {MAX_TICKERS} tickers per chart.")
    return tickers


def parse_request(args: Sequence[str]) -> tuple[int, list[str]]:
    """Parse `[days] [ticker ...]` command arguments."""
    if not args:
        return DEFAULT_DAYS, list(DEFAULT_TICKERS)
    return parse_days(args[0]), parse_tickers(args[1:]) or list(DEFAULT_TICKERS)


def describe_failures(failures: dict[str, str]) -> str:
    """Summarize skipped tickers, e.g. `FOO (not found on CoinGecko)`."""
    return ", ".join(f"{ticker} ({reason})" for ticker, reason in failures.items())


def format_price(price: float) -> str:
    """Two decimals, or three significant digits for prices below 1."""
    if price >= 1 or price <= 0:
        return f"{price:.2f}"
    return f"{price:.{2 - math.floor(math.log10(price))}f}"


def format_timestamp(timestamp: float) -> str:
    """Format a millisecond timestamp as a UTC date."""
    return datetime.datetime.fromtimestamp(timestamp / 1000, datetime.UTC).strftime(
        "%Y-%m-%d %H:%M UTC"
    )


def chart_filename(args: Sequence[str], format: str) -> str:
    """File name matching the command, e.g. `!stonks_365_BTC_X-GOOG.svg`."""
    return COMMAND_PREFIX + "".join("_" + arg.replace(":", "-") for arg in args) + f".{format}"


def log_level_from_env() -> int:
    """Logging level from the LOG_LEVEL environment variable (default INFO)."""
    return logging.getLevelNamesMapping().get(os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)


class StonksChart:
    """Main class for creating stonks charts."""

    def __init__(self):
        self.polygon_provider = PolygonProvider(os.getenv("POLYGON"))
        # Accept both COIN_GECKO and COINGECKO environment variables
        coingecko_api_key = os.getenv("COIN_GECKO") or os.getenv("COINGECKO")
        self.coingecko_provider = CoinGeckoProvider(coingecko_api_key)
        # Matplotlib isn't thread-safe; charts may be requested from several worker threads
        self._render_lock = threading.Lock()

    def fetch(self, days: int, tickers: Sequence[str]) -> tuple[list[Series], dict[str, str]]:
        """Fetch price history for each ticker; returns the series and {ticker: reason} for failures."""
        coins = [ticker for ticker in tickers if not is_stock(ticker)]
        coin_ids = self.coingecko_provider.resolve_coin_ids(coins) if coins else {}

        series: list[Series] = []
        failures: dict[str, str] = {}
        for ticker in tickers:
            try:
                if is_stock(ticker):
                    logger.info("Fetching %s from Polygon.io", ticker)
                    timestamps, prices = self.polygon_provider.get_historical_data(
                        ticker[len(STOCK_PREFIX):], days
                    )
                else:
                    logger.info("Fetching %s (%s) from CoinGecko", ticker, coin_ids[ticker])
                    timestamps, prices = self.coingecko_provider.get_historical_data(coin_ids[ticker], days)
                if not prices.max() > 0:
                    raise StonksError("no valid prices")
            except StonksError as e:
                logger.warning("Skipping %s: %s", ticker, e)
                failures[ticker] = str(e)
                continue
            logger.info("Fetched %d data points for %s", len(prices), ticker)
            series.append(Series(ticker, timestamps, prices))

        if not series:
            raise StonksError(f"No data could be fetched for any ticker: {describe_failures(failures)}")
        return series, failures

    def create(
        self, days: int, tickers: Sequence[str], figure_factory: Callable[..., Figure] = Figure
    ) -> tuple[Figure, dict[str, str]]:
        """Create a chart; returns the figure and {ticker: reason} for skipped tickers."""
        series, failures = self.fetch(days, tickers)
        with self._render_lock:
            return self._create_matplotlib_chart(days, series, figure_factory), failures

    def create_png(self, days: int, tickers: Sequence[str]) -> tuple[bytes, dict[str, str]]:
        """Create a chart as PNG bytes; returns the image and {ticker: reason} for skipped tickers."""
        series, failures = self.fetch(days, tickers)
        buf = io.BytesIO()
        with self._render_lock:
            fig = self._create_matplotlib_chart(days, series, Figure)
            fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            # The figure keeps its ~80 MB render alive inside reference cycles that Python
            # only frees on a full collection; free it now so a long-running bot stays small
            del fig
            gc.collect()
        return buf.getvalue(), failures

    def _create_matplotlib_chart(
        self, days: int, series: Sequence[Series], figure_factory: Callable[..., Figure]
    ) -> Figure:
        """Create the matplotlib chart with the given data."""
        fig = figure_factory(figsize=(15, 6))
        ax = fig.subplots()
        mini = 1

        # Plot each ticker
        for i, s in enumerate(series):
            # Normalize prices
            normalized = s.prices / s.prices.max()

            # Plot line
            ax.plot(s.timestamps, normalized, linewidth=3, label=s.label)

            # Add price labels for the first ticker
            if i == 0:
                self._add_price_labels(ax, s.timestamps, normalized, s.prices)

            # Track global minimum
            mini = min(mini, normalized.min())

        # Set minimum y-limit
        mini = min(mini, 0.9)

        self._configure_chart_appearance(ax, days, series, mini)
        fig.tight_layout()
        return fig

    def _add_price_labels(self, ax, timestamps: np.ndarray, normalized: np.ndarray, prices: np.ndarray) -> None:
        """Add price labels to the chart."""
        positions = np.linspace(0, timestamps.shape[0] - 1, TICKS_NUM).astype(int)
        for x, y, price in zip(timestamps[positions], normalized[positions], prices[positions]):
            ax.text(
                x, y, format_price(price),
                color="white", size=8, rotation=90,
                path_effects=[pe.withStroke(linewidth=2, foreground="black")]
            )

    def _configure_chart_appearance(self, ax, days: int, series: Sequence[Series], mini: float) -> None:
        """Configure the chart's visual appearance."""
        # X-axis: tick labels from the series covering the longest time span,
        # limits wide enough to show every series in full
        widest = max(series, key=lambda s: s.timestamps[-1] - s.timestamps[0])
        tick_times = widest.timestamps[np.linspace(0, widest.timestamps.shape[0] - 1, TICKS_NUM).astype(int)]
        ax.set_xticks(tick_times)
        ax.set_xticklabels([format_timestamp(t) for t in tick_times], rotation=45, ha="right")
        ax.set_xlim(min(s.timestamps[0] for s in series), max(s.timestamps[-1] for s in series))

        # Y-axis configuration
        price_ticks = np.linspace(0, 1, 11)
        ax.set_yticks(price_ticks)
        ax.set_yticklabels((price_ticks * 100).astype(int))
        ax.set_ylim(mini - 0.05, 1.05)

        # Grid, legend and labels
        ax.grid(linewidth=2, color="#595959", linestyle="--")
        ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
        ax.set_xlabel("Time")
        ax.set_ylabel("Normalized Price (%)")

        # Title
        ax.set_title(f"{('Last day' if days == 1 else f'{days} days')} asset price comparison")


# Global chart instance
_chart_instance: StonksChart | None = None


def get_chart_instance() -> StonksChart:
    """Get or create the global chart instance."""
    global _chart_instance
    if _chart_instance is None:
        _chart_instance = StonksChart()
    return _chart_instance


async def get_chart_png(days: int, tickers: Sequence[str]) -> tuple[bytes, dict[str, str]]:
    """Create a PNG chart in a worker thread so the event loop keeps running."""
    chart = get_chart_instance()
    return await asyncio.to_thread(chart.create_png, days, tickers)


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line entry point: show a chart in a window, or save it with --save."""
    parser = argparse.ArgumentParser(description="Normalized price comparison charts for crypto and stocks.")
    parser.add_argument("args", nargs="*", metavar="ARG", help="[days] [ticker ...], e.g. 30 BTC ETH X:AAPL")
    parser.add_argument("--save", action="store_true", help="save the chart to --out-dir instead of showing it")
    parser.add_argument("--format", choices=("png", "svg"), default="png", help="image format for --save")
    parser.add_argument("--out-dir", default="pics", help="directory for --save (default: pics)")
    parser.add_argument("--strict", action="store_true", help="fail instead of skipping tickers without data")
    options = parser.parse_args(argv)

    load_dotenv()
    logging.basicConfig(level=log_level_from_env(), format="%(levelname)s %(name)s: %(message)s")

    figure_factory: Callable[..., Figure] = Figure
    if not options.save:
        import matplotlib.pyplot as plt  # only needed for the interactive window
        figure_factory = plt.figure

    try:
        days, tickers = parse_request(options.args)
        fig, failures = get_chart_instance().create(days, tickers, figure_factory)
    except StonksError as e:
        logger.error("%s", e)
        return 1

    if failures and options.strict:
        logger.error("Not saving an incomplete chart, skipped %s", describe_failures(failures))
        return 1

    if options.save:
        os.makedirs(options.out_dir, exist_ok=True)
        filename = os.path.join(options.out_dir, chart_filename(options.args, options.format))
        fig.savefig(filename, format=options.format, dpi=300, bbox_inches="tight")
        logger.info("Chart saved as %s", filename)
    else:
        plt.show()
    return 0


if __name__ == "__main__":
    sys.exit(main())
