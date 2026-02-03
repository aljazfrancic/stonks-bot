#!/bin/bash

# Stonks Bot Setup Script
echo "Setting up Stonks Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.12+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python $python_version detected"

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
# Discord Bot Configuration
# Get your bot token from: https://discord.com/developers/applications
DISCORD_TOKEN=your_discord_bot_token_here

# CoinGecko API Configuration
# Get your API key from: https://www.coingecko.com/en/api
COIN_GECKO=your_coingecko_api_key_here

# Polygon.io API Configuration
# Get your API key from: https://polygon.io/
POLYGON=your_polygon_api_key_here
EOF
    echo "Please edit .env file with your actual API keys"
else
    echo ".env file already exists"
fi

# Create .env.example if it doesn't exist
if [ ! -f .env.example ]; then
    echo "Creating .env.example file..."
    cat > .env.example << EOF
# Discord Bot Configuration
# Get your bot token from: https://discord.com/developers/applications
DISCORD_TOKEN=your_discord_bot_token_here

# CoinGecko API Configuration
# Get your API key from: https://www.coingecko.com/en/api
COIN_GECKO=your_coingecko_api_key_here

# Polygon.io API Configuration
# Get your API key from: https://polygon.io/
POLYGON=your_polygon_api_key_here
EOF
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: python3 bot.py"
echo "3. Or run locally: python3 stonks.py" 
