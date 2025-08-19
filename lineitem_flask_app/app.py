

import os
import sys
import logging
import logging.handlers
from datetime import datetime
import traceback

# Add multiple possible paths for Openwrap_DFP_Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add current directory to Python path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add parent directory to Python path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Add Openwrap_DFP_Setup directory to Python path
openwrap_dir = os.path.join(current_dir, 'Openwrap_DFP_Setup')
if openwrap_dir not in sys.path:
    sys.path.insert(0, openwrap_dir)

# Add root Openwrap_DFP_Setup directory to Python path (copied files)
root_openwrap_dir = os.path.join(parent_dir, 'Openwrap_DFP_Setup')
if root_openwrap_dir not in sys.path:
    sys.path.insert(0, root_openwrap_dir)

# Create logs directory if it doesn't exist
logs_dir = os.path.join(current_dir, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Configure comprehensive logging
def setup_logging():
    """Setup comprehensive logging configuration"""
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler (INFO level and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs (DEBUG level and above)
    all_logs_file = os.path.join(logs_dir, 'all.log')
    file_handler = logging.handlers.RotatingFileHandler(
        all_logs_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler (ERROR level and above)
    error_logs_file = os.path.join(logs_dir, 'errors.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_logs_file, maxBytes=10*1024*1024, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Flask app specific logger
    app_logger = logging.getLogger('lineitem_app')
    app_logger.setLevel(logging.DEBUG)
    
    return app_logger

# Setup logging
logger = setup_logging()

print(f"DEBUG: Current directory: {current_dir}")
print(f"DEBUG: Parent directory: {parent_dir}")
print(f"DEBUG: Openwrap_DFP_Setup in current: {os.path.exists(openwrap_dir)}")
print(f"DEBUG: Openwrap_DFP_Setup in root: {os.path.exists(root_openwrap_dir)}")
print(f"DEBUG: Python path: {sys.path[:3]}")

# Import the modules - try different import approaches
try:
    from Openwrap_DFP_Setup.dfp.create_line_items import create_line_item_config, create_line_items
except ImportError:
    # Try importing from the full path
    import importlib.util
    # Try multiple possible paths
    possible_paths = [
        os.path.join(parent_dir, "Openwrap_DFP_Setup", "dfp", "create_line_items.py"),  # Root level (copied files)
        os.path.join(current_dir, "Openwrap_DFP_Setup", "dfp", "create_line_items.py"),  # Current directory
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            logger.info(f"Found create_line_items.py at: {path}")
            break
    
    if file_path is None:
        logger.error(f"Could not find create_line_items.py in any of: {possible_paths}")
        # Let's see what's actually in the Openwrap_DFP_Setup directory
        openwrap_dir = os.path.join(current_dir, "Openwrap_DFP_Setup")
        if os.path.exists(openwrap_dir):
            logger.info(f"Contents of {openwrap_dir}:")
            for root, dirs, files in os.walk(openwrap_dir):
                level = root.replace(openwrap_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                logger.info(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    logger.info(f"{subindent}{file}")
        raise ImportError("create_line_items.py not found")
    
    spec = importlib.util.spec_from_file_location("create_line_items", file_path)
    create_line_items_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(create_line_items_module)
    create_line_item_config = create_line_items_module.create_line_item_config
    create_line_items = create_line_items_module.create_line_items

from flask import Flask, render_template, request, redirect, flash, jsonify
# Import all required modules
from Openwrap_DFP_Setup.dfp.create_orders import get_order_id_by_name, create_order
from Openwrap_DFP_Setup.dfp.get_root_ad_unit_id import get_root_ad_unit_id
from Openwrap_DFP_Setup.tasks.add_new_openwrap_partner import OpenWrapTargetingKeyGen
from Openwrap_DFP_Setup import settings
from Openwrap_DFP_Setup.dfp.create_creatives import create_duplicate_creative_configs, create_creatives
from Openwrap_DFP_Setup.dfp.associate_line_items_and_creatives import make_licas
from Openwrap_DFP_Setup.dfp.get_advertisers import create_advertiser
from Openwrap_DFP_Setup.dfp.get_advertisers import get_advertiser_id_by_name
from Openwrap_DFP_Setup.dfp.get_placements import get_placement_ids_by_name
from Openwrap_DFP_Setup.tasks.price_utils import num_to_str

import math

# Setup Google Ad Manager credentials for Render deployment
logger.info("Starting Google Ads setup - VERSION 2")
logger.info(f"RENDER env var: {os.environ.get('RENDER')}")
logger.info(f"GOOGLE_SERVICE_ACCOUNT_JSON exists: {bool(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'))}")
logger.info(f"GOOGLEADS_YAML_CONTENT exists: {bool(os.environ.get('GOOGLEADS_YAML_CONTENT'))}")
logger.info(f"Current working directory: {os.getcwd()}")

try:
    from googleads_env import setup_googleads_for_render
    logger.info("Imported googleads_env successfully")
    result = setup_googleads_for_render()
    logger.info(f"setup_googleads_for_render returned: {result}")
except ImportError as e:
    logger.warning(f"ImportError: {e}")
    # Local development - use local googleads.yaml file
    pass
except Exception as e:
    logger.error(f"Exception in setup_googleads_for_render: {e}")

app = Flask(__name__)
app.secret_key = 'lineitem_creator_secret'

def get_exchange_rate(from_currency, to_currency):
    """
    Get exchange rate between currencies.
    This is a simplified implementation - in production, you'd want to use a real exchange rate API.
    """
    # Simplified exchange rates (you should replace this with a real API)
    exchange_rates = {
        'USD': {
            'INR': 83.0,   # 1 USD = 83 INR (approximate)
            'EUR': 0.92,   # 1 USD = 0.92 EUR
            'GBP': 0.79,   # 1 USD = 0.79 GBP
            'JPY': 150.0,  # 1 USD = 150 JPY (approximate)
        },
        'INR': {
            'USD': 0.012,  # 1 INR = 0.012 USD
            'EUR': 0.011,  # 1 INR = 0.011 EUR
            'GBP': 0.0095, # 1 INR = 0.0095 GBP
            'JPY': 1.81,   # 1 INR = 1.81 JPY
        },
        'EUR': {
            'USD': 1.09,   # 1 EUR = 1.09 USD
            'INR': 90.2,   # 1 EUR = 90.2 INR
            'GBP': 0.86,   # 1 EUR = 0.86 GBP
            'JPY': 163.0,  # 1 EUR = 163 JPY
        },
        'GBP': {
            'USD': 1.27,   # 1 GBP = 1.27 USD
            'INR': 105.1,  # 1 GBP = 105.1 INR
            'EUR': 1.16,   # 1 GBP = 1.16 EUR
            'JPY': 190.0,  # 1 GBP = 190 JPY
        },
        'JPY': {
            'USD': 0.0067, # 1 JPY = 0.0067 USD
            'INR': 0.55,   # 1 JPY = 0.55 INR
            'EUR': 0.0061, # 1 JPY = 0.0061 EUR
            'GBP': 0.0053, # 1 JPY = 0.0053 GBP
        }
    }
    
    if from_currency == to_currency:
        return 1.0
    
    if from_currency in exchange_rates and to_currency in exchange_rates[from_currency]:
        return exchange_rates[from_currency][to_currency]
    
    # If no direct rate found, try reverse conversion
    if to_currency in exchange_rates and from_currency in exchange_rates[to_currency]:
        return 1.0 / exchange_rates[to_currency][from_currency]
    
    # Default to 1.0 if no conversion rate found
    logger.warning(f"No exchange rate found for {from_currency} to {to_currency}, using 1.0")
    return 1.0

@app.route('/logs')
def view_logs():
    """View application logs"""
    try:
        # Get log files
        log_files = {
            'all.log': 'All Logs',
            'errors.log': 'Error Logs Only'
        }
        
        selected_file = request.args.get('file', 'all.log')
        if selected_file not in log_files:
            selected_file = 'all.log'
        
        # Read log file
        log_file_path = os.path.join(logs_dir, selected_file)
        logs_content = []
        
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as f:
                # Read last 1000 lines
                lines = f.readlines()
                logs_content = lines[-1000:] if len(lines) > 1000 else lines
        
        return render_template('logs.html', 
                             logs_content=logs_content, 
                             log_files=log_files, 
                             selected_file=selected_file)
    except Exception as e:
        logger.error(f"Error viewing logs: {e}")
        flash(f"Error viewing logs: {str(e)}", 'error')
        return redirect('/')

@app.route('/api/logs')
def get_logs():
    """API endpoint to get logs for AJAX requests"""
    try:
        selected_file = request.args.get('file', 'all.log')
        if selected_file not in ['all.log', 'errors.log']:
            selected_file = 'all.log'
        
        log_file_path = os.path.join(logs_dir, selected_file)
        logs_content = []
        
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as f:
                lines = f.readlines()
                logs_content = lines[-1000:] if len(lines) > 1000 else lines
        
        return jsonify({
            'success': True,
            'logs': logs_content,
            'file': selected_file,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting logs via API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/clear-logs')
def clear_logs():
    """Clear all log files"""
    try:
        for filename in ['all.log', 'errors.log']:
            log_file_path = os.path.join(logs_dir, filename)
            if os.path.exists(log_file_path):
                # Clear the file by opening in write mode
                with open(log_file_path, 'w') as f:
                    f.write(f"Logs cleared at {datetime.now()}\n")
        
        flash("Logs cleared successfully", 'success')
        logger.info("Logs cleared by user")
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        flash(f"Error clearing logs: {str(e)}", 'error')
    
    return redirect('/logs')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            logger.info("Processing form submission (after user confirmation)")
            form = request.form

            order_name = form['order_name']
            user_email = form['user_email']
            advertiser_name = form['advertiser_name']
            network_code = form['network_code']
            lineitem_prefix = form.get('lineitem_prefix', '')
            lineitem_type = form['lineitem_type']
            setup_type = form.get('openwrap_setup_type', 'WEB')
            
            logger.info(f"Form data - Order: {order_name}, Advertiser: {advertiser_name}, Network: {network_code}")
            logger.info(f"Form data - Line Item Type: {lineitem_type}, Setup Type: {setup_type}, Prefix: {lineitem_prefix}")
            
            # Map setup_type to canonical pwtplt value
            pwtplt_map = {
                'WEB': 'DISPLAY',
                'WEB_SAFEFRAME': 'DISPLAY',
                'IN_APP': 'IN_APP',
                'IN_APP_VIDEO': 'IN_APP',
                'AMP': 'AMP',
                'NATIVE': 'NATIVE',
                'IN_APP_NATIVE': 'NATIVE',
                'ADPOD': 'VIDEO',
                'VIDEO': 'VIDEO',
                'JWPLAYER': 'VIDEO',
            }
            canonical_pwtplt = pwtplt_map.get(setup_type, setup_type)
            creative_sizes_str = form['creative_sizes']
            currency_code = form.get('currency_code', 'USD')
            num_creatives = int(form.get('num_creatives', '1') or '1')
            
            logger.info(f"Creative sizes: {creative_sizes_str}, Currency: {currency_code}, Num creatives: {num_creatives}")
            
            # Extract currency exchange settings
            currency_exchange = form.get('currency_exchange') == 'on'  # Checkbox returns 'on' when checked
            target_currency = form.get('target_currency', 'INR')  # New field for target currency, default to INR
            
            if currency_exchange:
                logger.info(f"Currency exchange enabled: {currency_code} -> {target_currency}")

            # Prepare price bucket ranges
            expanded_prices = []
            ranges_count = int(form.get('ranges_count', '0') or '0')
            logger.debug(f"ranges_count: {ranges_count}")
            
            # If no ranges provided, create a default range
            if ranges_count == 0:
                logger.debug("No ranges provided, creating default range")
                expanded_prices.append({
                    'start_range': '5.00',
                    'end_range': '7.00',
                    'granularity': '0.03',
                    'rate_id': '2',
                    'pwtecp_values': ['5.00', '5.01', '5.02']
                })
            else:
                logger.info(f"Processing {ranges_count} price ranges")
                for i in range(ranges_count):
                    start = float(form.get(f'start_range_{i}'))
                    end = float(form.get(f'end_range_{i}'))
                    gran = float(form.get(f'granularity_{i}'))
                    rate_id = form.get(f'rate_id_{i}')
                    
                    logger.debug(f"Range {i+1}: {start} to {end}, granularity: {gran}, rate_id: {rate_id}")
                    
                    # Apply currency conversion if enabled
                    if currency_exchange and target_currency != currency_code:
                        exchange_rate = get_exchange_rate(currency_code, target_currency)
                        original_start, original_end, original_gran = start, end, gran
                        start = start * exchange_rate
                        end = end * exchange_rate
                        if gran != -1:
                            gran = gran * exchange_rate
                        logger.info(f"Applied exchange rate {exchange_rate}: {original_start}-{original_end} -> {start:.2f}-{end:.2f}")
                    
                    if gran == -1:
                        # Catch-all: one line item for the whole range, pwtecp is all integer values in range
                        pwtecp_values = [f"{int(x)}." for x in range(int(math.ceil(start)), int(math.floor(end)) + 1)]
                        expanded_prices.append({
                            'start_range': num_to_str(start, 2),
                            'end_range': num_to_str(end, 2),
                            'granularity': '-1',
                            'rate_id': rate_id,
                            'pwtecp_values': pwtecp_values,
                            'is_catch_all': True
                        })
                        logger.debug(f"Created catch-all range: {start:.2f}-{end:.2f} with {len(pwtecp_values)} pwtecp values")
                    else:
                        current = start
                        bucket_count = 0
                        while current <= end + 1e-8:  # add epsilon for float rounding
                            # For each bucket, generate all pwtecp values in the bucket
                            bucket_start = current
                            bucket_end = min(current + gran, end)
                            
                            # Generate pwtecp values for the bucket range
                            pwtecp_values = []
                            x = bucket_start
                            while x < bucket_end:  # Exclude bucket_end value to avoid overlap
                                pwtecp_values.append(f"{x:.2f}")
                                x = round(x + 0.01, 2)  # Increment by 0.01
                            
                            expanded_prices.append({
                                'start_range': num_to_str(current, 2),
                                'granularity': num_to_str(gran, 2),
                                'rate_id': rate_id,
                                'pwtecp_values': pwtecp_values
                            })
                            bucket_count += 1
                            current = round(current + gran, 8)
                        
                        logger.debug(f"Created {bucket_count} buckets for range {start:.2f}-{end:.2f}")

            # Get bidder name and code from form
            bidder_name = form.get('bidder_name', '').strip() or None
            bidder_code = form.get('bidder_code', '').strip() or None
            
            # Auto-generate names if both bidder name and code are provided
            if bidder_name and bidder_code:
                # Override form values with auto-generated ones
                original_order_name = order_name
                original_advertiser_name = advertiser_name
                original_lineitem_prefix = lineitem_prefix
                
                order_name = f'Openwrap-{bidder_name}-display'
                advertiser_name = f'Network OpenWrap {bidder_name}'
                lineitem_prefix = f'OpenWrap-{bidder_name}-display'
                
                logger.info(f"Auto-generated names for bidder '{bidder_name}':")
                logger.info(f"  Order Name: {original_order_name} -> {order_name}")
                logger.info(f"  Advertiser Name: {original_advertiser_name} -> {advertiser_name}")
                logger.info(f"  Line Item Prefix: {original_lineitem_prefix} -> {lineitem_prefix}")
            
            # Setup Google Ads client with the network code from the form
            if os.environ.get('RENDER') and network_code:
                try:
                    from googleads_env import setup_googleads_for_render
                    setup_googleads_for_render(network_code)
                    logger.debug(f"Reconfigured Google Ads client with network code: {network_code}")
                except Exception as e:
                    logger.warning(f"Failed to reconfigure Google Ads client: {e}")
            
            logger.info(f"Final configuration:")
            logger.info(f"  Expanded price buckets: {len(expanded_prices)}")
            logger.info(f"  Network code: {network_code}")
            logger.info(f"  Bidder name: {bidder_name}")
            logger.info(f"  Bidder code: {bidder_code}")
            logger.info(f"  Canonical pwtplt: {canonical_pwtplt}")

            logger.info("Creating OpenWrap targeting key generator")
            try:
                key_gen_obj = OpenWrapTargetingKeyGen(price_els=expanded_prices, creative_type=canonical_pwtplt, bidder_code=bidder_code)
                logger.info("OpenWrap targeting key generator created successfully")
            except Exception as e:
                logger.error(f"Failed to create OpenWrap targeting key generator: {e}")
                raise

            # Ensure order exists
            logger.info(f"Checking if order '{order_name}' exists")
            try:
                order_id = get_order_id_by_name(order_name)
                if not order_id:
                    logger.info(f"Creating new order '{order_name}'")
                    order_id = create_order(order_name, advertiser_name, user_email)
                    logger.info(f"Order created with ID: {order_id}")
                else:
                    logger.info(f"Using existing order with ID: {order_id}")
            except Exception as e:
                logger.error(f"Error with order creation/lookup: {e}")
                raise

            # Handle sizes
            sizes = []
            try:
                for size_str in creative_sizes_str.split(','):
                    w, h = size_str.lower().split('x')
                    sizes.append({'width': int(w.strip()), 'height': int(h.strip())})
                logger.info(f"Creative sizes: {sizes}")
            except Exception as e:
                logger.error(f"Error parsing creative sizes '{creative_sizes_str}': {e}")
                raise

            # Determine inventory targeting
            placement_ids = []
            ad_unit_ids = []
            placement_names_str = form.get('placement_names', '').strip()
            if placement_names_str:
                # User provided placement names (comma-separated)
                placement_names = [p.strip() for p in placement_names_str.split(',') if p.strip()]
                if placement_names:
                    logger.info(f"Looking up placements: {placement_names}")
                    try:
                        placement_ids = get_placement_ids_by_name(placement_names)
                        logger.info(f"Found placement IDs: {placement_ids}")
                    except Exception as e:
                        logger.error(f"Error looking up placements: {e}")
                        raise
            if not placement_ids:
                # Run of Network: target root ad unit
                logger.info("No placements specified, using Run of Network targeting")
                try:
                    ad_unit_ids = [get_root_ad_unit_id()]
                    logger.info(f"Root ad unit ID: {ad_unit_ids}")
                except Exception as e:
                    logger.error(f"Error getting root ad unit ID: {e}")
                    raise

            # Get all targeting sets (one per line item)
            logger.info("Generating DFP targeting")
            try:
                targeting_sets = key_gen_obj.get_dfp_targeting()
                logger.info(f"Generated {len(targeting_sets)} targeting sets")
            except Exception as e:
                logger.error(f"Error generating DFP targeting: {e}")
                raise

            # Use target currency for line items if currency exchange is enabled
            final_currency_code = target_currency if currency_exchange else currency_code

            # Create line item configs for each price bucket
            logger.info("Creating line item configurations")
            line_items_to_create = []
            price_configs = key_gen_obj.price_els
            for idx, price in enumerate(price_configs):
                # Format price string as per default logic
                if price.get('granularity') == '-1':
                    price_str = f"{float(price['start_range']):.2f}"
                    if lineitem_prefix:
                        name = f"{lineitem_prefix}_HB ${price_str}+ (Catch-all {price['start_range']}-{price['end_range']})"
                    else:
                        name = f"HB ${price_str}+ (Catch-all {price['start_range']}-{price['end_range']})"
                    micro_amount = int(float(price['start_range']) * 1000000)
                else:
                    price_str = f"{float(price['start_range']):.2f}"
                    if lineitem_prefix:
                        name = f"{lineitem_prefix}_HB ${price_str}"
                    else:
                        name = f"HB ${price_str}"
                micro_amount = int(float(price['start_range']) * 1000000)
                
                logger.debug(f"Creating line item config {idx+1}/{len(price_configs)}: {name}")
                logger.debug(f"  Price: ${price_str}, Micro amount: {micro_amount}, Currency: {final_currency_code}")
                
                try:
                    config = create_line_item_config(
                        name=name,
                        order_id=order_id,
                        placement_ids=placement_ids,
                        ad_unit_ids=ad_unit_ids,
                        cpm_micro_amount=micro_amount,
                        sizes=sizes,
                        key_gen_obj=None,  # We'll pass custom targeting directly
                        lineitem_type=lineitem_type,
                        currency_code=final_currency_code,
                        setup_type=setup_type,
                        custom_targeting=targeting_sets[idx]
                    )
                    line_items_to_create.append(config)
                    logger.debug(f"Line item config created successfully: {name}")
                except Exception as e:
                    logger.error(f"Error creating line item config for {name}: {e}")
                    raise

            logger.info(f"Creating {len(line_items_to_create)} line items")
            try:
                result_ids = create_line_items(line_items_to_create)
                logger.info(f"Line items created successfully: {result_ids}")
            except Exception as e:
                logger.error(f"Error creating line items: {e}")
                raise

            # --- Create creatives and associate them with line items ---
            # Get advertiser ID (needed for creatives)
            advertiser_id = None
            try:
                # Try to get advertiser ID by name
                logger.info(f"Looking up advertiser: {advertiser_name}")
                advertiser_id = get_advertiser_id_by_name(advertiser_name)
                logger.info(f"Found advertiser ID: {advertiser_id}")
            except ImportError:
                # Fallback: create advertiser if not found
                logger.info(f"Creating new advertiser: {advertiser_name}")
                try:
                    advertiser_result = create_advertiser(advertiser_name)
                    advertiser_id = advertiser_result['id']
                    logger.info(f"Advertiser created with ID: {advertiser_id}")
                except Exception as e:
                    logger.error(f"Error creating advertiser: {e}")
                    raise
            except Exception as e:
                logger.error(f"Error looking up advertiser: {e}")
                raise
            
            # Select creative snippet file based on platform
            if setup_type in ["IN_APP", "IN_APP_VIDEO", "IN_APP_NATIVE"]:
                creative_file = "creative_snippet_openwrap_in_app.html"
            elif setup_type == "AMP":
                creative_file = "creative_snippet_openwrap_amp.html"
            elif setup_type in ["VIDEO", "JWPLAYER", "ADPOD"]:
                # Use a video-specific snippet if available, else fallback
                creative_file = "creative_snippet_openwrap_sf.html"  # fallback to .html if not present
            else:
                creative_file = "creative_snippet_openwrap.html"
            
            logger.info(f"Using creative file: {creative_file}")
            
            # Create creative configs
            logger.info(f"Creating {num_creatives} creatives per line item")
            try:
                creative_configs = create_duplicate_creative_configs(
                    bidder_code=None,  # Not used for OpenWrap
                    order_name=order_name,
                    advertiser_id=advertiser_id,
                    sizes=sizes,
                    num_creatives=num_creatives,
                    prefix=lineitem_prefix,
                    creative_file=creative_file
                )
                logger.info(f"Creative configs created: {len(creative_configs)}")
            except Exception as e:
                logger.error(f"Error creating creative configs: {e}")
                raise
            
            logger.info("Creating creatives")
            try:
                creative_ids = create_creatives(creative_configs)
                logger.info(f"Creatives created successfully: {creative_ids}")
            except Exception as e:
                logger.error(f"Error creating creatives: {e}")
                raise
            
            # Associate creatives with line items
            logger.info("Associating creatives with line items")
            try:
                make_licas(result_ids, creative_ids, size_overrides=sizes, setup_type=setup_type)
                logger.info("Creative association completed")
            except Exception as e:
                logger.error(f"Error associating creatives with line items: {e}")
                raise

            # Prepare summary info
            currency_info = f" (Currency: {final_currency_code})" if currency_exchange else ""
            summary_message = f"✅ Order '{order_name}' created. Line items: {len(result_ids)}. Creatives per line item: {num_creatives}.{currency_info}"
            flash(summary_message, 'success')
            logger.info(f"Form processing completed successfully: {summary_message}")
            return redirect('/')

        except Exception as e:
            error_msg = f"Unexpected error in form processing: {str(e)}"
            logger.exception(error_msg)
            flash(f"❌ {error_msg}")
            return redirect('/')

    return render_template('index.html', form_data=None, settings=settings)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)