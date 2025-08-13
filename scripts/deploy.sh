#!/bin/bash

# Stonks Bot Railway Deployment Script
echo "🚀 Deploying Stonks Bot to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
fi

# Initialize Railway project if not already done
if [ ! -f .railway ]; then
    echo "🏗️  Initializing Railway project..."
    railway init
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set environment variables in Railway dashboard"
echo "2. Check deployment logs"
echo "3. Test your bot in Discord" 