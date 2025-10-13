#!/bin/bash

# Frontend Deployment Script for Railway
# This script helps deploy the Style AI frontend to Railway

echo "🚀 Style AI Frontend Deployment Script"
echo "======================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Please run this script from the frontend/style-ai directory"
    exit 1
fi

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "⚠️  .env.production not found. Creating from template..."
    cp env.production.template .env.production
    echo "📝 Please edit .env.production with your actual values before deploying"
    echo "   Required variables:"
    echo "   - VITE_API_URL (your Railway backend URL)"
    echo "   - VITE_STRIPE_PUBLISHABLE_KEY (your Stripe key)"
    exit 1
fi

echo "✅ Environment file found"

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway whoami > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Please login to Railway:"
    railway login
fi

# Initialize Railway project (if not already initialized)
if [ ! -f ".railway/project.json" ]; then
    echo "🚂 Initializing Railway project..."
    railway init
fi

echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your frontend should be available at the Railway URL shown above"
echo "📊 Monitor your deployment at: https://railway.app/dashboard"

