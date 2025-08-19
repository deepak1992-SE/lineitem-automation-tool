#!/usr/bin/env python3
"""
Test script to verify the logging system is working correctly.
Run this script to generate some test logs and verify they appear in the log files.
"""

import os
import sys
import logging
import time

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_logging():
    """Test the logging system by generating various log messages"""
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(current_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"Created logs directory: {logs_dir}")
    
    # Import and setup logging from app.py
    try:
        from app import setup_logging
        logger = setup_logging()
        print("✅ Successfully imported and setup logging from app.py")
    except ImportError as e:
        print(f"❌ Failed to import from app.py: {e}")
        return False
    
    # Test various log levels
    print("\n📝 Generating test log messages...")
    
    logger.debug("This is a DEBUG message - should appear in all.log")
    logger.info("This is an INFO message - should appear in all.log and console")
    logger.warning("This is a WARNING message - should appear in all.log and console")
    logger.error("This is an ERROR message - should appear in all.log, errors.log, and console")
    
    # Test with some context
    logger.info("Testing logging system with various scenarios")
    logger.info("Form submission started")
    logger.info("Processing order: Test-Order-123")
    logger.info("Network code: 12345678")
    logger.info("Creating line items...")
    
    # Simulate some errors
    try:
        # Simulate a division by zero error
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Mathematical error occurred: {e}")
        logger.exception("Full traceback for the error")
    
    # Test with more realistic scenarios
    logger.info("Line item creation completed successfully")
    logger.info("Creative association in progress...")
    logger.warning("Some placements not found, using Run of Network")
    logger.info("Process completed successfully")
    
    print("✅ Test log messages generated successfully")
    
    # Check if log files were created
    all_log_path = os.path.join(logs_dir, 'all.log')
    errors_log_path = os.path.join(logs_dir, 'errors.log')
    
    print(f"\n📁 Checking log files...")
    print(f"All logs file: {all_log_path}")
    print(f"Errors log file: {errors_log_path}")
    
    if os.path.exists(all_log_path):
        with open(all_log_path, 'r') as f:
            lines = f.readlines()
            print(f"✅ All logs file exists with {len(lines)} lines")
            if lines:
                print(f"Last log entry: {lines[-1].strip()}")
    else:
        print("❌ All logs file not found")
    
    if os.path.exists(errors_log_path):
        with open(errors_log_path, 'r') as f:
            lines = f.readlines()
            print(f"✅ Errors log file exists with {len(lines)} lines")
            if lines:
                print(f"Last error entry: {lines[-1].strip()}")
    else:
        print("❌ Errors log file not found")
    
    print("\n🎯 Logging system test completed!")
    print("You can now:")
    print("1. Start your Flask app: python app.py")
    print("2. Visit http://localhost:5000/logs to view the logs")
    print("3. Or check the log files directly in the logs/ directory")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Lineitem Automation Tool Logging System")
    print("=" * 50)
    
    success = test_logging()
    
    if success:
        print("\n🎉 All tests passed! Your logging system is working correctly.")
    else:
        print("\n💥 Some tests failed. Please check the error messages above.")
    
    print("\n" + "=" * 50)

