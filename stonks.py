"""
Stonks Bot - Cryptocurrency and Stock Price Comparison Tool

This module provides functionality to fetch historical price data from multiple APIs
(Polygon.io and CoinGecko) and create normalized price comparison charts.
"""

import asyncio
import datetime
import json
import os
import sys
import urllib3
from typing import List, Tuple, Optional, Union
from urllib3.exceptions import HTTPError, RequestError, TimeoutError
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
plt.style.use("dark_background")
COMMAND_PREFIX = "!stonks"
DEFAULT_TICKERS = ["BTC", "ETH", "XMR", "AVAX"]

# API Configuration
POLYGON_BASE_URL = "https://api.polygon.io/v2/aggs"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Error messages
ERROR_MESSAGES = {
    "api_key_missing": "API key not found. Please set the POLYGON environment variable.",
    "invalid_ticker": "Invalid ticker format. Use 'X:SYMBOL' for Polygon or 'symbol' for CoinGecko.",
    "api_error": "API request failed. Please try again later.",
    "no_data": "No data available for the specified ticker and time period.",
    "rate_limit": "Rate limit exceeded. Please wait before making another request."
}


class StonksError(Exception):
    """Custom exception for Stonks bot errors."""
    pass


class DataProvider:
    """Base class for data providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.http = urllib3.PoolManager()
    
    def _make_request(self, url: str) -> dict:
        """Make HTTP request with error handling."""
        try:
            response = self.http.request("GET", url)
            if response.status == 429:
                raise StonksError(ERROR_MESSAGES["rate_limit"])
            elif response.status != 200:
                raise StonksError(f"API request failed with status {response.status}")
            
            return json.loads(response.data)
        except (HTTPError, RequestError, TimeoutError) as e:
            raise StonksError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise StonksError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            raise StonksError(f"Unexpected error: {str(e)}")


class PolygonProvider(DataProvider):
    """Polygon.io data provider for stocks and some cryptocurrencies."""
    
    def get_historical_data(self, ticker: str, days: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get historical price data from Polygon.io."""
        if not self.api_key:
            raise StonksError(ERROR_MESSAGES["api_key_missing"])
        
        if not ticker.startswith("X:"):
            raise StonksError(ERROR_MESSAGES["invalid_ticker"])
        
        print(f"Fetching data for {ticker} from Polygon.io...")
        
        # Remove X: prefix for Polygon API calls
        clean_ticker = ticker.replace("X:", "")
        
        end_time = int(time.time() * 1000)
        start_time = end_time - days * 24 * 60 * 60 * 1000
        interval = "day" if days > 60 else "minute"
        
        url = f"{POLYGON_BASE_URL}/ticker/{clean_ticker}/range/1/{interval}/{start_time}/{end_time}?limit=50000&apiKey={self.api_key}"
        
        data = self._make_request(url)
        
        if not data.get("results"):
            print(f"Polygon API response for {clean_ticker}: {data}")
            raise StonksError(ERROR_MESSAGES["no_data"])
        
        # Extract data before converting to numpy arrays
        results = data["results"]
        print(f"Successfully fetched {len(results)} data points for {clean_ticker}")
        
        prices = np.array([result["c"] for result in results])
        timestamps = np.array([result["t"] for result in results])
        
        # Convert timestamps to readable dates
        readable_dates = np.array([
            datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
            for ts in timestamps
        ])
        
        return prices, readable_dates, timestamps


class CoinGeckoProvider(DataProvider):
    """CoinGecko data provider for cryptocurrencies."""
    
    def get_historical_data(self, ticker: str, days: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get historical price data from CoinGecko."""
        print(f"Fetching data for {ticker} from CoinGecko...")
        
        # Convert ticker to CoinGecko format
        coin_id = self._get_coin_id(ticker)
        
        url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
        
        data = self._make_request(url)
        
        if not data.get("prices"):
            raise StonksError(ERROR_MESSAGES["no_data"])
        
        prices = np.array([price[1] for price in data["prices"]])
        timestamps = np.array([price[0] for price in data["prices"]])
        
        # Convert timestamps to readable dates
        readable_dates = np.array([
            datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
            for ts in timestamps
        ])
        
        return prices, readable_dates, timestamps
    
    def _get_coin_id(self, ticker: str) -> str:
        """Convert ticker to CoinGecko coin ID."""
        # Common ticker mappings
        ticker_mapping = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "XMR": "monero",
            "AVAX": "avalanche-2",
            "ADA": "cardano",
            "DOT": "polkadot",
            "LINK": "chainlink",
            "LTC": "litecoin",
            "BCH": "bitcoin-cash",
            "XRP": "ripple"
        }
        
        # Remove 'X:' prefix if present
        clean_ticker = ticker.replace("X:", "")
        
        if clean_ticker in ticker_mapping:
            return ticker_mapping[clean_ticker]
        
        # If not in mapping, try to use the ticker as-is
        return clean_ticker.lower()


class StonksChart:
    """Main class for creating stonks charts."""
    
    def __init__(self):
        self.polygon_provider = PolygonProvider(os.getenv("POLYGON"))
        self.coingecko_provider = CoinGeckoProvider()
    
    def _get_data_provider(self, ticker: str) -> DataProvider:
        """Determine which data provider to use based on ticker format."""
        if ticker.startswith("X:"):
            return self.polygon_provider
        else:
            return self.coingecko_provider
    
    async def create_chart(self, days: Union[str, int], tickers: List[str]) -> plt.Figure:
        """Create a normalized price comparison chart."""
        days_int = int(days)
        
        # Fetch data for all tickers
        all_prices = []
        all_timestamps = []
        all_readable_dates = []
        
        for ticker in tickers:
            try:
                provider = self._get_data_provider(ticker)
                prices, readable_dates, timestamps = provider.get_historical_data(ticker, days_int)
                
                all_prices.append(prices)
                all_timestamps.append(timestamps)
                all_readable_dates.append(readable_dates)
                
            except StonksError as e:
                print(f"Error fetching data for {ticker}: {e}")
                continue
        
        if len(all_prices) == 0:
            raise StonksError("No data could be fetched for any ticker")
        
        # Find the oldest timestamp to align all data
        # Find the array with the earliest timestamp
        min_index = 0
        min_timestamp = float('inf')
        for i, timestamps in enumerate(all_timestamps):
            if len(timestamps) > 0 and timestamps[0] < min_timestamp:
                min_timestamp = timestamps[0]
                min_index = i
        
        oldest_timestamps = all_timestamps[min_index]
        oldest_readable_dates = all_readable_dates[min_index]
        
        # Create the chart
        fig = self._create_matplotlib_chart(
            days_int, tickers, all_prices, all_timestamps, 
            oldest_timestamps, oldest_readable_dates
        )
        
        return fig
    
    def _create_matplotlib_chart(
        self, 
        days: int, 
        tickers: List[str], 
        all_prices: List[np.ndarray], 
        all_timestamps: List[np.ndarray],
        oldest_timestamps: np.ndarray,
        oldest_readable_dates: np.ndarray
    ) -> plt.Figure:
        """Create the matplotlib chart with the given data."""
        fig = plt.figure(figsize=(15, 6))
        
        # Define ticks
        ticks_num = 11
        ticks = np.int32(np.linspace(0, oldest_timestamps.shape[0] - 1, ticks_num))
        mini = 1
        
        # Plot each ticker
        for i, (prices, timestamps) in enumerate(zip(all_prices, all_timestamps)):
            # Normalize prices
            normalized = prices / prices.max()
            
            # Plot line
            plt.plot(timestamps, normalized, linewidth=3, label=tickers[i])
            
            # Add price labels for the first ticker
            if i == 0:
                self._add_price_labels(timestamps, normalized, prices, ticks_num)
            
            # Track global minimum
            norm_mini = normalized.min()
            if norm_mini < mini:
                mini = norm_mini
        
        # Set minimum y-limit
        if mini > 0.9:
            mini = 0.9
        
        # Configure chart appearance
        self._configure_chart_appearance(
            days, oldest_timestamps, oldest_readable_dates, 
            ticks, mini, tickers
        )
        
        return fig
    
    def _add_price_labels(self, timestamps: np.ndarray, normalized: np.ndarray, 
                         prices: np.ndarray, ticks_num: int) -> None:
        """Add price labels to the chart."""
        ticks_positions = np.int32(
            np.linspace(0, timestamps.shape[0] - 1, ticks_num)
        )
        
        for x, y, price in zip(
            timestamps[ticks_positions],
            normalized[ticks_positions],
            prices[ticks_positions]
        ):
            plt.text(
                x, y, f"{price:.2f}",
                color="white", size=8, rotation=90,
                path_effects=[pe.withStroke(linewidth=2, foreground="black")]
            )
    
    def _configure_chart_appearance(self, days: int, oldest_timestamps: np.ndarray,
                                  oldest_readable_dates: np.ndarray, ticks: np.ndarray,
                                  mini: float, tickers: List[str]) -> None:
        """Configure the chart's visual appearance."""
        # X-axis configuration
        plt.gca().set_xticks(oldest_timestamps[ticks])
        plt.gca().set_xticklabels(oldest_readable_dates[ticks], rotation=45, ha="right")
        
        # Y-axis configuration
        price_ticks = np.linspace(0, 1, 11)
        plt.gca().set_yticks(price_ticks)
        plt.gca().set_yticklabels((price_ticks * 100).astype(int))
        plt.gca().set_ylim(mini - 0.05, 1.05)
        
        # Chart limits and grid
        plt.gca().set_xlim(oldest_timestamps[0], oldest_timestamps[-1])
        plt.grid(linewidth=2, color="#595959", linestyle="--")
        
        # Legend and labels
        plt.legend(tickers, bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.xlabel("Time")
        plt.ylabel("Normalized Price (%)")
        
        # Title
        title = f"{('Last day' if days == 1 else f'{days} days')} asset price comparison"
        plt.title(title)
        
        plt.tight_layout()


# Global chart instance
_chart_instance = None


def get_chart_instance() -> StonksChart:
    """Get or create the global chart instance."""
    global _chart_instance
    if _chart_instance is None:
        _chart_instance = StonksChart()
    return _chart_instance


async def get_fig(days: Union[str, int], tickers: List[str]) -> plt.Figure:
    """Get a figure for the specified days and tickers."""
    chart = get_chart_instance()
    return await chart.create_chart(days, tickers)


def main(save: bool = False) -> None:
    """Main function for command-line usage."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Determine tickers and days
        if len(sys.argv) == 1:
            task = get_fig("365", DEFAULT_TICKERS)
        elif len(sys.argv) == 2:
            task = get_fig(sys.argv[1], DEFAULT_TICKERS)
        else:
            task = get_fig(sys.argv[1], sys.argv[2:])
        
        # Generate the chart
        fig = loop.run_until_complete(task)
        
        if save:
            # Save the chart
            args = [arg.replace(":", "-") for arg in sys.argv[1:]]
            filename = (
                f"pics/{COMMAND_PREFIX}"
                + ("_" if args else "")
                + "_".join(args)
                + ".png"
            )
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Chart saved as {filename}")
        else:
            # Display the chart
            plt.show(block=True)
            
    except StonksError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        plt.close("all")


if __name__ == "__main__":
    main(save=False)
