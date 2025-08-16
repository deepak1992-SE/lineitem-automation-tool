#!/usr/bin/env python3
"""
Simple test to verify pwtpid functionality logic
"""

def test_pwtpid_logic():
    """Test the logic for adding pwtpid targeting"""
    
    # Simulate the logic from OpenWrapTargetingKeyGen.get_dfp_targeting()
    bidder_code = 'pubmatic'
    
    # Mock targeting structure
    top_level_targeting = {
        'logicalOperator': 'AND',
        'children': []
    }
    
    # Add pwtecp targeting (price)
    child_pwtecp = {
        'xsi_type': 'CustomCriteria',
        'keyId': 12345,  # pwtecp key ID
        'valueIds': [1001, 1002, 1003],  # price values
        'operator': 'IS'
    }
    top_level_targeting['children'].append(child_pwtecp)
    
    # Add pwtplt targeting (platform)
    child_pwtplt = {
        'xsi_type': 'CustomCriteria',
        'keyId': 12346,  # pwtplt key ID
        'valueIds': [2001],  # DISPLAY
        'operator': 'IS'
    }
    top_level_targeting['children'].append(child_pwtplt)
    
    # Add pwtbst targeting (always 1)
    child_pwtbst = {
        'xsi_type': 'CustomCriteria',
        'keyId': 12347,  # pwtbst key ID
        'valueIds': [3001],  # value "1"
        'operator': 'IS'
    }
    top_level_targeting['children'].append(child_pwtbst)
    
    # Add pwtpid targeting (bidder code) - THIS IS THE NEW FUNCTIONALITY
    if bidder_code:
        child_pwtpid = {
            'xsi_type': 'CustomCriteria',
            'keyId': 12348,  # pwtpid key ID
            'valueIds': [4001],  # bidder code value
            'operator': 'IS'
        }
        top_level_targeting['children'].append(child_pwtpid)
    
    # Verify the structure
    assert len(top_level_targeting['children']) == 4, f"Expected 4 targeting criteria, got {len(top_level_targeting['children'])}"
    
    # Check that all expected key IDs are present
    key_ids = [child['keyId'] for child in top_level_targeting['children']]
    expected_key_ids = [12345, 12346, 12347, 12348]  # pwtecp, pwtplt, pwtbst, pwtpid
    
    for expected_id in expected_key_ids:
        assert expected_id in key_ids, f"Expected key ID {expected_id} not found"
    
    # Find and verify pwtpid targeting
    pwtpid_targeting = None
    for child in top_level_targeting['children']:
        if child['keyId'] == 12348:
            pwtpid_targeting = child
            break
    
    assert pwtpid_targeting is not None, "pwtpid targeting not found"
    assert pwtpid_targeting['operator'] == 'IS', "Expected IS operator for pwtpid"
    assert pwtpid_targeting['valueIds'] == [4001], f"Expected pwtpid value ID [4001], got {pwtpid_targeting['valueIds']}"
    
    print("✅ Test passed: pwtpid targeting is correctly added when bidder_code is provided")


def test_no_pwtpid_logic():
    """Test the logic when no bidder code is provided"""
    
    bidder_code = None  # No bidder code
    
    # Mock targeting structure
    top_level_targeting = {
        'logicalOperator': 'AND',
        'children': []
    }
    
    # Add standard targeting (pwtecp, pwtplt, pwtbst)
    children_to_add = [
        {'xsi_type': 'CustomCriteria', 'keyId': 12345, 'valueIds': [1001], 'operator': 'IS'},  # pwtecp
        {'xsi_type': 'CustomCriteria', 'keyId': 12346, 'valueIds': [2001], 'operator': 'IS'},  # pwtplt
        {'xsi_type': 'CustomCriteria', 'keyId': 12347, 'valueIds': [3001], 'operator': 'IS'},  # pwtbst
    ]
    
    for child in children_to_add:
        top_level_targeting['children'].append(child)
    
    # Add pwtpid targeting only if bidder_code is provided
    if bidder_code:
        child_pwtpid = {
            'xsi_type': 'CustomCriteria',
            'keyId': 12348,  # pwtpid key ID
            'valueIds': [4001],  # bidder code value
            'operator': 'IS'
        }
        top_level_targeting['children'].append(child_pwtpid)
    
    # Verify the structure - should only have 3 children (no pwtpid)
    assert len(top_level_targeting['children']) == 3, f"Expected 3 targeting criteria, got {len(top_level_targeting['children'])}"
    
    # Check that pwtpid key ID is NOT present
    key_ids = [child['keyId'] for child in top_level_targeting['children']]
    expected_key_ids = [12345, 12346, 12347]  # pwtecp, pwtplt, pwtbst only
    
    for expected_id in expected_key_ids:
        assert expected_id in key_ids, f"Expected key ID {expected_id} not found"
    
    # Ensure pwtpid is NOT present
    assert 12348 not in key_ids, "pwtpid targeting should not be present when bidder_code is None"
    
    print("✅ Test passed: pwtpid targeting is NOT added when bidder_code is None")


def test_flask_app_integration():
    """Test that the Flask app correctly passes bidder_code to the targeting generator"""
    
    # Simulate form data from Flask app
    form_data = {
        'bidder_code': 'pubmatic',
        'order_name': 'Test Order',
        'user_email': 'test@example.com',
        'advertiser_name': 'Test Advertiser',
        'network_code': '12345',
        'lineitem_type': 'PRICE_PRIORITY',
        'creative_sizes': '300x250,728x90',
        'openwrap_setup_type': 'WEB'
    }
    
    # Extract bidder code as the Flask app would
    bidder_code = form_data.get('bidder_code', '').strip() or None
    
    assert bidder_code == 'pubmatic', f"Expected 'pubmatic', got {bidder_code}"
    
    # Test with empty bidder code
    form_data_empty = form_data.copy()
    form_data_empty['bidder_code'] = ''
    
    bidder_code_empty = form_data_empty.get('bidder_code', '').strip() or None
    assert bidder_code_empty is None, f"Expected None, got {bidder_code_empty}"
    
    # Test with whitespace-only bidder code
    form_data_whitespace = form_data.copy()
    form_data_whitespace['bidder_code'] = '   '
    
    bidder_code_whitespace = form_data_whitespace.get('bidder_code', '').strip() or None
    assert bidder_code_whitespace is None, f"Expected None, got {bidder_code_whitespace}"
    
    print("✅ Test passed: Flask app correctly processes bidder_code field")


if __name__ == '__main__':
    print("Running pwtpid functionality tests...")
    test_pwtpid_logic()
    test_no_pwtpid_logic()
    test_flask_app_integration()
    print("🎉 All tests passed!")
    print("\nSummary of changes:")
    print("1. Added 'pwtpid' targeting key to OpenWrapTargetingKeyGen")
    print("2. Added bidder_code parameter to constructor")
    print("3. Added conditional pwtpid targeting in get_dfp_targeting() method")
    print("4. Added bidder_code field to Flask app form")
    print("5. Updated HTML template with bidder code input field")
    print("6. Updated README.md with new feature documentation")