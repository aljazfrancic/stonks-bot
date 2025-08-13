from stonks import get_fig, default_tickers, command_prefix
import matplotlib.pyplot as plt
import discord
import os
import io

################
# DISCORD PART #
################

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    command_split = message.content.split()
    print(command_split)
    if command_split[0] == command_prefix:
        await message.channel.send("Roger, roger!")
        try:
            if len(command_split) == 1:
                fig = await get_fig("365", default_tickers)
            elif len(command_split) == 2:
                fig = await get_fig(command_split[1], default_tickers)
            else:
                fig = await get_fig(command_split[1], command_split[2:])

            # print image to discord channel
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            await message.channel.send(file=discord.File(buf, "stonks.png"))
            buf.close()
            plt.close("all")

        except Exception as e:
            print(e.__class__.__name__)
            await message.channel.send(e.__class__.__name__)


@client.event
async def on_ready():
    print(f"{client.user} reporting for duty!")


if __name__ == "__main__":
    secret = os.getenv("DISCORD_TOKEN")
    client.run(secret)
