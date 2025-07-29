# Deployment Guide

This guide will help you deploy your Flask application to various hosting platforms.

## Railway (Recommended)

Railway is a modern platform that makes it easy to deploy Flask applications.

### Prerequisites
- GitHub account
- Railway account (free tier available)

### Steps

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

2. **Connect to Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign up with your GitHub account
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Configure Environment Variables**:
   - In Railway dashboard, go to your project
   - Click on "Variables" tab
   - Add your Google Ad Manager credentials as environment variables:
     ```
     GOOGLEADS_YAML_CONTENT=<your-googleads-yaml-content>
     DFP_NETWORK_CODE=<your-network-code>
     ```

4. **Deploy**:
   - Railway will automatically detect it's a Python app
   - It will install dependencies from `requirements.txt`
   - Your app will be deployed and get a URL

### Railway Configuration Files

Railway automatically detects Python apps, but you can add a `railway.json` file for custom configuration:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd lineitem_flask_app && python app.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Alternative Platforms

### Render

1. **Create a Render account** at [render.com](https://render.com)
2. **Connect your GitHub repository**
3. **Create a new Web Service**
4. **Configure**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd lineitem_flask_app && python app.py`
   - **Environment Variables**: Add your GAM credentials

### Heroku

1. **Install Heroku CLI**
2. **Create `Procfile`**:
   ```
   web: cd lineitem_flask_app && python app.py
   ```
3. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### PythonAnywhere

1. **Sign up** at [pythonanywhere.com](https://pythonanywhere.com)
2. **Upload your code** or clone from GitHub
3. **Configure WSGI file** to point to your Flask app
4. **Set environment variables** for your credentials

## Environment Variables

For security, store sensitive data as environment variables:

```python
# In your app.py, replace hardcoded values with:
import os

# Instead of hardcoded network code
network_code = os.environ.get('DFP_NETWORK_CODE', 'default-network')

# Instead of hardcoded credentials
googleads_yaml_content = os.environ.get('GOOGLEADS_YAML_CONTENT')
```

## SSL/HTTPS

Most platforms (Railway, Render, Heroku) provide automatic SSL certificates.

## Custom Domain

- **Railway**: Add custom domain in project settings
- **Render**: Configure in your web service settings
- **Heroku**: Use `heroku domains:add yourdomain.com`

## Monitoring

- **Railway**: Built-in logs and metrics
- **Render**: Logs available in dashboard
- **Heroku**: `heroku logs --tail`

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure `requirements.txt` includes all dependencies
   - Check Python version compatibility

2. **Environment Variables**:
   - Verify all required env vars are set
   - Check variable names match your code

3. **Port Configuration**:
   - Most platforms expect the app to run on `PORT` environment variable
   - Update your Flask app to use: `port = int(os.environ.get('PORT', 5000))`

4. **File Paths**:
   - Ensure all file paths are relative to the project root
   - Check that `googleads.yaml` is accessible

### Debugging

- Check platform-specific logs
- Verify environment variables are set correctly
- Test locally with the same environment variables 