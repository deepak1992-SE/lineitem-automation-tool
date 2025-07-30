# In: Openwrap_DFP_Setup/dfp/client.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from Openwrap_DFP_Setup import settings
from googleads import ad_manager

def get_client():
    print(f"DEBUG: client.py - Loading from: {settings.GOOGLEADS_YAML_FILE}")
    print(f"DEBUG: client.py - File exists: {os.path.exists(settings.GOOGLEADS_YAML_FILE)}")
    if os.path.exists(settings.GOOGLEADS_YAML_FILE):
        with open(settings.GOOGLEADS_YAML_FILE, 'r') as f:
            content = f.read()
            print(f"DEBUG: client.py - File content preview: {content[:200]}...")
    return ad_manager.AdManagerClient.LoadFromStorage(settings.GOOGLEADS_YAML_FILE)
