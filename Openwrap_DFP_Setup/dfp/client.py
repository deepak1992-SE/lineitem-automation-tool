# In: Openwrap_DFP_Setup/dfp/client.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from Openwrap_DFP_Setup import settings
from googleads import ad_manager

def get_client():
    return ad_manager.AdManagerClient.LoadFromStorage(settings.GOOGLEADS_YAML_FILE)
