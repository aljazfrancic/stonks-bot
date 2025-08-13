"""
Discord Bot for Stonks - Cryptocurrency and Stock Price Comparison

This bot responds to Discord messages with price comparison charts
using the stonks module.
"""

from stonks import get_fig, DEFAULT_TICKERS, COMMAND_PREFIX, StonksError
import matplotlib.pyplot as plt
import discord
import os
import io
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Discord bot configuration
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_message(message):
    """Handle incoming Discord messages."""
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # Parse command
    command_parts = message.content.split()
    
    # Check if this is a stonks command
    if command_parts[0] != COMMAND_PREFIX:
        return
    
    logger.info(f"Received stonks command from {message.author}: {message.content}")
    
    # Send initial response
    await message.channel.send("🔄 Generating your stonks chart...")
    
    try:
        # Determine parameters
        if len(command_parts) == 1:
            # Default: 365 days with default tickers
            fig = await get_fig("365", DEFAULT_TICKERS)
        elif len(command_parts) == 2:
            # Days specified, use default tickers
            days = command_parts[1]
            fig = await get_fig(days, DEFAULT_TICKERS)
        else:
            # Days and custom tickers specified
            days = command_parts[1]
            tickers = command_parts[2:]
            fig = await get_fig(days, tickers)
        
        # Send the chart
        await send_chart(message.channel, fig)
        
    except StonksError as e:
        error_msg = f"❌ Error generating chart: {str(e)}"
        logger.error(f"StonksError for user {message.author}: {e}")
        await message.channel.send(error_msg)
        
    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        logger.error(f"Unexpected error for user {message.author}: {e}", exc_info=True)
        await message.channel.send(error_msg)


async def send_chart(channel, fig: plt.Figure) -> None:
    """Send a matplotlib figure as a Discord file."""
    try:
        # Create a bytes buffer for the image
        buf = io.BytesIO()
        
        # Save the figure to the buffer with high quality
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        
        # Send the file to Discord
        file = discord.File(buf, filename="stonks_chart.png")
        await channel.send("📈 Here's your stonks chart!", file=file)
        
        # Clean up
        buf.close()
        plt.close(fig)
        
    except Exception as e:
        logger.error(f"Error sending chart: {e}")
        await channel.send(f"❌ Error sending chart: {str(e)}")


@client.event
async def on_ready():
    """Called when the bot is ready."""
    logger.info(f"🤖 {client.user} is online and ready!")
    logger.info(f"Bot ID: {client.user.id}")
    logger.info(f"Connected to {len(client.guilds)} guild(s)")
    
    # Set bot status
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="!stonks for charts"
        )
    )


@client.event
async def on_error(event, *args, **kwargs):
    """Handle Discord client errors."""
    logger.error(f"Discord client error in event {event}", exc_info=True)


def main():
    """Main function to run the Discord bot."""
    # Get Discord token from environment
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        return
    
    try:
        # Run the bot
        logger.info("Starting Discord bot...")
        client.run(token)
        
    except discord.LoginFailure:
        logger.error("Invalid Discord token!")
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)


if __name__ == "__main__":
    main()
