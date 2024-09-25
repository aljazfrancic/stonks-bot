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

default_tickers = ["X:BTCUSD", "X:ETHUSD", "X:XMRUSD"]


#################
# API CALL HACK #
#################

def do_req(url):
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return json.loads(response.data)


################
# POLYGON PART #
################

# doesn't use the official https://github.com/polygon-io/client-python
# which would be more elegant

# get historical data for one coin

def get_coin_historic_price_polygon(ticker, days, key):
    print(ticker)
    int_days = int(days)
    end = int(time.time() * 1000)
    start = end - int_days * 24 * 60 * 60 * 1000
    req = (f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/{"day" if int_days > 60 else "minute"}"
           f"/{start}/{end}?limit=50000&apiKey={key}")
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
            f"{datetime.datetime.fromtimestamp(int(timestamp) / 1000,
                                               datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")} UTC")

    return np.array(prices), np.array(readable_dates), np.array(timestamps)


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
        prices, readable_dates, timestamps = get_coin_historic_price_polygon(ticker, days, key)
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

    # threshold for number of datapoints for displaying first coin's price and showing dates on x-axis labels
    threshold = 35

    # define ticks (hacky)
    days_num = int(days)
    ticks_num = 10
    ticks = np.int32(np.linspace(0, oldest_timestamps.shape[0] - 1, ticks_num))
    mini = 1
    # for each coin in data
    for i, d in enumerate(coins_prices):
        # normalize
        normalized = d / d.max()
        # plot line for one coin
        plt.plot(coins_timestamps[i], normalized)
        # for first coin plot price text
        if i == 0:
            ticks_first_coin = np.int32(np.linspace(0, coins_timestamps[i].shape[0] - 1, ticks_num))
            for x, y, z in zip(coins_timestamps[i][ticks_first_coin], np.array(normalized)[ticks_first_coin],
                               np.array(d)[ticks_first_coin]):
                plt.text(
                    x,
                    y,
                    f"{round(z)}",
                    color="white",
                    size=8,
                    rotation=90,
                    path_effects=[pe.withStroke(linewidth=2, foreground="black")]
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
    plt.grid(color="#595959", linestyle="--")
    plt.legend(tickers, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xlabel("time")
    plt.ylabel("%")
    plt.title(f"{("last day" if days_num == 1 else f"{days} days")}" + " asset price comparison")
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
        args = [arg.replace(":", "-") for arg in sys.argv[1:]]
        if save:
            plt.savefig("pics/" + command_prefix + ("_" if len(args) > 0 else "") + "_".join(args) + ".png")
        else:
            plt.show(block=True)
    except Exception as e:
        print(e.__class__.__name__)


# for running the script locally
if __name__ == "__main__":
    main(save=False)
