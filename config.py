"""
Configuration file for Stonks Bot.

This file contains all the configuration settings for the bot,
making it easy to customize behavior without modifying the main code.
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_CONFIG = {
    "command_prefix": "!stonks",
    "activity_type": "watching",
    "activity_name": "!stonks for charts",
    "log_level": "INFO",
    "chart_dpi": 300,
    "chart_format": "png",
    "chart_bbox_inches": "tight"
}

# Default Tickers Configuration
DEFAULT_TICKERS = {
    "cryptocurrencies": ["BTC", "ETH", "XMR", "AVAX"],
    "stocks": ["X:GOOG", "X:NVDA", "X:AAPL", "X:MSFT"],
    "mixed": ["X:BTCUSD", "X:ETHUSD", "X:XMRUSD", "X:AVAXUSD"]
}

# API Configuration
API_CONFIG = {
    "polygon": {
        "base_url": "https://api.polygon.io/v2/aggs",
        "api_key_env": "POLYGON",
        "rate_limit_delay": 60,  # seconds
        "max_retries": 3
    },
    "coingecko": {
        "base_url": "https://api.coingecko.com/api/v3",
        "rate_limit_delay": 30,  # seconds
        "max_retries": 3
    }
}

# Chart Configuration
CHART_CONFIG = {
    "figure_size": (15, 6),
    "style": "dark_background",
    "grid_color": "#595959",
    "grid_linestyle": "--",
    "grid_linewidth": 2,
    "line_width": 3,
    "price_label_size": 8,
    "price_label_rotation": 90,
    "x_axis_rotation": 45,
    "ticks_count": 11,
    "y_axis_margin": 0.05
}

# Ticker Mappings for CoinGecko
COINGECKO_TICKER_MAPPING = {
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
    "MATIC": "matic-network",
    "UNI": "uniswap",
    "ATOM": "cosmos",
    "FTM": "fantom"
}

# Error Messages
ERROR_MESSAGES = {
    "api_key_missing": "API key not found. Please set the POLYGON environment variable.",
    "invalid_ticker": "Invalid ticker format. Use 'X:SYMBOL' for Polygon or 'symbol' for CoinGecko.",
    "api_error": "API request failed. Please try again later.",
    "no_data": "No data available for the specified ticker and time period.",
    "rate_limit": "Rate limit exceeded. Please wait before making another request.",
    "network_error": "Network error occurred. Please check your internet connection.",
    "invalid_days": "Invalid number of days. Please use a positive integer.",
    "too_many_tickers": "Too many tickers specified. Maximum allowed is 10."
}

# Validation Rules
VALIDATION_RULES = {
    "max_tickers": 10,
    "min_days": 1,
    "max_days": 3650,  # 10 years
    "max_chart_size_mb": 25
}

# File Paths
PATHS = {
    "images_directory": "pics",
    "logs_directory": "logs",
    "config_directory": "config"
}

# Environment Variables
ENV_VARS = {
    "discord_token": "DISCORD_TOKEN",
    "polygon_api_key": "POLYGON",
    "log_level": "LOG_LEVEL",
    "environment": "ENVIRONMENT"
}


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value by key."""
    return BOT_CONFIG.get(key, default)


def get_api_config(provider: str) -> Dict[str, Any]:
    """Get API configuration for a specific provider."""
    return API_CONFIG.get(provider, {})


def get_error_message(error_key: str) -> str:
    """Get error message by key."""
    return ERROR_MESSAGES.get(error_key, "An unknown error occurred.")


def get_ticker_mapping(ticker: str) -> str:
    """Get CoinGecko coin ID for a ticker."""
    return COINGECKO_TICKER_MAPPING.get(ticker.upper(), ticker.lower())


def get_default_tickers(category: str = "mixed") -> List[str]:
    """Get default tickers for a specific category."""
    return DEFAULT_TICKERS.get(category, DEFAULT_TICKERS["mixed"])


def validate_days(days: int) -> bool:
    """Validate the number of days."""
    return VALIDATION_RULES["min_days"] <= days <= VALIDATION_RULES["max_days"]


def validate_ticker_count(count: int) -> bool:
    """Validate the number of tickers."""
    return count <= VALIDATION_RULES["max_tickers"]


def get_environment() -> str:
    """Get the current environment."""
    return os.getenv(ENV_VARS["environment"], "development")


def is_production() -> bool:
    """Check if running in production environment."""
    return get_environment() == "production"
