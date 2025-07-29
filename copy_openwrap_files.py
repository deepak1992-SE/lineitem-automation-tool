#!/usr/bin/env python3
"""
Script to copy Openwrap_DFP_Setup files directly into the main repository
to avoid Git submodule issues on Render.
"""
import os
import shutil
import sys

def copy_openwrap_files():
    """Copy Openwrap_DFP_Setup files to avoid Git submodule issues"""
    
    # Source and destination paths
    source_dir = "lineitem_flask_app/Openwrap_DFP_Setup"
    dest_dir = "Openwrap_DFP_Setup"
    
    # Files and directories to copy
    items_to_copy = [
        "dfp/",
        "tasks/",
        "settings.py",
        "update_settings.py",
        "constant.py",
        "__init__.py"
    ]
    
    print(f"Copying Openwrap_DFP_Setup files from {source_dir} to {dest_dir}")
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created directory: {dest_dir}")
    
    # Copy each item
    for item in items_to_copy:
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        if os.path.exists(source_path):
            if os.path.isdir(source_path):
                # Copy directory
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
                print(f"Copied directory: {item}")
            else:
                # Copy file
                shutil.copy2(source_path, dest_path)
                print(f"Copied file: {item}")
        else:
            print(f"Warning: {source_path} does not exist")
    
    print("Copy operation completed!")

if __name__ == "__main__":
    copy_openwrap_files() 