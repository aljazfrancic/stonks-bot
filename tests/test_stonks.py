"""Tests for stonks.py. No network access: providers and HTTP responses are faked."""

import asyncio
import json
import logging
import socket
import threading
import time
import weakref

import matplotlib.pyplot as plt
import numpy as np
import pytest
import urllib3

import stonks
from stonks import StonksChart, StonksError

HOUR_MS = 3_600_000
START_MS = 1_760_000_000_000
DEFAULT_TICKERS = ["BTC", "ETH", "XMR", "AVAX"]


def make_series(n=100, start=START_MS, first=1.0, last=2.0):
    """Hourly (timestamps, prices) moving linearly from `first` to `last`."""
    return np.arange(n, dtype=float) * HOUR_MS + start, np.linspace(first, last, n)


class FakeResponse:
    def __init__(self, status=200, payload=None):
        self.status = status
        self.data = json.dumps(payload).encode()


class FakeHTTP:
    """Stands in for urllib3.PoolManager: records requests, replies with canned responses."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []

    def request(self, method, url, fields=None):
        self.requests.append((method, url, fields))
        return self.responses.pop(0)


def provider_with(provider_class, *responses, api_key=None):
    provider = provider_class(api_key)
    provider.http = FakeHTTP(*responses)
    return provider


@pytest.fixture
def chart():
    """Chart with fake data: BTC rises, ETH falls, X: stocks rise, anything else is unknown."""
    chart = StonksChart()
    data = {"bitcoin": make_series(first=1, last=2), "ethereum": make_series(first=2, last=1)}

    def coingecko_history(coin_id, days):
        if coin_id not in data:
            raise StonksError("not found on CoinGecko")
        return data[coin_id]

    chart.coingecko_provider.get_historical_data = coingecko_history
    chart.coingecko_provider._lookup_symbols = lambda symbols: {}
    chart.polygon_provider.get_historical_data = lambda symbol, days: make_series(n=50, first=3, last=4)
    return chart


@pytest.fixture
def closed_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


# --- argument parsing ---------------------------------------------------------------------------

def test_parse_request_defaults():
    assert stonks.parse_request([]) == (365, DEFAULT_TICKERS)
    assert stonks.parse_request(["7"]) == (7, DEFAULT_TICKERS)


def test_parse_request_normalizes_tickers():
    assert stonks.parse_request(["30", "btc", "x:aapl", "BTC"]) == (30, ["BTC", "X:AAPL"])


@pytest.mark.parametrize("days", ["abc", "0", "-5", "3651", "1.5", "@everyone"])
def test_parse_request_rejects_bad_days(days):
    with pytest.raises(StonksError, match="Days must be a whole number"):
        stonks.parse_request([days])


@pytest.mark.parametrize("ticker", ["@everyone", "<@123>", "a/b", "../x", "x?y", "#x", "a" * 41])
def test_parse_request_rejects_bad_tickers(ticker):
    with pytest.raises(StonksError, match="Tickers may only contain"):
        stonks.parse_request(["30", ticker])


def test_parse_request_limits_ticker_count():
    with pytest.raises(StonksError, match="At most 10 tickers"):
        stonks.parse_request(["30"] + [f"T{i}" for i in range(11)])


@pytest.mark.parametrize("args", [["@everyone"], ["30", "@everyone"]])
def test_parse_errors_do_not_echo_input(args):
    with pytest.raises(StonksError) as excinfo:
        stonks.parse_request(args)
    assert "@" not in str(excinfo.value)


# --- chart creation -----------------------------------------------------------------------------

def test_skipped_ticker_does_not_shift_labels(chart):
    fig, failures = chart.create(30, ["BTC", "FOO", "ETH"])
    ax = fig.axes[0]
    lines = {line.get_label(): line.get_ydata() for line in ax.get_lines()}
    assert list(lines) == ["BTC", "ETH"]
    assert lines["BTC"][-1] > lines["BTC"][0]  # rising data is labeled BTC
    assert lines["ETH"][-1] < lines["ETH"][0]  # falling data is labeled ETH
    assert [text.get_text() for text in ax.get_legend().get_texts()] == ["BTC", "ETH"]
    assert failures == {"FOO": "not found on CoinGecko"}


def test_all_tickers_failing_raises_with_reasons(chart):
    with pytest.raises(StonksError, match=r"FOO \(not found on CoinGecko\)"):
        chart.create(30, ["FOO"])


def test_x_axis_covers_every_series(chart):
    stock = make_series(n=5 * 24)  # starts first, ends two days early
    crypto = make_series(n=7 * 24, start=START_MS + 5 * 60_000)
    chart.polygon_provider.get_historical_data = lambda symbol, days: stock
    chart.coingecko_provider.get_historical_data = lambda coin_id, days: crypto
    fig, _ = chart.create(7, ["X:AAPL", "BTC"])
    xmin, xmax = fig.axes[0].get_xlim()
    assert xmin <= stock[0][0]
    assert xmax >= crypto[0][-1]


def test_missing_polygon_key_only_skips_stocks(chart):
    chart.polygon_provider = stonks.PolygonProvider(None)
    _, failures = chart.create(30, ["BTC", "X:AAPL"])
    assert failures == {"X:AAPL": "POLYGON API key not set"}


def test_create_png_frees_the_figure(chart):
    figures = []
    create_chart = chart._create_matplotlib_chart

    def tracking_create_chart(*args):
        fig = create_chart(*args)
        figures.append(weakref.ref(fig))
        return fig

    chart._create_matplotlib_chart = tracking_create_chart
    png, failures = chart.create_png(30, ["BTC", "ETH"])
    assert png.startswith(b"\x89PNG")
    assert failures == {}
    assert plt.get_fignums() == []
    assert figures[0]() is None  # freed right away, not whenever the garbage collector next runs


@pytest.mark.parametrize(
    "price, expected",
    [(65432.1, "65432.10"), (1, "1.00"), (0.5, "0.500"), (0.0999, "0.0999"), (0.00001234, "0.0000123"), (0, "0.00")],
)
def test_format_price(price, expected):
    assert stonks.format_price(price) == expected


@pytest.mark.parametrize(
    "value, expected",
    [(None, logging.INFO), ("debug", logging.DEBUG), ("WARNING", logging.WARNING), ("nonsense", logging.INFO)],
)
def test_log_level_from_env(monkeypatch, value, expected):
    if value is None:
        monkeypatch.delenv("LOG_LEVEL", raising=False)
    else:
        monkeypatch.setenv("LOG_LEVEL", value)
    assert stonks.log_level_from_env() == expected


def test_get_chart_png_does_not_block_the_event_loop(monkeypatch):
    class SlowChart:
        def create_png(self, days, tickers):
            time.sleep(1)  # stands in for slow API calls and rendering
            return b"png", {}

    monkeypatch.setattr(stonks, "_chart_instance", SlowChart())

    async def scenario():
        loop = asyncio.get_running_loop()
        started = loop.time()
        timer = loop.create_future()
        loop.call_later(0.1, lambda: timer.set_result(loop.time() - started))
        result = await stonks.get_chart_png(30, ["BTC"])
        return result, timer.result()

    result, timer_delay = asyncio.run(scenario())
    assert result == (b"png", {})
    assert timer_delay < 0.5


# --- HTTP and providers -------------------------------------------------------------------------

@pytest.mark.parametrize(
    "status, message",
    [(429, "rate limit"), (401, "check the API key"), (404, "not found on CoinGecko"), (502, "HTTP 502")],
)
def test_http_errors_become_clear_messages(status, message):
    provider = provider_with(stonks.CoinGeckoProvider, FakeResponse(status))
    with pytest.raises(StonksError, match=message) as excinfo:
        provider._get_json("https://api.example/x")
    assert "Unexpected" not in str(excinfo.value)


def test_api_keys_are_sent_in_headers_not_urls():
    assert stonks.PolygonProvider("SECRET").http.headers == {"Authorization": "Bearer SECRET"}
    assert stonks.CoinGeckoProvider("SECRET").http.headers == {"x-cg-demo-api-key": "SECRET"}

    polygon = provider_with(stonks.PolygonProvider, FakeResponse(200, {"results": [{"t": 1, "c": 2}]}), api_key="SECRET")
    coingecko = provider_with(stonks.CoinGeckoProvider, FakeResponse(200, {"prices": [[1, 2]]}), api_key="SECRET")
    polygon.get_historical_data("AAPL", 30)
    coingecko.get_historical_data("bitcoin", 30)
    for provider in (polygon, coingecko):
        _, url, fields = provider.http.requests[0]
        assert "SECRET" not in url + json.dumps(fields)


def test_network_errors_do_not_leak_api_keys(monkeypatch, closed_port, caplog):
    monkeypatch.setattr(stonks, "POLYGON_BASE_URL", f"http://127.0.0.1:{closed_port}")
    provider = stonks.PolygonProvider("SECRET")
    with pytest.raises(StonksError, match="could not reach Polygon.io") as excinfo:
        provider.get_historical_data("AAPL", 30)
    assert "SECRET" not in str(excinfo.value)
    assert "SECRET" not in caplog.text


def test_requests_time_out(monkeypatch):
    # A server that accepts connections but never answers
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen()
    monkeypatch.setattr(stonks, "HTTP_TIMEOUT", urllib3.Timeout(connect=1, read=0.5))
    provider = stonks.CoinGeckoProvider()
    result = {}

    def call():
        try:
            provider._get_json(f"http://127.0.0.1:{server.getsockname()[1]}/hang")
        except StonksError as e:
            result["error"] = str(e)

    thread = threading.Thread(target=call, daemon=True)
    thread.start()
    thread.join(timeout=10)
    server.close()
    assert not thread.is_alive()
    assert result == {"error": "could not reach CoinGecko"}


def test_known_coin_symbols_need_no_lookup():
    provider = provider_with(stonks.CoinGeckoProvider)  # any request would fail: no canned responses
    assert provider.resolve_coin_ids(["BTC", "sol", "DOGE", "UNI"]) == {
        "BTC": "bitcoin", "sol": "solana", "DOGE": "dogecoin", "UNI": "uniswap",
    }


def test_unknown_symbols_resolve_to_largest_coin_and_are_cached():
    markets = [
        {"symbol": "pepe", "id": "pepe"},
        {"symbol": "wif", "id": "dogwifcoin"},
        {"symbol": "wif", "id": "smaller-wif"},
    ]
    provider = provider_with(stonks.CoinGeckoProvider, FakeResponse(200, markets))
    assert provider.resolve_coin_ids(["PEPE", "WIF", "AVALANCHE-2"]) == {
        "PEPE": "pepe", "WIF": "dogwifcoin", "AVALANCHE-2": "avalanche-2",
    }
    _, url, fields = provider.http.requests[0]
    assert url.endswith("/coins/markets")
    assert fields["symbols"] == "pepe,wif,avalanche-2"

    assert provider.resolve_coin_ids(["WIF"]) == {"WIF": "dogwifcoin"}
    assert len(provider.http.requests) == 1


def test_failed_symbol_lookup_falls_back_to_coin_ids():
    provider = provider_with(stonks.CoinGeckoProvider, FakeResponse(429))
    assert provider.resolve_coin_ids(["dogwifcoin"]) == {"dogwifcoin": "dogwifcoin"}


def test_coingecko_rejects_more_than_365_days():
    provider = provider_with(stonks.CoinGeckoProvider)
    with pytest.raises(StonksError, match="365 days"):
        provider.get_historical_data("bitcoin", 366)


def test_user_input_is_escaped_in_urls():
    provider = provider_with(stonks.CoinGeckoProvider, FakeResponse(404))
    with pytest.raises(StonksError, match="not found"):
        provider.get_historical_data("../../evil?x=1#", 30)
    _, url, _ = provider.http.requests[0]
    assert url.endswith("/coins/..%2F..%2Fevil%3Fx%3D1%23/market_chart")


def test_malformed_responses_become_stonks_errors():
    polygon = provider_with(stonks.PolygonProvider, FakeResponse(200, {"results": [{"t": 1}]}), api_key="key")
    coingecko = provider_with(stonks.CoinGeckoProvider, FakeResponse(200, {"prices": "nonsense"}))
    with pytest.raises(StonksError, match="unexpected response"):
        polygon.get_historical_data("AAPL", 30)
    with pytest.raises(StonksError, match="unexpected response"):
        coingecko.get_historical_data("bitcoin", 30)


# --- command line -------------------------------------------------------------------------------

@pytest.fixture
def cli(chart, monkeypatch):
    monkeypatch.setattr(stonks, "_chart_instance", chart)
    monkeypatch.setattr(stonks, "load_dotenv", lambda: None)
    return stonks.main


def test_cli_saves_charts_named_after_the_command(cli, tmp_path):
    assert cli(["--save", "--format", "svg", "--out-dir", str(tmp_path), "365", "BTC", "X:GOOG"]) == 0
    assert cli(["--save", "--out-dir", str(tmp_path)]) == 0
    assert sorted(path.name for path in tmp_path.iterdir()) == ["!stonks.png", "!stonks_365_BTC_X-GOOG.svg"]


def test_cli_strict_refuses_incomplete_charts(cli, tmp_path):
    assert cli(["--save", "--strict", "--out-dir", str(tmp_path), "30", "BTC", "FOO"]) == 1
    assert list(tmp_path.iterdir()) == []


def test_cli_rejects_invalid_input(cli, tmp_path):
    assert cli(["--save", "--out-dir", str(tmp_path), "abc"]) == 1
    assert list(tmp_path.iterdir()) == []
