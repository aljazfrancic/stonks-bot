import os
import io
import datetime
import json
import numpy as np
import nextcord
import matplotlib.pyplot as plt

plt.style.use("dark_background")

from requests import Request, Session

from dotenv import load_dotenv
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

#################
# API CALL HACK #
#################

def do_req(url):
    headers = {"Accepts": "application/json"}
    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url)
        data = json.loads(response.text)
    except Exception as e:
        print(e)
        data = None
    return data

##################
# COINGECKO PART #
##################

# get historical data for one coin
def get_coin_historic_prix_gecko(coin, days):
    print(coin)
    data = do_req("https://api.coingecko.com/api/v3/coins/" + coin + "/market_chart?vs_currency=usd&days=" + str(days))["prices"]
    data_arr = np.flip(np.array(data), 0)
    prixes = data_arr[:, 1]
    dates = data_arr[:, 0]
    readable_dates = []
    for date in dates:
        readable_dates.append(datetime.datetime.utcfromtimestamp(int(date)/1000).strftime('%Y-%m-%d %H:%M:%S') + " UTC")
    readable = np.array(readable_dates)
    return prixes, readable, dates

###################
# MATPLOTLIB PART #
###################

async def print_graph(coins, data, timestamps, longreadable, longstamp, colors, linestyle, linewidth, discord_channel, days, title_addon):
    # threshold for number of datapoints for displaying avax price and showing dates on x axis labels
    thresh = 35
    # rounding
    rounding = 1
    # plot size
    plt.figure(figsize=(15, 6))
    # define ticks (hacky)
    days_num = longstamp.shape[0] if days == "max" else int(days)
    tikz = np.int32(np.linspace(0, longstamp.shape[0] - 1, 25 if days_num == 1 else (thresh if days_num > thresh else (days_num + 1))))
    mini = 1
    # for each currency in data
    for i, d in enumerate(data):
        # normalize
        normalized = d / d.max()
        # plot line for one currency using defined color, linestyle, etc.
        plt.plot(
            timestamps[i],
            normalized,
            color = "#" + colors[i],
            linestyle = linestyle[i],
            linewidth = linewidth[i]
        )
        # if avax plot price
        if coins[i] == "avalanche-2":
            tikzava = np.int32(np.linspace(0, timestamps[i].shape[0] - 1, 25 if days_num == 1 else (thresh if days_num > thresh else (days_num + 1))))
            if timestamps[i].shape[0] * 2 > longstamp.shape[0]:
                for x, y, z in zip(timestamps[i][tikzava], np.array(normalized)[tikzava], np.array(d)[tikzava]):
                    plt.text(
                        x,
                        y,
                        str(round(z, rounding)),
                        color = "white",
                        weight = "bold",
                        size = 10,
                        rotation = 90,
                    )
        # find global minimum
        norm_mini = normalized.min()
        if norm_mini < mini:
            mini = norm_mini
    # print full date instead of number of points in the past
    plt.gca().set_xticks(longstamp[tikz])
    plt.gca().set_xticklabels(longreadable[tikz], rotation = 45, ha = "right")
    # other matplotlib stuff
    plt.gca().set_yticks(np.linspace(0, 1, 11))
    plt.gca().set_ylim(mini - 0.05, 1.05)
    plt.grid(color = "#595959", linestyle = '--')
    plt.legend(coins, bbox_to_anchor = (1.04, 1), loc = "upper left")
    plt.xlabel("time")
    plt.ylabel("$$$")
    plt.title(title_addon + ": " + ("last day" if days_num == 1 else days + " days") + " crypto price comparison")
    
    # print image ot discord channel
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    await discord_channel.send(file=nextcord.File(buf, "image.png"))
    buf.close()
    
    plt.close()

async def print_all_graphs(discord_channel, days):    
    coins = ["avalanche-2", "avalaunch", "roco-finance", "lydia-finance", "penguin-finance", "avaware", "yay-games"]
    colors = ["ff0000", "ffff00", "f55307", "9c5bfc", "e314a8", "1864d6", "00ff00"]
    linestyle = ["-", "-", "--", "--", "-", "-", "-"]
    linewidth = [2, 2, 1, 1, 1, 1, 1]
    title_addon = "Launchpads"
    
    await call_print_graph(discord_channel, days, coins, colors, linestyle, linewidth, title_addon)
    
    coins = ["avalanche-2", "pangolin", "benqi", "snowball-token", "hurricaneswap-token", "elk-finance", "yield-yak", "oh-finance", "beefy-finance", "chainlink"]
    colors = ["ff0000", "ed8c0c", "065f9e" , "0cdcf7", "8a07e8", "1f6e07", "36c70a", "ed05d6", "ffffff", "3271fa"]
    linestyle = ["-", "-", "-", "--", "--", "--", "--", "-", "-", "--"]
    linewidth = [2, 2, 2, 1, 1, 1, 1, 1, 1, 1]
    title_addon = "Defi"
    
    await call_print_graph(discord_channel, days, coins, colors, linestyle, linewidth, title_addon)
    
    coins = ["avalanche-2", "crabada", "treasure-under-sea", "talecraft"]
    colors = ["ff0000", "25c4fa", "ffff00", "f20ca9"]
    linestyle = ["-", "-", "-", "-"]
    linewidth = [2, 2, 2, 2]
    title_addon = "Game-Fi"
    
    await call_print_graph(discord_channel, days, coins, colors, linestyle, linewidth, title_addon)
    
    coins = ["avalanche-2", "baguette", "snowbank", "hoopoe", "gondola-finance", "sherpa"]
    colors = ["ff0000", "ffdb6e", "858585", "ffbf00", "ff0000", "00ff00"]
    linestyle = ["-", "-", "-", "-", "--", "-"]
    linewidth = [2, 2, 2, 2, 2, 2]
    title_addon = "Gems #1"
    
    await call_print_graph(discord_channel, days, coins, colors, linestyle, linewidth, title_addon)
    
    coins = ["bitcoin", "ethereum", "monero", "avalanche-2", "avalaunch"]
    colors = ["ffffff", "9e9e9e", "ff8800", "ff0000", "ffff00"]
    linestyle = [":", ":", ":", "-", "-"]
    linewidth = [2, 2, 2, 2, 2]
    title_addon = "Old coins"
    
    await call_print_graph(discord_channel, days, coins, colors, linestyle, linewidth, title_addon)
    
    coins = ["shiba-inu", "dogecoin", "polkadot", "cardano", "ripple", "binancecoin", "solana", "avalanche-2", "bitcoin", "ethereum", "monero"]
    colors = ["f58b00", "f0e19e", "e60bba", "2240e6", "fffef0", "f5dd42", "429ef5", "ff0000", "ffffff", "9e9e9e", "ff8800"]
    linestyle = ["-", "-", "--", "--", "--", "--", "--", "-",":", ":", ":"]
    linewidth = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2]
    title_addon = "Top coins"
    
    await call_print_graph(discord_channel, days, coins, colors, linestyle, linewidth, title_addon)

async def call_print_graph(discord_channel, days, coins, colors, linestyle, linewidth, title_addon):
    data = []
    timestamps = []
    longreadable = None
    longstamp = None
    age = np.Inf
    for i, coin in enumerate(coins):
        history, datescoin, ts = get_coin_historic_prix_gecko(coin, days)
        # find oldest coin
        if age > ts[-1]:
            longreadable = datescoin
            longstamp = ts
            age = ts[-1]
        # append one coin to data
        data.append(history)
        timestamps.append(ts)
    await print_graph(coins, data, timestamps, longreadable, longstamp, colors, linestyle, linewidth, discord_channel, days, title_addon)

###############
# DICORD PART #
###############

discord_client = nextcord.Client()

@discord_client.event
async def on_ready():
    print(str(discord_client.user) + " reporting for duty!")

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    command_one = "!kekw"
    if message.content[: len(command_one)] == command_one:
        await message.channel.send("Roger, roger!")
        await print_all_graphs(message.channel, message.content.split()[1])

discord_client.run(DISCORD_TOKEN)
