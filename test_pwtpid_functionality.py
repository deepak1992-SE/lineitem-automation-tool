#!/usr/bin/env python3
"""
Simple test to verify pwtpid functionality works correctly
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the project directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'Openwrap_DFP_Setup'))

# Mock the DFP client and related functions to avoid API calls
with patch('Openwrap_DFP_Setup.tasks.dfp_utils.get_custom_targeting') as mock_get_targeting, \
     patch('Openwrap_DFP_Setup.tasks.dfp_utils.create_custom_targeting') as mock_create_targeting:
    
    # Mock the get_key_id_by_name function
    mock_get_targeting.get_key_id_by_name = MagicMock(side_effect=lambda name: {
        'pwtecp': 12345,
        'pwtplt': 12346, 
        'pwtbst': 12347,
        'pwtpid': 12348
    }.get(name))
    
    # Mock the get_targeting_by_key_name function
    mock_get_targeting.get_targeting_by_key_name = MagicMock(return_value=[])
    
    # Mock the create_targeting_key function
    mock_create_targeting.create_targeting_key = MagicMock(return_value=99999)
    
    from Openwrap_DFP_Setup.tasks.add_new_openwrap_partner import OpenWrapTargetingKeyGen

def test_pwtpid_targeting():
    """Test that pwtpid targeting is correctly added when bidder_code is provided"""
    
    # Test data
    price_els = [{
        'start_range': '5.00',
        'end_range': '5.02',
        'granularity': '0.01',
        'rate_id': '2',
        'pwtecp_values': ['5.00', '5.01', '5.02']
    }]
    
    creative_type = 'DISPLAY'
    bidder_code = 'pubmatic'
    
    # Create targeting key generator with bidder code
    key_gen = OpenWrapTargetingKeyGen(
        price_els=price_els,
        creative_type=creative_type,
        bidder_code=bidder_code
    )
    
    # Mock the key IDs and value getters to avoid DFP API calls
    key_gen.pwtecp_key_id = 12345
    key_gen.pwtplt_key_id = 12346
    key_gen.pwtbst_key_id = 12347
    key_gen.pwtpid_key_id = 12348
    
    # Mock value getters
    class MockValueGetter:
        def __init__(self, key_name):
            self.key_name = key_name
            
        def get_value_id(self, value):
            # Return mock IDs based on value
            mock_ids = {
                '5.00': 1001, '5.01': 1002, '5.02': 1003,
                'DISPLAY': 2001,
                '1': 3001,
                'pubmatic': 4001
            }
            return mock_ids.get(value, 9999)
    
    key_gen.pwtecp_value_getter = MockValueGetter('pwtecp')
    key_gen.pwtplt_value_getter = MockValueGetter('pwtplt')
    key_gen.pwtbst_value_getter = MockValueGetter('pwtbst')
    key_gen.pwtpid_value_getter = MockValueGetter('pwtpid')
    
    # Get targeting
    targeting_sets = key_gen.get_dfp_targeting()
    
    # Verify results
    assert len(targeting_sets) == 1, f"Expected 1 targeting set, got {len(targeting_sets)}"
    
    targeting = targeting_sets[0]
    assert targeting['logicalOperator'] == 'AND', "Expected AND operator"
    
    children = targeting['children']
    assert len(children) == 4, f"Expected 4 targeting criteria (pwtecp, pwtplt, pwtbst, pwtpid), got {len(children)}"
    
    # Check each targeting criterion
    key_ids_found = [child['keyId'] for child in children]
    expected_key_ids = [12345, 12346, 12347, 12348]  # pwtecp, pwtplt, pwtbst, pwtpid
    
    for expected_id in expected_key_ids:
        assert expected_id in key_ids_found, f"Expected key ID {expected_id} not found in targeting"
    
    # Find pwtpid targeting specifically
    pwtpid_targeting = None
    for child in children:
        if child['keyId'] == 12348:  # pwtpid key ID
            pwtpid_targeting = child
            break
    
    assert pwtpid_targeting is not None, "pwtpid targeting not found"
    assert pwtpid_targeting['operator'] == 'IS', "Expected IS operator for pwtpid"
    assert pwtpid_targeting['valueIds'] == [4001], f"Expected pwtpid value ID [4001], got {pwtpid_targeting['valueIds']}"
    
    print("✅ Test passed: pwtpid targeting is correctly added when bidder_code is provided")


def test_no_pwtpid_when_no_bidder_code():
    """Test that pwtpid targeting is NOT added when bidder_code is None"""
    
    # Test data
    price_els = [{
        'start_range': '5.00',
        'end_range': '5.02',
        'granularity': '0.01',
        'rate_id': '2',
        'pwtecp_values': ['5.00', '5.01', '5.02']
    }]
    
    creative_type = 'DISPLAY'
    bidder_code = None  # No bidder code
    
    # Create targeting key generator without bidder code
    key_gen = OpenWrapTargetingKeyGen(
        price_els=price_els,
        creative_type=creative_type,
        bidder_code=bidder_code
    )
    
    # Mock the key IDs and value getters
    key_gen.pwtecp_key_id = 12345
    key_gen.pwtplt_key_id = 12346
    key_gen.pwtbst_key_id = 12347
    key_gen.pwtpid_key_id = 12348
    
    # Mock value getters
    class MockValueGetter:
        def __init__(self, key_name):
            self.key_name = key_name
            
        def get_value_id(self, value):
            mock_ids = {
                '5.00': 1001, '5.01': 1002, '5.02': 1003,
                'DISPLAY': 2001,
                '1': 3001
            }
            return mock_ids.get(value, 9999)
    
    key_gen.pwtecp_value_getter = MockValueGetter('pwtecp')
    key_gen.pwtplt_value_getter = MockValueGetter('pwtplt')
    key_gen.pwtbst_value_getter = MockValueGetter('pwtbst')
    key_gen.pwtpid_value_getter = MockValueGetter('pwtpid')
    
    # Get targeting
    targeting_sets = key_gen.get_dfp_targeting()
    
    # Verify results
    assert len(targeting_sets) == 1, f"Expected 1 targeting set, got {len(targeting_sets)}"
    
    targeting = targeting_sets[0]
    children = targeting['children']
    assert len(children) == 3, f"Expected 3 targeting criteria (pwtecp, pwtplt, pwtbst), got {len(children)}"
    
    # Check that pwtpid is NOT included
    key_ids_found = [child['keyId'] for child in children]
    expected_key_ids = [12345, 12346, 12347]  # pwtecp, pwtplt, pwtbst only
    
    for expected_id in expected_key_ids:
        assert expected_id in key_ids_found, f"Expected key ID {expected_id} not found in targeting"
    
    # Ensure pwtpid is NOT present
    assert 12348 not in key_ids_found, "pwtpid targeting should not be present when bidder_code is None"
    
    print("✅ Test passed: pwtpid targeting is NOT added when bidder_code is None")


if __name__ == '__main__':
    print("Running pwtpid functionality tests...")
    test_pwtpid_targeting()
    test_no_pwtpid_when_no_bidder_code()
    print("🎉 All tests passed!")