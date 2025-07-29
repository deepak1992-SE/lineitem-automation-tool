

import os
import sys

# Setup proper import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add Openwrap_DFP_Setup directory to Python path
openwrap_dir = os.path.join(current_dir, 'Openwrap_DFP_Setup')
if openwrap_dir not in sys.path:
    sys.path.insert(0, openwrap_dir)

# Try to import the modules
try:
    from Openwrap_DFP_Setup.dfp.create_line_items import create_line_item_config, create_line_items
    print("✅ SUCCESS: Openwrap_DFP_Setup modules imported")
except ImportError as e:
    print(f"❌ WARNING: Could not import Openwrap_DFP_Setup modules: {e}")
    # Create dummy functions
    def create_line_item_config(*args, **kwargs): pass
    def create_line_items(*args, **kwargs): pass

from flask import Flask, render_template, request, redirect, flash
# Import all required modules with fallback
try:
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
except ImportError as e:
    print(f"Warning: Could not import Openwrap_DFP_Setup modules: {e}")
    # Create dummy functions for testing
    def create_line_item_config(*args, **kwargs): pass
    def create_line_items(*args, **kwargs): pass
    def get_order_id_by_name(*args, **kwargs): pass
    def create_order(*args, **kwargs): pass
    def get_root_ad_unit_id(*args, **kwargs): pass
    def create_duplicate_creative_configs(*args, **kwargs): pass
    def create_creatives(*args, **kwargs): pass
    def make_licas(*args, **kwargs): pass
    def create_advertiser(*args, **kwargs): pass
    def get_advertiser_id_by_name(*args, **kwargs): pass
    def get_placement_ids_by_name(*args, **kwargs): pass
    def num_to_str(*args, **kwargs): pass
    class OpenWrapTargetingKeyGen:
        def __init__(self, price_els=None, creative_type=None):
            self.price_els = price_els or []
            self.creative_type = creative_type or 'WEB'
            print(f"DEBUG: Dummy OpenWrapTargetingKeyGen created with {len(self.price_els)} price elements")
        
        def get_dfp_targeting(self):
            print("DEBUG: self.price_els =", self.price_els)
            # Return empty targeting sets for dummy implementation
            targeting_sets = []
            for p in self.price_els:
                targeting_sets.append({
                    'logicalOperator': 'AND',
                    'children': []
                })
            return targeting_sets
    class settings: pass

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
            num_creatives = int(form.get('num_creatives', 1))
            
            # Extract currency exchange settings
            currency_exchange = form.get('currency_exchange') == 'on'  # Checkbox returns 'on' when checked
            target_currency = form.get('target_currency', 'INR')  # New field for target currency, default to INR

            # Prepare price bucket ranges
            expanded_prices = []
            ranges_count = int(form.get('ranges_count', 0))
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