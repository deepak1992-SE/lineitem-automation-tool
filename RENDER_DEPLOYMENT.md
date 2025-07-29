# Render Deployment Guide

This guide will walk you through deploying your Line Item Automation Tool to Render.

## Prerequisites

- ✅ GitHub repository (already done!)
- Render account (free)

## Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with your GitHub account
4. Complete the signup process

## Step 2: Deploy from GitHub

1. **In Render Dashboard:**
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub account if not already connected

2. **Select Repository:**
   - Choose `deepak1992-SE/lineitem-automation-tool`
   - Click "Connect"

3. **Configure Web Service:**

   **Basic Settings:**
   - **Name**: `lineitem-automation-tool` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you (e.g., Oregon for US)

   **Build & Deploy Settings:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd lineitem_flask_app && python app.py`

4. **Click "Create Web Service"**

## Step 3: Configure Environment Variables

After deployment, go to your service dashboard and add these environment variables:

### Required Variables:

1. **`GOOGLEADS_YAML_CONTENT`**
   - Copy the entire content of your `googleads.yaml` file
   - Paste it as the value for this environment variable

2. **`DFP_NETWORK_CODE`**
   - Your Google Ad Manager network code
   - Example: `123456789`

### Optional Variables:

3. **`FLASK_ENV`**
   - Value: `production`

4. **`SECRET_KEY`**
   - Generate a random string for Flask secret key
   - Example: `your-super-secret-key-here`

## Step 4: Update Code for Environment Variables

Since Render doesn't have a `googleads.yaml` file, we need to modify the code to use environment variables. Let me create a patch for you:

### Create a new file: `googleads_env.py`

```python
import os
import tempfile
import yaml

def create_googleads_yaml_from_env():
    """Create googleads.yaml file from environment variable"""
    yaml_content = os.environ.get('GOOGLEADS_YAML_CONTENT')
    if not yaml_content:
        raise ValueError("GOOGLEADS_YAML_CONTENT environment variable not set")
    
    # Create temporary googleads.yaml file
    temp_dir = tempfile.gettempdir()
    yaml_path = os.path.join(temp_dir, 'googleads.yaml')
    
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    return yaml_path
```

### Update your app.py to use this:

Add this at the top of your `app.py`:

```python
import os
from googleads_env import create_googleads_yaml_from_env

# Create googleads.yaml from environment variable if on Render
if os.environ.get('RENDER'):
    googleads_path = create_googleads_yaml_from_env()
    os.environ['GOOGLEADS_YAML_FILE'] = googleads_path
```

## Step 5: Test Your Deployment

1. **Wait for deployment** (usually 2-5 minutes)
2. **Check logs** for any errors
3. **Visit your app URL** (provided by Render)
4. **Test the form** with your GAM credentials

## Step 6: Custom Domain (Optional)

1. **In Render Dashboard:**
   - Go to your web service
   - Click "Settings"
   - Scroll to "Custom Domains"
   - Add your domain

2. **Configure DNS:**
   - Add CNAME record pointing to your Render URL
   - Wait for SSL certificate (automatic)

## Troubleshooting

### Common Issues:

1. **"Module not found" errors:**
   - Check `requirements.txt` includes all dependencies
   - Verify build command is correct

2. **"Google Ad Manager connection failed":**
   - Verify `GOOGLEADS_YAML_CONTENT` is set correctly
   - Check your GAM credentials are valid

3. **"Port already in use":**
   - Render automatically handles port configuration
   - Your app should use `os.environ.get('PORT', 5000)`

4. **"Environment variable not found":**
   - Double-check environment variable names
   - Ensure they're added to the correct service

### Debugging:

1. **Check Render logs:**
   - Go to your service dashboard
   - Click "Logs" tab
   - Look for error messages

2. **Test locally with same environment:**
   ```bash
   export GOOGLEADS_YAML_CONTENT="your-yaml-content"
   export DFP_NETWORK_CODE="your-network-code"
   cd lineitem_flask_app && python app.py
   ```

## Render Features You Get:

- ✅ **Free SSL certificate**
- ✅ **Automatic deployments** from GitHub
- ✅ **Custom domains**
- ✅ **Built-in logging**
- ✅ **Environment variables**
- ✅ **Auto-scaling** (if needed)

## Cost:

- **Free tier**: 750 hours/month
- **Your app**: Will use ~730 hours/month (24/7)
- **Result**: Completely free! 🎉

## Next Steps:

1. **Deploy to Render** using the steps above
2. **Test thoroughly** with your GAM credentials
3. **Share your app URL** with your team
4. **Monitor usage** in Render dashboard

Your Flask app will be live and accessible to anyone with the URL! 🚀 