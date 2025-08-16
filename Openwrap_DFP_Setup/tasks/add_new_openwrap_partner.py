from Openwrap_DFP_Setup.tasks.dfp_utils import DFPValueIdGetter, get_or_create_dfp_targeting_key

class OpenWrapTargetingKeyGen:
    def __init__(self, price_els=None, creative_type=None, bidder_code=None):
        self.price_els = price_els or []
        self.creative_type = creative_type or 'WEB'
        self.bidder_code = bidder_code
        # Get or create targeting keys for pwtecp, pwtplt, pwtbst, and pwtpid
        self.pwtecp_key_id = get_or_create_dfp_targeting_key('pwtecp')
        self.pwtplt_key_id = get_or_create_dfp_targeting_key('pwtplt')
        self.pwtbst_key_id = get_or_create_dfp_targeting_key('pwtbst')
        self.pwtpid_key_id = get_or_create_dfp_targeting_key('pwtpid')
        # Default value getter for granular buckets (EXACT)
        self.pwtecp_value_getter = DFPValueIdGetter('pwtecp')
        self.pwtplt_value_getter = DFPValueIdGetter('pwtplt')
        self.pwtbst_value_getter = DFPValueIdGetter('pwtbst')
        self.pwtpid_value_getter = DFPValueIdGetter('pwtpid')

    def get_dfp_targeting(self):
        print("DEBUG: self.price_els =", self.price_els)
        # Return a list of targeting sets, one per line item
        targeting_sets = []
        for p in self.price_els:
            top_level_targeting = {
                'logicalOperator': 'AND',
                'children': []
            }
            # pwtecp: price bucket value(s)
            pwtecp_values = p.get('pwtecp_values')
            is_catch_all = p.get('is_catch_all', False)
            if pwtecp_values:
                # Use PREFIX match type for catch-all (integer) buckets
                if is_catch_all:
                    pwtecp_value_getter_prefix = DFPValueIdGetter('pwtecp', match_type='PREFIX')
                    pwtecp_value_ids = [pwtecp_value_getter_prefix.get_value_id(val) for val in pwtecp_values]
                else:
                    pwtecp_value_ids = [self.pwtecp_value_getter.get_value_id(val) for val in pwtecp_values]
                child_pwtecp = {
                    'xsi_type': 'CustomCriteria',
                    'keyId': self.pwtecp_key_id,
                    'valueIds': pwtecp_value_ids,
                    'operator': 'IS'
                }
            else:
                price_value = str(p['start_range'])
                # Use PREFIX for catch-all, else EXACT
                if is_catch_all:
                    pwtecp_value_getter_prefix = DFPValueIdGetter('pwtecp', match_type='PREFIX')
                    pwtecp_value_id = pwtecp_value_getter_prefix.get_value_id(price_value)
                else:
                    pwtecp_value_id = self.pwtecp_value_getter.get_value_id(price_value)
                child_pwtecp = {
                    'xsi_type': 'CustomCriteria',
                    'keyId': self.pwtecp_key_id,
                    'valueIds': [pwtecp_value_id],
                    'operator': 'IS'
                }
            top_level_targeting['children'].append(child_pwtecp)
            # pwtplt: creative type
            pwtplt_value_id = self.pwtplt_value_getter.get_value_id(self.creative_type)
            child_pwtplt = {
                'xsi_type': 'CustomCriteria',
                'keyId': self.pwtplt_key_id,
                'valueIds': [pwtplt_value_id],
                'operator': 'IS'
            }
            top_level_targeting['children'].append(child_pwtplt)
            # pwtbst: always 1
            pwtbst_value_id = self.pwtbst_value_getter.get_value_id('1')
            child_pwtbst = {
                'xsi_type': 'CustomCriteria',
                'keyId': self.pwtbst_key_id,
                'valueIds': [pwtbst_value_id],
                'operator': 'IS'
            }
            top_level_targeting['children'].append(child_pwtbst)
            
            # pwtpid: bidder code (if provided)
            if self.bidder_code:
                pwtpid_value_id = self.pwtpid_value_getter.get_value_id(self.bidder_code)
                child_pwtpid = {
                    'xsi_type': 'CustomCriteria',
                    'keyId': self.pwtpid_key_id,
                    'valueIds': [pwtpid_value_id],
                    'operator': 'IS'
                }
                top_level_targeting['children'].append(child_pwtpid)
            
            targeting_sets.append(top_level_targeting)
        return targeting_sets
