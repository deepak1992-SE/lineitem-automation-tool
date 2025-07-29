#!/usr/bin/env python3
"""
Fix imports for Openwrap_DFP_Setup modules
"""
import os
import sys

def setup_imports():
    """Setup proper import paths for Openwrap_DFP_Setup"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add current directory to Python path
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Add Openwrap_DFP_Setup directory to Python path
    openwrap_dir = os.path.join(current_dir, 'Openwrap_DFP_Setup')
    if openwrap_dir not in sys.path:
        sys.path.insert(0, openwrap_dir)
    
    print(f"Current directory: {current_dir}")
    print(f"Openwrap_DFP_Setup directory: {openwrap_dir}")
    print(f"Python path updated")

def test_imports():
    """Test if we can import the required modules"""
    try:
        from Openwrap_DFP_Setup.dfp.create_line_items import create_line_item_config, create_line_items
        print("✅ SUCCESS: create_line_items imported")
        return True
    except ImportError as e:
        print(f"❌ FAILED: create_line_items - {e}")
        return False

if __name__ == "__main__":
    setup_imports()
    test_imports() 