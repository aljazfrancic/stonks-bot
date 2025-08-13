"""
Test suite for Stonks Bot.

This file contains tests for the main functionality of the stonks bot,
including data providers, chart generation, and error handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add the current directory to the path so we can import stonks
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stonks import (
    StonksChart, PolygonProvider, CoinGeckoProvider, 
    DataProvider, StonksError, get_chart_instance
)
from config import (
    get_config, get_api_config, get_error_message, 
    get_ticker_mapping, validate_days, validate_ticker_count
)


class TestDataProvider(unittest.TestCase):
    """Test the base DataProvider class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = DataProvider("test_key")
    
    def test_init(self):
        """Test DataProvider initialization."""
        self.assertEqual(self.provider.api_key, "test_key")
        self.assertIsNotNone(self.provider.http)
    
    @patch('stonks.urllib3.PoolManager')
    def test_make_request_success(self, mock_pool_manager):
        """Test successful HTTP request."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.data = b'{"test": "data"}'
        
        mock_pool_manager.return_value.request.return_value = mock_response
        
        result = self.provider._make_request("http://test.com")
        self.assertEqual(result, {"test": "data"})
    
    @patch('stonks.urllib3.PoolManager')
    def test_make_request_rate_limit(self, mock_pool_manager):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status = 429
        
        mock_pool_manager.return_value.request.return_value = mock_response
        
        with self.assertRaises(StonksError) as context:
            self.provider._make_request("http://test.com")
        
        self.assertIn("Rate limit exceeded", str(context.exception))


class TestPolygonProvider(unittest.TestCase):
    """Test the PolygonProvider class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = PolygonProvider("test_key")
    
    def test_init(self):
        """Test PolygonProvider initialization."""
        self.assertEqual(self.provider.api_key, "test_key")
    
    def test_get_historical_data_no_api_key(self):
        """Test error when no API key is provided."""
        provider = PolygonProvider(None)
        
        with self.assertRaises(StonksError) as context:
            provider.get_historical_data("X:BTCUSD", 30)
        
        self.assertIn("API key not found", str(context.exception))
    
    def test_get_historical_data_invalid_ticker(self):
        """Test error when ticker doesn't start with 'X:'."""
        with self.assertRaises(StonksError) as context:
            self.provider.get_historical_data("BTC", 30)
        
        self.assertIn("Invalid ticker format", str(context.exception))
    
    @patch.object(DataProvider, '_make_request')
    def test_get_historical_data_success(self, mock_make_request):
        """Test successful data retrieval."""
        mock_data = {
            "results": [
                {"c": 50000.0, "t": 1640995200000},  # 2022-01-01
                {"c": 51000.0, "t": 1641081600000},  # 2022-01-02
            ]
        }
        mock_make_request.return_value = mock_data
        
        prices, dates, timestamps = self.provider.get_historical_data("X:BTCUSD", 2)
        
        self.assertEqual(len(prices), 2)
        self.assertEqual(len(dates), 2)
        self.assertEqual(len(timestamps), 2)
        self.assertEqual(prices[0], 50000.0)
        self.assertEqual(prices[1], 51000.0)


class TestCoinGeckoProvider(unittest.TestCase):
    """Test the CoinGeckoProvider class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = CoinGeckoProvider()
    
    def test_get_coin_id_known_ticker(self):
        """Test getting coin ID for known ticker."""
        coin_id = self.provider._get_coin_id("BTC")
        self.assertEqual(coin_id, "bitcoin")
    
    def test_get_coin_id_unknown_ticker(self):
        """Test getting coin ID for unknown ticker."""
        coin_id = self.provider._get_coin_id("UNKNOWN")
        self.assertEqual(coin_id, "unknown")
    
    def test_get_coin_id_with_x_prefix(self):
        """Test getting coin ID for ticker with X: prefix."""
        coin_id = self.provider._get_coin_id("X:BTC")
        self.assertEqual(coin_id, "bitcoin")
    
    @patch.object(DataProvider, '_make_request')
    def test_get_historical_data_success(self, mock_make_request):
        """Test successful data retrieval."""
        mock_data = {
            "prices": [
                [1640995200000, 50000.0],  # 2022-01-01
                [1641081600000, 51000.0],  # 2022-01-02
            ]
        }
        mock_make_request.return_value = mock_data
        
        prices, dates, timestamps = self.provider.get_historical_data("BTC", 2)
        
        self.assertEqual(len(prices), 2)
        self.assertEqual(len(dates), 2)
        self.assertEqual(len(timestamps), 2)
        self.assertEqual(prices[0], 50000.0)
        self.assertEqual(prices[1], 51000.0)


class TestStonksChart(unittest.TestCase):
    """Test the StonksChart class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.chart = StonksChart()
    
    def test_init(self):
        """Test StonksChart initialization."""
        self.assertIsNotNone(self.chart.polygon_provider)
        self.assertIsNotNone(self.chart.coingecko_provider)
    
    def test_get_data_provider_polygon(self):
        """Test getting Polygon provider for X: tickers."""
        provider = self.chart._get_data_provider("X:BTCUSD")
        self.assertIsInstance(provider, PolygonProvider)
    
    def test_get_data_provider_coingecko(self):
        """Test getting CoinGecko provider for regular tickers."""
        provider = self.chart._get_data_provider("BTC")
        self.assertIsInstance(provider, CoinGeckoProvider)
    
    @patch.object(PolygonProvider, 'get_historical_data')
    @patch.object(CoinGeckoProvider, 'get_historical_data')
    async def test_create_chart_success(self, mock_coingecko, mock_polygon):
        """Test successful chart creation."""
        # Mock data for both providers
        mock_polygon.return_value = (
            np.array([50000.0, 51000.0]),
            np.array(["2022-01-01 00:00 UTC", "2022-01-02 00:00 UTC"]),
            np.array([1640995200000, 1641081600000])
        )
        
        mock_coingecko.return_value = (
            np.array([3000.0, 3100.0]),
            np.array(["2022-01-01 00:00 UTC", "2022-01-02 00:00 UTC"]),
            np.array([1640995200000, 1641081600000])
        )
        
        fig = await self.chart.create_chart(2, ["X:BTCUSD", "ETH"])
        
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)


class TestConfig(unittest.TestCase):
    """Test the configuration module."""
    
    def test_get_config(self):
        """Test getting configuration values."""
        command_prefix = get_config("command_prefix")
        self.assertEqual(command_prefix, "!stonks")
    
    def test_get_api_config(self):
        """Test getting API configuration."""
        polygon_config = get_api_config("polygon")
        self.assertIn("base_url", polygon_config)
        self.assertIn("api_key_env", polygon_config)
    
    def test_get_error_message(self):
        """Test getting error messages."""
        message = get_error_message("api_key_missing")
        self.assertIn("API key not found", message)
    
    def test_get_ticker_mapping(self):
        """Test ticker mapping."""
        coin_id = get_ticker_mapping("BTC")
        self.assertEqual(coin_id, "bitcoin")
    
    def test_validate_days(self):
        """Test days validation."""
        self.assertTrue(validate_days(30))
        self.assertFalse(validate_days(0))
        self.assertFalse(validate_days(4000))
    
    def test_validate_ticker_count(self):
        """Test ticker count validation."""
        self.assertTrue(validate_ticker_count(5))
        self.assertFalse(validate_ticker_count(15))


class TestStonksError(unittest.TestCase):
    """Test the StonksError exception."""
    
    def test_stonks_error(self):
        """Test StonksError creation and message."""
        error = StonksError("Test error message")
        self.assertEqual(str(error), "Test error message")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
