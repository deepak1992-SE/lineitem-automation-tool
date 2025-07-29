#!/bin/bash

# GitHub Setup Script for Line Item Automation Tool
# This script will help you initialize Git and push to GitHub

echo "🚀 Setting up GitHub repository for Line Item Automation Tool"
echo "=========================================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Initialize git repository
echo "📁 Initializing Git repository..."
git init

# Add all files
echo "📝 Adding files to Git..."
git add .

# Make initial commit
echo "💾 Making initial commit..."
git commit -m "Initial commit: Line Item Automation Tool with currency exchange support"

# Set main as default branch
echo "🌿 Setting main as default branch..."
git branch -M main

echo ""
echo "✅ Git repository initialized successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Choose a repository name (e.g., 'lineitem-automation-tool')"
echo "   - Make it public or private as you prefer"
echo "   - DO NOT initialize with README, .gitignore, or license (we already have these)"
echo ""
echo "2. Connect your local repository to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo ""
echo "3. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "4. Deploy to Railway:"
echo "   - Go to https://railway.app"
echo "   - Sign up with GitHub"
echo "   - Create new project from GitHub repo"
echo "   - Add environment variables for your GAM credentials"
echo ""
echo "🔐 Important: Make sure your googleads.yaml file is NOT committed to Git!"
echo "   It should be in .gitignore to keep your credentials secure."
echo ""
echo "📖 See DEPLOYMENT.md for detailed deployment instructions." 