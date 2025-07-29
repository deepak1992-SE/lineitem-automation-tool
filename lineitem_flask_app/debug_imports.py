#!/usr/bin/env python3
"""
Debug script to test import paths
"""
import os
import sys

print("=== Debug Import Paths ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"sys.path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

print("\n=== Testing Module Imports ===")

# Test 1: Try to import the module
try:
    from Openwrap_DFP_Setup.dfp.create_line_items import create_line_item_config, create_line_items
    print("✅ SUCCESS: Openwrap_DFP_Setup.dfp.create_line_items imported successfully")
except ImportError as e:
    print(f"❌ FAILED: {e}")

# Test 2: Check if the directory exists
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
openwrap_dir = os.path.join(parent_dir, 'Openwrap_DFP_Setup')
dfp_dir = os.path.join(openwrap_dir, 'dfp')

print(f"\n=== Directory Check ===")
print(f"Current directory: {current_dir}")
print(f"Parent directory: {parent_dir}")
print(f"Openwrap_DFP_Setup directory: {openwrap_dir}")
print(f"DFP directory: {dfp_dir}")

print(f"Parent dir exists: {os.path.exists(parent_dir)}")
print(f"Openwrap_DFP_Setup exists: {os.path.exists(openwrap_dir)}")
print(f"DFP dir exists: {os.path.exists(dfp_dir)}")

if os.path.exists(dfp_dir):
    print(f"DFP dir contents: {os.listdir(dfp_dir)}")

print("\n=== End Debug ===") 