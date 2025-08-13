#!/usr/bin/env python3
"""
Railway Environment Variables Setup Script

This script helps you set up environment variables in Railway
by reading from your local .env file and providing the commands
to run in Railway CLI.
"""

import os
import sys
from pathlib import Path

def read_env_file():
    """Read the .env file and return environment variables."""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your secrets first.")
        return {}
    
    env_vars = {}
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        return env_vars
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return {}

def generate_railway_commands(env_vars):
    """Generate Railway CLI commands for setting environment variables."""
    if not env_vars:
        return
    
    print("🚂 Railway CLI Commands:")
    print("=" * 50)
    
    for key, value in env_vars.items():
        # Mask sensitive values for display
        if 'TOKEN' in key.upper() or 'KEY' in key.upper() or 'SECRET' in key.upper():
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"railway variables set {key}={masked_value}")
        else:
            print(f"railway variables set {key}={value}")
    
    print("\n" + "=" * 50)

def generate_dashboard_instructions(env_vars):
    """Generate instructions for Railway Dashboard."""
    if not env_vars:
        return
    
    print("\n🖥️  Railway Dashboard Instructions:")
    print("=" * 50)
    print("1. Go to [Railway Dashboard](https://railway.app)")
    print("2. Select your stonks-bot project")
    print("3. Click on your service")
    print("4. Go to 'Variables' tab")
    print("5. Add these variables:")
    print()
    
    for key, value in env_vars.items():
        # Mask sensitive values for display
        if 'TOKEN' in key.upper() or 'KEY' in key.upper() or 'SECRET' in key.upper():
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"   {key} = {masked_value}")
        else:
            print(f"   {key} = {value}")
    
    print("\n" + "=" * 50)

def main():
    """Main function."""
    print("🚂 Stonks Bot Railway Setup")
    print("=" * 50)
    
    # Read environment variables
    env_vars = read_env_file()
    
    if not env_vars:
        print("\n📝 Create a .env file with these variables:")
        print("DISCORD_TOKEN=your_discord_bot_token")
        print("POLYGON=your_polygon_api_key")
        print("LOG_LEVEL=INFO")
        print("ENVIRONMENT=production")
        return
    
    print(f"✅ Found {len(env_vars)} environment variables in .env file")
    
    # Generate Railway CLI commands
    generate_railway_commands(env_vars)
    
    # Generate dashboard instructions
    generate_dashboard_instructions(env_vars)
    
    print("\n🔒 Security Notes:")
    print("- Never share your .env file")
    print("- Use Railway's built-in environment variable management")
    print("- Rotate your API keys regularly")
    
    print("\n🚀 Next Steps:")
    print("1. Choose either Railway CLI or Dashboard method above")
    print("2. Set the environment variables in Railway")
    print("3. Deploy your bot")
    print("4. Test with !stonks command in Discord")

if __name__ == "__main__":
    main()
