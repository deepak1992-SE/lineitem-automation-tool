# pwtpid Bidder Code Targeting Feature

## Overview
Successfully added `pwtpid` targeting key support to the Line Item Automation Tool, allowing line items to target specific bidder codes in Google Ad Manager.

## Changes Made

### 1. Core Targeting Logic (`Openwrap_DFP_Setup/tasks/add_new_openwrap_partner.py`)
- Added `bidder_code` parameter to `OpenWrapTargetingKeyGen` constructor
- Added `pwtpid_key_id` and `pwtpid_value_getter` initialization
- Modified `get_dfp_targeting()` method to conditionally add pwtpid targeting when bidder_code is provided
- Maintains backward compatibility - pwtpid only added when bidder_code is specified

### 2. Flask Application (`lineitem_flask_app/app.py`)
- Added bidder_code extraction from form data
- Updated `OpenWrapTargetingKeyGen` instantiation to pass bidder_code parameter
- Added debug logging for bidder_code value

### 3. Web Interface (`lineitem_flask_app/templates/index.html`)
- Added "Bidder Code (pwtpid)" input field after OpenWrap Creative Type
- Included helpful placeholder text with examples (pubmatic, appnexus, rubicon)
- Added descriptive help text explaining the feature
- Marked as optional field

### 4. Documentation (`README.md`)
- Updated features list to include "Bidder Code Targeting"
- Added bidder code to configuration options
- Updated line item creation section to mention pwtpid targeting

### 5. File Synchronization
- Updated both root and lineitem_flask_app copies of the Openwrap_DFP_Setup files
- Ran copy script to ensure consistency

## Technical Details

### Targeting Structure
When a bidder code is provided, line items now include four targeting criteria:
1. `pwtecp` - Price bucket targeting
2. `pwtplt` - Platform/creative type targeting  
3. `pwtbst` - Always set to "1"
4. `pwtpid` - Bidder code targeting (NEW)

### Example Targeting Output
```json
{
  "logicalOperator": "AND",
  "children": [
    {
      "xsi_type": "CustomCriteria",
      "keyId": 12345,
      "valueIds": [1001, 1002, 1003],
      "operator": "IS"
    },
    {
      "xsi_type": "CustomCriteria", 
      "keyId": 12346,
      "valueIds": [2001],
      "operator": "IS"
    },
    {
      "xsi_type": "CustomCriteria",
      "keyId": 12347, 
      "valueIds": [3001],
      "operator": "IS"
    },
    {
      "xsi_type": "CustomCriteria",
      "keyId": 12348,
      "valueIds": [4001],
      "operator": "IS"
    }
  ]
}
```

## Usage

### Web Interface
1. Navigate to the line item creation form
2. Fill in required fields (order name, email, advertiser, etc.)
3. Optionally enter a bidder code in the "Bidder Code (pwtpid)" field
4. Submit the form to create line items with bidder targeting

### Supported Bidder Codes
Common examples include:
- `pubmatic`
- `appnexus` 
- `rubicon`
- `amazon`
- `criteo`
- Any custom bidder identifier

## Backward Compatibility
- Existing functionality remains unchanged
- When no bidder code is provided, line items are created with the original 3 targeting criteria
- No breaking changes to existing API or configuration

## Testing
- Created comprehensive tests to verify pwtpid logic
- Tested both scenarios: with and without bidder code
- Verified Flask app integration
- All tests pass successfully

## Deployment
- Changes committed to main branch
- Ready for deployment to Render.com
- No additional configuration required

## Benefits
1. **Granular Control**: Target specific demand partners
2. **Improved Performance**: Reduce unnecessary bid requests
3. **Better Monetization**: Optimize for preferred bidders
4. **Flexible Targeting**: Can be combined with existing price and platform targeting
5. **Easy to Use**: Simple optional field in web interface

## Next Steps
The feature is now ready for production use. Users can immediately start creating line items with bidder-specific targeting by entering a bidder code in the web form.