import os
import tempfile

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

def setup_googleads_for_render():
    """Setup Google Ad Manager credentials for Render deployment"""
    if os.environ.get('RENDER'):
        try:
            googleads_path = create_googleads_yaml_from_env()
            os.environ['GOOGLEADS_YAML_FILE'] = googleads_path
            print(f"✅ Google Ad Manager credentials configured from environment variables")
            return True
        except Exception as e:
            print(f"❌ Error setting up Google Ad Manager credentials: {e}")
            return False
    return True  # Not on Render, use local file 