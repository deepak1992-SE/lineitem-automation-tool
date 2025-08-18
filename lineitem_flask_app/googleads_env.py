import os
import tempfile

def create_googleads_yaml_from_env(network_code=None):
    """Create googleads.yaml file from environment variable with dynamic network code"""
    print("DEBUG: googleads_env.py - create_googleads_yaml_from_env called")
    
    # Get network code from parameter, environment variable, or default
    if not network_code:
        network_code = os.environ.get('NETWORK_CODE', '15671365')
    
    print(f"DEBUG: Using network code: {network_code}")
    
    # Try GOOGLE_SERVICE_ACCOUNT_JSON first (preferred method)
    service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if service_account_json and service_account_json != 'REPLACE_WITH_YOUR_ACTUAL_SERVICE_ACCOUNT_JSON':
        print("DEBUG: Using GOOGLE_SERVICE_ACCOUNT_JSON")
        temp_dir = tempfile.gettempdir()
        
        # Create temporary JSON file
        json_path = os.path.join(temp_dir, 'service_account.json')
        with open(json_path, 'w') as f:
            f.write(service_account_json)
        print(f"DEBUG: Created service account JSON at: {json_path}")
        
        # Create YAML file that references the JSON file with dynamic network code
        yaml_path = os.path.join(temp_dir, 'googleads.yaml')
        yaml_content = f"""ad_manager:
  application_name: API-Access
  network_code: '{network_code}'
  path_to_private_key_file: {json_path}"""
        
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        
        print(f"DEBUG: Created googleads.yaml from GOOGLE_SERVICE_ACCOUNT_JSON at: {yaml_path}")
        return yaml_path
    
    # Fallback to GOOGLEADS_YAML_CONTENT (replace network code if needed)
    yaml_content = os.environ.get('GOOGLEADS_YAML_CONTENT')
    if yaml_content:
        print("DEBUG: Using GOOGLEADS_YAML_CONTENT")
        
        # Replace network code in existing YAML content
        import re
        yaml_content = re.sub(r'network_code:\s*[\'"]?\d+[\'"]?', f"network_code: '{network_code}'", yaml_content)
        
        temp_dir = tempfile.gettempdir()
        yaml_path = os.path.join(temp_dir, 'googleads.yaml')
        
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        
        print(f"DEBUG: Created googleads.yaml from GOOGLEADS_YAML_CONTENT at: {yaml_path}")
        return yaml_path
    
    print("DEBUG: No environment variables found, using local file")
    raise ValueError("Neither GOOGLE_SERVICE_ACCOUNT_JSON nor GOOGLEADS_YAML_CONTENT environment variables are set")

def setup_googleads_for_render(network_code=None):
    """Setup Google Ad Manager credentials for Render deployment with dynamic network code"""
    print(f"DEBUG: googleads_env.py - setup_googleads_for_render called")
    print(f"DEBUG: RENDER environment variable: {os.environ.get('RENDER')}")
    print(f"DEBUG: GOOGLE_SERVICE_ACCOUNT_JSON exists: {bool(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'))}")
    print(f"DEBUG: GOOGLEADS_YAML_CONTENT exists: {bool(os.environ.get('GOOGLEADS_YAML_CONTENT'))}")
    print(f"DEBUG: Network code parameter: {network_code}")
    
    if os.environ.get('RENDER'):
        try:
            googleads_path = create_googleads_yaml_from_env(network_code)
            os.environ['GOOGLEADS_YAML_FILE'] = googleads_path
            print(f"✅ Google Ad Manager credentials configured from environment variables")
            print(f"DEBUG: Set GOOGLEADS_YAML_FILE to: {googleads_path}")
            return True
        except Exception as e:
            print(f"❌ Error setting up Google Ad Manager credentials: {e}")
            return False
    else:
        print("DEBUG: Not on Render, using local file")
    return True  # Not on Render, use local file 