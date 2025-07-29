

import os
import sys

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

# Add parent's Openwrap_DFP_Setup directory to Python path
parent_openwrap_dir = os.path.join(parent_dir, 'Openwrap_DFP_Setup')
if parent_openwrap_dir not in sys.path:
    sys.path.insert(0, parent_openwrap_dir)

print(f"DEBUG: Current directory: {current_dir}")
print(f"DEBUG: Parent directory: {parent_dir}")
print(f"DEBUG: Openwrap_DFP_Setup in current: {os.path.exists(openwrap_dir)}")
print(f"DEBUG: Openwrap_DFP_Setup in parent: {os.path.exists(parent_openwrap_dir)}")
print(f"DEBUG: Python path: {sys.path[:3]}")

# Import the modules - try different import approaches
try:
    from Openwrap_DFP_Setup.dfp.create_line_items import create_line_item_config, create_line_items
except ImportError:
    # Try importing from the full path
    import importlib.util
    # Try multiple possible paths
    possible_paths = [
        os.path.join(current_dir, "Openwrap_DFP_Setup", "dfp", "create_line_items.py"),
        os.path.join(parent_dir, "Openwrap_DFP_Setup", "dfp", "create_line_items.py"),
        os.path.join(current_dir, "Openwrap_DFP_Setup", "dfp", "create_line_items.py")
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            print(f"DEBUG: Found create_line_items.py at: {path}")
            break
    
    if file_path is None:
        print(f"DEBUG: Could not find create_line_items.py in any of: {possible_paths}")
        raise ImportError("create_line_items.py not found")
    
    spec = importlib.util.spec_from_file_location("create_line_items", file_path)
    create_line_items_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(create_line_items_module)
    create_line_item_config = create_line_items_module.create_line_item_config
    create_line_items = create_line_items_module.create_line_items

from flask import Flask, render_template, request, redirect, flash
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

import logging
import math

# Setup Google Ad Manager credentials for Render deployment
try:
    from googleads_env import setup_googleads_for_render
    setup_googleads_for_render()
except ImportError:
    # Local development - use local googleads.yaml file
    pass

app = Flask(__name__)
app.secret_key = 'lineitem_creator_secret'

logging.basicConfig(level=logging.DEBUG)

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
    logging.warning(f"No exchange rate found for {from_currency} to {to_currency}, using 1.0")
    return 1.0

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            form = request.form

            order_name = form['order_name']
            user_email = form['user_email']
            advertiser_name = form['advertiser_name']
            network_code = form['network_code']
            lineitem_prefix = form.get('lineitem_prefix', '')
            lineitem_type = form['lineitem_type']
            setup_type = form.get('openwrap_setup_type', 'WEB')
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
            
            # Extract currency exchange settings
            currency_exchange = form.get('currency_exchange') == 'on'  # Checkbox returns 'on' when checked
            target_currency = form.get('target_currency', 'INR')  # New field for target currency, default to INR

            # Prepare price bucket ranges
            expanded_prices = []
            ranges_count = int(form.get('ranges_count', '0') or '0')
            logging.debug(f"ranges_count: {ranges_count}")
            
            # If no ranges provided, create a default range
            if ranges_count == 0:
                logging.debug("No ranges provided, creating default range")
                expanded_prices.append({
                    'start_range': '5.00',
                    'end_range': '7.00',
                    'granularity': '0.03',
                    'rate_id': '2',
                    'pwtecp_values': ['5.00', '5.01', '5.02']
                })
            else:
                for i in range(ranges_count):
                    start = float(form.get(f'start_range_{i}'))
                    end = float(form.get(f'end_range_{i}'))
                    gran = float(form.get(f'granularity_{i}'))
                    
                    # Apply currency conversion if enabled
                    if currency_exchange and target_currency != currency_code:
                        exchange_rate = get_exchange_rate(currency_code, target_currency)
                        start = start * exchange_rate
                        end = end * exchange_rate
                        if gran != -1:
                            gran = gran * exchange_rate
                    
                    if gran == -1:
                        # Catch-all: one line item for the whole range, pwtecp is all integer values in range
                        pwtecp_values = [f"{int(x)}." for x in range(int(math.ceil(start)), int(math.floor(end)) + 1)]
                        expanded_prices.append({
                            'start_range': num_to_str(start, 2),
                            'end_range': num_to_str(end, 2),
                            'granularity': '-1',
                            'rate_id': form.get(f'rate_id_{i}'),
                            'pwtecp_values': pwtecp_values,
                            'is_catch_all': True
                        })
                    else:
                        current = start
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
                                'rate_id': form.get(f'rate_id_{i}'),
                                'pwtecp_values': pwtecp_values
                            })
                            current = round(current + gran, 8)

            logging.debug(f"Expanded price_els = {expanded_prices}")

            key_gen_obj = OpenWrapTargetingKeyGen(price_els=expanded_prices, creative_type=canonical_pwtplt)

            # Ensure order exists
            order_id = get_order_id_by_name(order_name)
            if not order_id:
                order_id = create_order(order_name, advertiser_name, user_email)

            # Handle sizes
            sizes = []
            for size_str in creative_sizes_str.split(','):
                w, h = size_str.lower().split('x')
                sizes.append({'width': int(w.strip()), 'height': int(h.strip())})

            # Determine inventory targeting
            placement_ids = []
            ad_unit_ids = []
            placement_names_str = form.get('placement_names', '').strip()
            if placement_names_str:
                # User provided placement names (comma-separated)
                placement_names = [p.strip() for p in placement_names_str.split(',') if p.strip()]
                if placement_names:
                    placement_ids = get_placement_ids_by_name(placement_names)
            if not placement_ids:
                # Run of Network: target root ad unit
                ad_unit_ids = [get_root_ad_unit_id()]

            # Get all targeting sets (one per line item)
            targeting_sets = key_gen_obj.get_dfp_targeting()

            # Use target currency for line items if currency exchange is enabled
            final_currency_code = target_currency if currency_exchange else currency_code

            # Create line item configs for each price bucket
            line_items_to_create = []
            price_configs = key_gen_obj.price_els
            for idx, price in enumerate(price_configs):
                # Format price string as per default logic
                if price.get('granularity') == '-1':
                    price_str = f"{float(price['start_range']):.2f}"
                    if lineitem_prefix:
                        name = f"{lineitem_prefix}_Top Bid: HB ${price_str}+ (Catch-all {price['start_range']}-{price['end_range']})"
                    else:
                        name = f"Top Bid: HB ${price_str}+ (Catch-all {price['start_range']}-{price['end_range']})"
                    micro_amount = int(float(price['start_range']) * 1000000)
                else:
                    price_str = f"{float(price['start_range']):.2f}"
                    if lineitem_prefix:
                        name = f"{lineitem_prefix}_Top Bid: HB ${price_str}"
                    else:
                        name = f"Top Bid: HB ${price_str}"
                micro_amount = int(float(price['start_range']) * 1000000)
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

            result_ids = create_line_items(line_items_to_create)

            # --- Create creatives and associate them with line items ---
            # Get advertiser ID (needed for creatives)
            advertiser_id = None
            try:
                # Try to get advertiser ID by name
                advertiser_id = get_advertiser_id_by_name(advertiser_name)
            except ImportError:
                # Fallback: create advertiser if not found
                advertiser_id = create_advertiser(advertiser_name)['id']
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
            # Create creative configs
            creative_configs = create_duplicate_creative_configs(
                bidder_code=None,  # Not used for OpenWrap
                order_name=order_name,
                advertiser_id=advertiser_id,
                sizes=sizes,
                num_creatives=num_creatives,
                prefix=lineitem_prefix,
                creative_file=creative_file
            )
            creative_ids = create_creatives(creative_configs)
            # Associate creatives with line items
            make_licas(result_ids, creative_ids, size_overrides=sizes, setup_type=setup_type)

            # Prepare summary info
            currency_info = f" (Currency: {final_currency_code})" if currency_exchange else ""
            summary_message = f"✅ Order '{order_name}' created. Line items: {len(result_ids)}. Creatives per line item: {num_creatives}.{currency_info}"
            flash(summary_message, 'success')
            return redirect('/')

        except Exception as e:
            logging.exception("Unexpected error in form processing")
            flash(f"❌ Unexpected error: {str(e)}")
            return redirect('/')

    return render_template('index.html', form_data=None, settings=settings)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)