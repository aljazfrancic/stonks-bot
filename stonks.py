import asyncio
import datetime
import json
import os
import sys
import urllib3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import time
from dotenv import load_dotenv

load_dotenv()

plt.style.use("dark_background")

command_prefix = "!stonks"

default_tickers = ["BTC", "ETH", "XMR", "AVAX"]


#################
# API CALL HACK #
#################


def do_req(url):
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return json.loads(response.data)


################
# COINGECKO PART #
################

def get_coin_historic_price_coingecko(coin_id, days):
    """Get historical price data from CoinGecko API"""
    print(f"CoinGecko: {coin_id}")
    int_days = int(days)
    # CoinGecko interval logic - avoid hourly as it requires Enterprise plan
    if int_days <= 1:
        # For 1 day, use daily interval (hourly requires Enterprise)
        interval = "daily"
    elif int_days <= 90:
        interval = "daily"
    else:
        interval = "daily"
    
    # Check if we have a CoinGecko API key for higher rate limits
    coingecko_key = os.getenv("COIN_GECKO")
    if coingecko_key:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={int_days}&interval={interval}&x_cg_demo_api_key={coingecko_key}"
    else:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={int_days}&interval={interval}"
    
    try:
        data = do_req(url)
        
        if "prices" not in data:
            print(f"CoinGecko API error: {data}")
            # Check if it's a rate limit error
            if "error_code" in str(data) and "10005" in str(data):
                raise Exception("CoinGecko rate limit exceeded")
            raise Exception(f"Invalid response from CoinGecko: {data}")
        
        prices = []
        timestamps = []
        readable_dates = []
        
        for price_point in data["prices"]:
            timestamp = price_point[0]
            price = price_point[1]
            prices.append(price)
            timestamps.append(timestamp)
            readable_dates.append(
                f"{datetime.datetime.fromtimestamp(int(timestamp) / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC"
            )
        
        return np.array(prices), np.array(readable_dates), np.array(timestamps)
    except Exception as e:
        print(f"CoinGecko API call failed: {e}")
        raise e


################
# POLYGON PART #
################

def get_coin_historic_price_polygon(ticker, days, key):
    """Get historical price data from Polygon API"""
    print(f"Polygon: {ticker}")
    int_days = int(days)
    end = int(time.time() * 1000)
    start = end - int_days * 24 * 60 * 60 * 1000
    interval = "day" if int_days > 60 else "minute"
    req = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/{interval}/{start}/{end}?limit=50000&apiKey={key}"
    data = do_req(req)
    data_array = np.array(data["results"])
    prices = []
    timestamps = []
    readable_dates = []
    for row in data_array:
        prices.append(row["c"])
        timestamp = row["t"]
        timestamps.append(timestamp)
        readable_dates.append(
            f"{datetime.datetime.fromtimestamp(int(timestamp) / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC"
        )

    return np.array(prices), np.array(readable_dates), np.array(timestamps)


###################
# DATA SOURCE SELECTOR #
###################

# Mapping of common crypto tickers to CoinGecko IDs
CRYPTO_MAPPING = {
    "BTC": "bitcoin",
    "ETH": "ethereum", 
    "XMR": "monero",
    "AVAX": "avalanche-2",
    "ADA": "cardano",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu",
    "MATIC": "matic-network",
    "SOL": "solana",
    "ATOM": "cosmos",
    "NEAR": "near",
    "FTM": "fantom",
    "ALGO": "algorand",
    "VET": "vechain"
}

def get_data_source(ticker):
    """Determine the best data source for a given ticker"""
    # Check if it's a known crypto
    if ticker in CRYPTO_MAPPING:
        return "coingecko", CRYPTO_MAPPING[ticker]
    
    # Default to Polygon for stocks and other assets
    return "polygon", ticker

def get_historic_price(ticker, days, polygon_key):
    """Get historical price data using the best available source"""
    source, identifier = get_data_source(ticker)
    
    try:
        if source == "coingecko":
            return get_coin_historic_price_coingecko(identifier, days)
        else:
            return get_coin_historic_price_polygon(identifier, days, polygon_key)
    except Exception as e:
        print(f"Error with {source} for {ticker}: {e}")
        # Fallback to Polygon if CoinGecko fails
        if source == "coingecko":
            print(f"Falling back to Polygon for {ticker}")
            try:
                return get_coin_historic_price_polygon(ticker, days, polygon_key)
            except Exception as polygon_error:
                print(f"Polygon fallback also failed for {ticker}: {polygon_error}")
                # If both fail, provide helpful error message
                if "rate limit" in str(e).lower():
                    print(f"💡 Tip: Add COIN_GECKO API key to environment for higher rate limits")
                raise polygon_error
        else:
            raise e


###################
# MATPLOTLIB PART #
###################


async def get_fig(days, tickers):
    coins_prices = []
    coins_timestamps = []
    oldest_readable_date = None
    oldest_timestamps = None
    age = np.inf
    key = os.getenv("POLYGON")
    
    for ticker in tickers:
        prices, readable_dates, timestamps = get_historic_price(ticker, days, key)
        # find the oldest coin
        if age > timestamps[0]:
            oldest_readable_date = readable_dates
            oldest_timestamps = timestamps
            age = timestamps[0]
        # append one coin to data
        coins_prices.append(prices)
        coins_timestamps.append(timestamps)

    # plot size
    fig = plt.figure(figsize=(15, 6))

    # define ticks (hacky)
    days_num = int(days)
    ticks_num = 11
    ticks = np.int32(np.linspace(0, oldest_timestamps.shape[0] - 1, ticks_num))
    mini = 1
    # for each coin in data
    for i, d in enumerate(coins_prices):
        # normalize
        normalized = d / d.max()
        # plot line for one coin
        plt.plot(coins_timestamps[i], normalized, linewidth=3)
        # for first coin plot price text
        if i == 0:
            ticks_first_coin = np.int32(
                np.linspace(0, coins_timestamps[i].shape[0] - 1, ticks_num)
            )
            for x, y, z in zip(
                coins_timestamps[i][ticks_first_coin],
                np.array(normalized)[ticks_first_coin],
                np.array(d)[ticks_first_coin],
            ):
                plt.text(
                    x,
                    y,
                    f"{round(z)}",
                    color="white",
                    size=8,
                    rotation=90,
                    path_effects=[pe.withStroke(linewidth=2, foreground="black")],
                )
        # find global minimum
        norm_mini = normalized.min()
        if norm_mini < mini:
            mini = norm_mini
    if mini > 0.9:
        mini = 0.9
    # print full date
    plt.gca().set_xticks(oldest_timestamps[ticks])
    plt.gca().set_xticklabels(oldest_readable_date[ticks], rotation=45, ha="right")
    # other matplotlib stuff
    price_ticks = np.linspace(0, 1, 11)
    plt.gca().set_yticks(price_ticks)
    plt.gca().set_yticklabels((price_ticks * 100).astype(int))
    plt.gca().set_ylim(mini - 0.05, 1.05)
    plt.gca().set_xlim(oldest_timestamps[0], oldest_timestamps[-1])
    plt.grid(linewidth=2, color="#595959", linestyle="--")
    plt.legend(tickers, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xlabel("time")
    plt.ylabel("%")
    plt.title(
        f"{('last day' if days_num == 1 else f'{days} days')} asset price comparison"
    )
    plt.tight_layout()

    return fig


def main(save):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if len(sys.argv) == 1:
        task = get_fig("365", default_tickers)
    elif len(sys.argv) == 2:
        task = get_fig(sys.argv[1], default_tickers)
    else:
        task = get_fig(sys.argv[1], sys.argv[2:])

    try:
        loop.run_until_complete(task)
        args = [arg.replace(":", "") for arg in sys.argv[1:]]
        if save:
            plt.savefig(
                "pics/"
                + command_prefix
                + ("_" if len(args) > 0 else "")
                + "_".join(args)
                + ".png"
            )
        else:
            plt.show(block=True)
    except Exception as e:
        print(e.__class__.__name__)


# for running the script locally
if __name__ == "__main__":
    main(save=False)
