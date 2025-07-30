import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Check if we're on Render and use environment variable
print(f"DEBUG: RENDER environment variable: {os.environ.get('RENDER')}")
print(f"DEBUG: GOOGLE_SERVICE_ACCOUNT_JSON exists: {bool(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'))}")

if os.environ.get('RENDER'):
    print("DEBUG: Running on Render, setting up environment-based configuration")
    # On Render, create googleads.yaml from environment variable
    import tempfile
    yaml_content = os.environ.get('GOOGLEADS_YAML_CONTENT')
    if yaml_content:
        print("DEBUG: Using GOOGLEADS_YAML_CONTENT")
        temp_dir = tempfile.gettempdir()
        yaml_path = os.path.join(temp_dir, 'googleads.yaml')
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        GOOGLEADS_YAML_FILE = yaml_path
        print(f"DEBUG: Created googleads.yaml at: {yaml_path}")
    else:
        # Fallback: create googleads.yaml with embedded service account
        service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if service_account_json and service_account_json != 'REPLACE_WITH_YOUR_ACTUAL_SERVICE_ACCOUNT_JSON':
            print("DEBUG: Using GOOGLE_SERVICE_ACCOUNT_JSON")
            temp_dir = tempfile.gettempdir()
            yaml_path = os.path.join(temp_dir, 'googleads.yaml')
            yaml_content = f"""ad_manager:
  application_name: API-Access
  network_code: '15671365'
  service_account_json: |
{chr(10).join('    ' + line for line in service_account_json.split(chr(10)))}"""
            with open(yaml_path, 'w') as f:
                f.write(yaml_content)
            GOOGLEADS_YAML_FILE = yaml_path
            print(f"DEBUG: Created googleads.yaml at: {yaml_path}")
        else:
            print("DEBUG: Using fallback local googleads.yaml")
            GOOGLEADS_YAML_FILE = os.path.join(ROOT_DIR, 'googleads.yaml')
else:
    print("DEBUG: Running locally, using local googleads.yaml")
    # Local development
    GOOGLEADS_YAML_FILE = os.path.join(ROOT_DIR, 'googleads.yaml')

print(f"DEBUG: Final GOOGLEADS_YAML_FILE path: {GOOGLEADS_YAML_FILE}")

#########################################################################
# DFP SETTINGS
#########################################################################

# A string describing the order.
# For ADPOD setup, separate order wil be created for lineitems of each slot.
# Each slot will have multiple orders if linitems count per slot exceeds 450(order limit).
# Ex:  DFP_ORDER_NAME = 'test_order_name' then order name will s1_1_test_order_name,  s2_1_test_order_name for 1st and 2nd slot of adpod
DFP_ORDER_NAME = 'PubMatic_Openwrap_minutelySB_0.1_1'

# The email of the DFP user who will be the trafficker for
# the created order
DFP_USER_EMAIL_ADDRESS = 'deepakkumar225610@gmail.com'

# The exact name of the DFP advertiser for the created order
# Set 'PubMatic' for openwrap Line items
DFP_ADVERTISER_NAME = 'PubMatic'

# Advertiser type.  Can be either "ADVERTISER" or "AD_NETWORK".  Controls
#   what type advertisers are looked up and created with.
#   Defaults to "ADVERTISER"
#  This option is only for openwrap
DFP_ADVERTISER_TYPE = "ADVERTISER"

# Lineitem type. Can be either "NETWORK", "HOUSE", "PRICE_PRIORITY" or "SPONSORSHIP"
# This option is only for openwrap
DFP_LINEITEM_TYPE = "PRICE_PRIORITY"

# Names of placements the line items should target.
# For Openwrap Leave empty for Run of Network (requires Network permission)
DFP_TARGETED_PLACEMENT_NAMES = []

# Names of ad units the line items should target.
# This option is only for prebid
# DFP_TARGETED_AD_UNIT_NAMES = "IN_ios"

# Sizes of placements. These are used to set line item and creative sizes.
# In case of  OPENWRAP_SETUP_TYPE = "ADPOD" only one size object is permitted, which will be applicable to all the creatives and line items for all the slots of Adpod.
DFP_PLACEMENT_SIZES = [
    {"width": "728", "height": "90"},
    {"width": "300", "height": "250"},
    {"width": "336", "height": "280"},
    {"width": "320", "height": "50"},
    {"width": "300", "height": "600"},
    {"width": "970", "height": "90"},
    {"width": "234", "height": "60"},
    {"width": "160", "height": "600"},
    {"width": "120", "height": "600"},
    {"width": "468", "height": "60"}

]

# Whether we should create the advertiser in DFP if it does not exist.
# If False, the program will exit rather than create an advertiser.
DFP_CREATE_ADVERTISER_IF_DOES_NOT_EXIST = True

# If settings.DFP_ORDER_NAME is the same as an existing order, add the created
# line items to that order. If False, the program will exit rather than
# modify an existing order.
DFP_USE_EXISTING_ORDER_IF_EXISTS = True

# Optional
# Each line item should have at least as many creatives as the number of
# ad units you serve on a single page because DFP specifies:
#   "Each of a line item's assigned creatives can only serve once per page,
#    so if you want the same creative to appear more than once per page,
#    copy the creative to associate multiple instances of the same creative."
# https://support.google.com/dfp_sb/answer/82245?hl=en
#
# This will default to the number of placements specified in
# `DFP_TARGETED_PLACEMENT_NAMES`.
DFP_NUM_CREATIVES_PER_LINE_ITEM = 3

# Optional
# The currency to use in DFP when setting line item CPMs. Defaults to 'USD'.
DFP_CURRENCY_CODE = 'USD'

# Optional
# Whether to set the "Same Advertiser Exception" on line items.  Defaults to false
# Currently only works for OpenWrap
# DFP_SAME_ADV_EXCEPTION = True

# Optional
# Device Category Targeting
#    Valid Values: 'Connected TV', 'Desktop', 'Feature Phone', 'Set Top Box', 'Smartphone', 'Tablet'}
#    Defaults to no device category targeting
#    Currently supported for OpenWrap Only
#    Not applicable for "IN_APP", "IN_APP_VIDEO", "IN_APP_NATIVE" and "JWPLAYER"
# DFP_DEVICE_CATEGORIES = ['Desktop']

# Optional
# DFP Roadblock Type
#    Valid Values: 'ONE_OR_MORE', 'AS_MANY_AS_POSSIBLE'
#    Defaults to 'ONE_OR_MORE'
#    Currently supported for OpenWrap Only
# DFP_ROADBLOCK_TYPE = 'AS_MANY_AS_POSSIBLE'

# Optional
# The prefix you want to add in line item's name.
# This option is for openwrap only
# LINE_ITEM_PREFIX = 'test_li'


#########################################################################
# PREBID/OPENWRAP SETTINGS
#########################################################################

# OpenWrap: you can specify an array to target multiple bidders with one line item
# not applicable for JWPLAYER, IN_APP, IN_APP_VIDEO, IN_APP_NATIVE
PREBID_BIDDER_CODE = None

# Prebid line item generator only accepts a single value
# PREBID_BIDDER_CODE = None

# Price buckets. This should match your Prebid settings for the partner. See:
# http://prebid.org/dev-docs/publisher-api-reference.html#module_pbjs.setPriceGranularity
# FIXME: this should be an array of buckets. See:
# https://github.com/prebid/Prebid.js/blob/8fed3d7aaa814e67ca3efc103d7d306cab8c692c/src/cpmBucketManager.js


# OpenWrap: Buckets are specified in a CSV file
OPENWRAP_BUCKET_CSV = 'LineItem.csv'

# Optional
# OpenWrap: Set custom line item targeting values
# Not applicable for "IN_APP", "IN_APP_VIDEO", "IN_APP_NATIVE" and "JWPLAYER"
# OPENWRAP_CUSTOM_TARGETING = [
#     ("hb_bidder", "IS", ("groupm")),
# ("hb_bidder_groupm", "IS", ("groupm")),
# ("hb_deal", "IS", ("GM")),
# ("hb_deal_groupm", "IS", ("GM")),
# ]
PREBID_PRICE_BUCKETS = {
    'precision': 2,
    'min': 8,
    'max': 20,
    'increment': 0.50,
}

# OpenWrap Creative Type
#  One of "WEB", "WEB_SAFEFRAME", "AMP", "IN_APP", "IN_APP_VIDEO", "IN_APP_NATIVE", "NATIVE", "VIDEO", "JWPLAYER", "ADPOD"
#  Defaults to WEB
#OPENWRAP_SETUP_TYPE = "IN_APP_NATIVE"

# OpenWrap Use 1x1 Creative
#  If true, will create creatives with 1x1 and size overrides
#    to the sizes configured
#  Defaults to False
# Not applicable for native, since native creative is always created with 1x1 size
# Not applicable for ADPOD
#OPENWRAP_USE_1x1_CREATIVE = True

# Creative Template
# Mandatory for Native creative type
# you can specify an array for multiple creative templates
#OPENWRAP_CREATIVE_TEMPLATE =['Native-OW-Web']

# option to set user-defined variable for NATIVE creative (used only for setup_type = NATIVE or IN_APP_NATIVE)
#OPENWRAP_NATIVE_CREATIVE_USER_DEFINED_VAR = 'pubmatic-ow-signal:%%PATTERN:pwtsid%%'

# Optional
# Openwrap currency conversion
# This option if set, will convert rate to network's currency,
# Like the existing tool, default value is True for all platforms
# and you can set it to false for WEB, WEB_SAFEFRAME, NATIVE, IN_APP, IN_APP_VIDEO and IN_APP_NATIVE only
CURRENCY_EXCHANGE = False

# Optional
# Target currency for currency exchange conversion
# This is the currency to convert to when CURRENCY_EXCHANGE is enabled
TARGET_CURRENCY = 'INR'

# Optional
# OPENWRAP VIDEO_LENGTHS
# This parameter is to set the duration of video ads creatives in seconds.
# Ex VIDEO_LENGTHS = [10,15] will create 2 creatives with durations 10 and 15 seconds per ad slot.
# Use this when OPENWRAP_SETUP_TYPE = "ADPOD"
# This parameter will be used to set creative level targeting. ex s1_pwtdur = 10
# Represents the video length parameter on UI.
VIDEO_LENGTHS = []

# Optional
# OpenWrap ADPOD_SLOTS
# This option is to set the slot in a single ADPOD.
# Use this when OPENWRAP_SETUP_TYPE = "ADPOD"
# ex ADPOD_SLOTS = [1,2,3], will create 1st, 2nd and 3rd slot of adpod
# ex ADPOD_SLOTS = [4,5], will create 4th and 5th slot of adpod
# Slot numbers should be in incremental order.
ADPOD_SLOTS = []

# ENABLE_DEAL_LINEITEM
# THis option is only for Adpod setup
# Set ENABLE_DEAL_LINEITEM = True for creating deal line item
# Defaults to False
ENABLE_DEAL_LINEITEM = False

# DEAL_CONFIG_TYPE identifies the type of DEAL_CONFIG setting.
# Set to DEALTIER when creating deal lineitem with dealtier targeting
# Set to DEALID when creating deal lineitem with dealid targeting
DEAL_CONFIG_TYPE = None

# DEAL_CONFIG - configuration for creating deal lineitem with dealtier or dealid targeting
# THis option is only for Adpod setup
# Set DFP_LINEITEM_TYPE = "SPONSORSHIP" and ENABLE_DEAL_LINEITEM = True
# DEAL_CONFIG_TYPE =  to DEALID or DEALTIER
#
# DEALID config:
# Provide price and dealids for each bidder
# Number of LineItem created = len(dealids) for each bidder
# LineItem will be created with pwtdid(dealid)targeting with pwtdid value as dealids[index] for each bidder
# Example: DEAL_CONFIG = {"pubmatic":{"price":10,"dealids":["PubDeal1"]}}
#
# DEALTIER config:
# Provide price, dealtier prefix and dealpriority values
# Number of LineItem created = len(prefix)*len(mindealtier) for each bidder
# LineItem wil be created with pwtdt(dealtier)targeting with pwtdt value as prefix[index] + mindealtier[index] for each bidder
# Example: DEAL_CONFIG = {"pubmatic":{"price":10,"prefix":["abc"],"dealpriority":[5]}}
DEAL_CONFIG = None

# VIDEO_POSITION_TYPE - video position to target
# Valid values -  "PREROLL", "MIDROLL", "POSTROLL"
# This is a optional setting and is applicable for video and adpod setup
# For adpod setup each slot lineitem will have same video position targeting
VIDEO_POSITION_TYPE = None

# Optional parameter to set creative cache url for adpod setup
# Defaults to ow.pubmatic.com
# ADPOD_CREATIVE_CACHE_URL = "test.com"

#########################################################################

# Try importing local settings, which will take precedence.
try:
    from local_settings import *
except ImportError:
    pass
