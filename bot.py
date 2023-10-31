import os
import datetime
import io
import json
import urllib3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import discord
from dotenv import load_dotenv

load_dotenv()

plt.style.use("dark_background")


#################
# API CALL HACK #
#################

def do_req(url):
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return json.loads(response.data)


##################
# COINGECKO PART #
##################

# get historical data for one coin
def get_coin_historic_price_gecko(coin, days):
    print(coin)
    data = do_req(f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days={str(days)}")[
        "prices"]
    data_array = np.array(data)
    prices = data_array[:, 1]
    timestamps = data_array[:, 0]
    readable_dates = []
    for date in timestamps:
        readable_dates.append(
            f"{datetime.datetime.fromtimestamp(int(date) / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    readable_dates = np.array(readable_dates)
    return prices, readable_dates, timestamps


###################
# MATPLOTLIB PART #
###################

async def print_graph(chan, days, coins):
    coins_prices = []
    coins_timestamps = []
    oldest_readable_date = None
    oldest_timestamps = None
    age = np.Inf
    for coin in coins:
        prices, readable_dates, timestamps = get_coin_historic_price_gecko(coin, days)
        # find the oldest coin
        if age > timestamps[0]:
            oldest_readable_date = readable_dates
            oldest_timestamps = timestamps
            age = timestamps[0]
        # append one coin to data
        coins_prices.append(prices)
        coins_timestamps.append(timestamps)

    # threshold for number of datapoints for displaying first coin's price and showing dates on x-axis labels
    threshold = 35
    # plot size
    plt.figure(figsize=(15, 6))
    # define ticks (hacky)
    days_num = oldest_timestamps.shape[0] if days == "max" else int(days)
    ticks = np.int32(np.linspace(0, oldest_timestamps.shape[0] - 1,
                                 25 if days_num == 1 else (threshold if days_num > threshold else (days_num + 1))))
    mini = 1
    # for each coin in data
    for i, d in enumerate(coins_prices):
        # normalize
        normalized = d / d.max()
        # plot line for one coin
        plt.plot(coins_timestamps[i], normalized)
        # for first coin plot price text
        if i == 0:
            ticks_first_coin = np.int32(np.linspace(0, coins_timestamps[i].shape[0] - 1,
                                                    25 if days_num == 1 else (
                                                        threshold if days_num > threshold else (days_num + 1))))
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
    plt.gca().set_yticks(np.linspace(0, 1, 11))
    plt.gca().set_ylim(mini - 0.05, 1.05)
    plt.grid(color="#595959", linestyle="--")
    plt.legend(coins, bbox_to_anchor=(1, 1), loc="upper left")
    plt.xlabel("time")
    plt.ylabel("$$$")
    plt.title(f"{('last day' if days_num == 1 else f'{days} days')}" + " crypto price comparison")

    # print image to discord channel
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    await chan.send(file=discord.File(buf, "image.png"))
    buf.close()

    plt.close()


################
# DISCORD PART #
################

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    command_prefix = "!kekw"
    if message.content[: len(command_prefix)] == command_prefix:
        await message.channel.send("Roger, roger!")
        await print_graph(message.channel, 1, ["bitcoin", "ethereum", "monero"])
        await print_graph(message.channel, 7, ["bitcoin", "ethereum", "monero"])
        await print_graph(message.channel, 365, ["bitcoin", "ethereum", "monero"])
        await print_graph(message.channel, "max", ["bitcoin", "ethereum", "monero"])
        # await print_graph(message.channel, "max", ["monero", "bitcoin", "ethereum"])


@client.event
async def on_ready():
    print(f"{client.user} reporting for duty!")


secret = os.getenv("DISCORD_TOKEN")

client.run(secret)
