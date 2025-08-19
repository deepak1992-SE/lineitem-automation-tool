# 📋 Logging System for Lineitem Automation Tool

This document explains how to use the comprehensive logging system that has been added to your Lineitem Automation Tool.

## 🎯 Overview

The logging system provides:
- **Real-time logging** to both console and files
- **Web-based log viewer** accessible from your Flask app
- **Structured logging** with different log levels
- **Log rotation** to prevent log files from growing too large
- **Error tracking** with full stack traces
- **Search and filtering** capabilities

## 🚀 Quick Start

### 1. View Logs in Browser
- Start your Flask app: `python app.py`
- Visit: `http://localhost:5000/logs`
- Or click the "📋 View Logs" link in the sidebar

### 2. Test the Logging System
```bash
cd lineitem_flask_app
python test_logging.py
```

## 📁 Log Files

The system creates two main log files in the `logs/` directory:

- **`all.log`** - Contains all log messages (DEBUG level and above)
- **`errors.log`** - Contains only ERROR and CRITICAL level messages

### Log File Locations
- **Local Development**: `lineitem_flask_app/logs/`
- **Production/Render**: The logs directory will be created automatically

## 🔍 Log Levels

The system uses standard Python logging levels:

| Level | Description | Console | all.log | errors.log |
|-------|-------------|---------|----------|------------|
| **DEBUG** | Detailed information for debugging | ❌ | ✅ | ❌ |
| **INFO** | General information about program execution | ✅ | ✅ | ❌ |
| **WARNING** | Warning messages for potentially problematic situations | ✅ | ✅ | ❌ |
| **ERROR** | Error messages for serious problems | ✅ | ✅ | ✅ |
| **CRITICAL** | Critical errors that may prevent the program from running | ✅ | ✅ | ✅ |

## 🌐 Web Interface Features

### Main Controls
- **Log File Selector**: Switch between "All Logs" and "Error Logs Only"
- **Search Filter**: Search for specific text in logs
- **Level Filters**: Show/hide specific log levels
- **Auto-refresh**: Automatically refresh logs every 10 seconds
- **Manual Refresh**: Click the refresh button to update logs immediately

### Log Display
- **Color-coded**: Different colors for different log levels
- **Hover Effects**: Hover over log entries for better readability
- **Responsive Design**: Works on both desktop and mobile devices

### Actions
- **View Logs**: Browse through all application logs
- **Clear Logs**: Remove all log entries (use with caution)
- **Return Home**: Go back to the main application

## 🛠️ API Endpoints

The logging system provides these API endpoints:

- **`GET /logs`** - Main logs viewer page
- **`GET /api/logs?file=all.log`** - Get logs as JSON (for AJAX requests)
- **`GET /clear-logs`** - Clear all log files

## 📝 Adding Logging to Your Code

### Basic Usage
```python
import logging

# Get the logger
logger = logging.getLogger(__name__)

# Log different levels
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Error with traceback")
```

### Example from Your App
```python
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            logger.info("Processing form submission")
            form = request.form
            
            order_name = form['order_name']
            logger.info(f"Processing order: {order_name}")
            
            # ... your code ...
            
            logger.info("Form processing completed successfully")
            
        except Exception as e:
            logger.exception("Unexpected error in form processing")
            flash(f"❌ Error: {str(e)}")
```

## 🔧 Configuration

### Log File Settings
- **Max File Size**: 10MB per log file
- **Backup Count**: 5 backup files (total max size: 60MB)
- **Rotation**: Automatic when file size limit is reached

### Customization
You can modify the logging configuration in `app.py`:

```python
def setup_logging():
    # Change log levels
    console_handler.setLevel(logging.INFO)  # Console shows INFO+
    file_handler.setLevel(logging.DEBUG)    # File shows DEBUG+
    error_handler.setLevel(logging.ERROR)   # Error file shows ERROR+
    
    # Change file sizes
    file_handler = logging.handlers.RotatingFileHandler(
        all_logs_file, maxBytes=20*1024*1024, backupCount=10  # 20MB, 10 backups
    )
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Logs Not Appearing
- Check if the `logs/` directory exists
- Verify file permissions
- Check if the Flask app has write access

#### 2. Log Files Too Large
- The system automatically rotates logs
- You can manually clear logs via the web interface
- Check the `maxBytes` and `backupCount` settings

#### 3. Performance Issues
- Disable DEBUG logging in production
- Use level filters to show only relevant logs
- Consider reducing the auto-refresh interval

### Debug Mode
To enable debug logging for troubleshooting:

```python
# In your Flask app
app.debug = True
logging.getLogger().setLevel(logging.DEBUG)
```

## 📊 Monitoring and Alerts

### Log Analysis
- **Error Frequency**: Monitor `errors.log` for recurring issues
- **Performance**: Track INFO level messages for timing information
- **User Activity**: Monitor form submissions and processing

### Integration with External Tools
The log files can be integrated with:
- **Log aggregation services** (ELK Stack, Splunk)
- **Monitoring tools** (Datadog, New Relic)
- **Alert systems** (PagerDuty, OpsGenie)

## 🔒 Security Considerations

- **Log Files**: Store sensitive information carefully
- **Access Control**: Consider restricting access to logs in production
- **Data Retention**: Implement log rotation and cleanup policies
- **PII**: Avoid logging personally identifiable information

## 📚 Best Practices

1. **Use Appropriate Log Levels**
   - DEBUG: Detailed debugging information
   - INFO: General operational information
   - WARNING: Potential issues
   - ERROR: Actual errors
   - CRITICAL: System-breaking errors

2. **Include Context**
   ```python
   logger.info(f"Processing order {order_id} for user {user_email}")
   ```

3. **Log Exceptions Properly**
   ```python
   try:
       # your code
   except Exception as e:
       logger.exception("Failed to process order")  # Includes traceback
   ```

4. **Avoid Logging Sensitive Data**
   ```python
   # ❌ Bad
   logger.info(f"User password: {password}")
   
   # ✅ Good
   logger.info(f"User {username} logged in successfully")
   ```

## 🎉 Benefits

With this logging system, you can now:

✅ **Debug Issues Locally**: No more need to check Render.com logs  
✅ **Monitor Application Health**: Real-time visibility into operations  
✅ **Track User Actions**: See exactly what users are doing  
✅ **Identify Performance Issues**: Monitor processing times and bottlenecks  
✅ **Maintain Audit Trail**: Keep records of all operations  
✅ **Troubleshoot Errors**: Get full context when things go wrong  

## 🚀 Next Steps

1. **Test the System**: Run `python test_logging.py`
2. **Start Your App**: `python app.py`
3. **View Logs**: Visit `/logs` in your browser
4. **Monitor Operations**: Watch logs as you use the application
5. **Customize**: Adjust log levels and formats as needed

---

**Need Help?** Check the logs first! They should give you detailed information about what's happening in your application.

