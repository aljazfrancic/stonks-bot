import os
import datetime
import io
import json
import urllib3
import numpy as np
import matplotlib.pyplot as plt
import discord
from dotenv import load_dotenv

load_dotenv()

plt.style.use("dark_background")


#################
# API CALL HACK #
#################

def do_req(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    return json.loads(response.data)


##################
# COINGECKO PART #
##################

# get historical data for one coin
def get_coin_historic_prix_gecko(coin, days):
    print(coin)
    data = do_req("https://api.coingecko.com/api/v3/coins/" + coin + "/market_chart?vs_currency=usd&days=" + str(days))[
        "prices"]
    data_arr = np.flip(np.array(data), 0)
    prixes = data_arr[:, 1]
    dates = data_arr[:, 0]
    readable_dates = []
    for date in dates:
        readable_dates.append(
            datetime.datetime.fromtimestamp(int(date) / 1000, datetime.timezone.utc).strftime(
                '%Y-%m-%d %H:%M:%S') + " UTC")
    readable = np.array(readable_dates)
    return prixes, readable, dates


###################
# MATPLOTLIB PART #
###################

async def print_graph(chan, days, coins, colors, linestyle, linewidth, title_addon):
    data = []
    timestamps = []
    longreadable = None
    longstamp = None
    age = np.Inf
    for i, coin in enumerate(coins):
        history, datescoin, ts = get_coin_historic_prix_gecko(coin, days)
        # find the oldest coin
        if age > ts[-1]:
            longreadable = datescoin
            longstamp = ts
            age = ts[-1]
        # append one coin to data
        data.append(history)
        timestamps.append(ts)

    # threshold for number of datapoints for displaying avax price and showing dates on x-axis labels
    thresh = 35
    # rounding
    rounding = 1
    # plot size
    plt.figure(figsize=(15, 6))
    # define ticks (hacky)
    days_num = longstamp.shape[0] if days == "max" else int(days)
    tikz = np.int32(np.linspace(0, longstamp.shape[0] - 1,
                                25 if days_num == 1 else (thresh if days_num > thresh else (days_num + 1))))
    mini = 1
    # for each currency in data
    for i, d in enumerate(data):
        # normalize
        normalized = d / d.max()
        # plot line for one currency using defined color, linestyle, etc.
        plt.plot(
            timestamps[i],
            normalized,
            color="#" + colors[i],
            linestyle=linestyle[i],
            linewidth=linewidth[i]
        )
        # if avax plot price
        if coins[i] == "avalanche-2":
            tikzava = np.int32(np.linspace(0, timestamps[i].shape[0] - 1,
                                           25 if days_num == 1 else (thresh if days_num > thresh else (days_num + 1))))
            if timestamps[i].shape[0] * 2 > longstamp.shape[0]:
                for x, y, z in zip(timestamps[i][tikzava], np.array(normalized)[tikzava], np.array(d)[tikzava]):
                    plt.text(
                        x,
                        y,
                        str(round(z, rounding)),
                        color="white",
                        weight="bold",
                        size=10,
                        rotation=90,
                    )
        # find global minimum
        norm_mini = normalized.min()
        if norm_mini < mini:
            mini = norm_mini
    # print full date instead of number of points in the past
    plt.gca().set_xticks(longstamp[tikz])
    plt.gca().set_xticklabels(longreadable[tikz], rotation=45, ha="right")
    # other matplotlib stuff
    plt.gca().set_yticks(np.linspace(0, 1, 11))
    plt.gca().set_ylim(mini - 0.05, 1.05)
    plt.grid(color="#595959", linestyle='--')
    plt.legend(coins, bbox_to_anchor=(1.04, 1), loc="upper left")
    plt.xlabel("time")
    plt.ylabel("$$$")
    plt.title(title_addon + ": " + ("last day" if days_num == 1 else str(days) + " days") + " crypto price comparison")

    # print image to discord channel
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    await chan.send(file=discord.File(buf, "image.png"))
    buf.close()

    plt.close()


###############
# LOCAL DEBUG #
###############

days = 365
coins = ["bitcoin", "ethereum"]  # , "monero", "avalanche-2", "avalaunch"
colors = ["ffffff", "9e9e9e", "ff8800", "ff0000", "ffff00"]
linestyle = [":", ":", ":", "-", "-"]
linewidth = [2, 2, 2, 2, 2]
title_addon = "old coins"

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
        await print_graph(message.channel, days, coins, colors, linestyle, linewidth, title_addon)


@client.event
async def on_ready():
    print(f'{client.user} reporting for duty!')


secret = os.getenv("DISCORD_TOKEN")

client.run(secret)
