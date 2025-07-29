import logging
from googleads import ad_manager
from Openwrap_DFP_Setup.dfp.client import get_client

logger = logging.getLogger(__name__)

def create_line_items(line_items):
    dfp_client = get_client()
    line_item_service = dfp_client.GetService('LineItemService', version='v202502')
    created_items = line_item_service.createLineItems(line_items)
    return [item['id'] for item in created_items]

def create_line_item_config(name, order_id, placement_ids, ad_unit_ids, cpm_micro_amount, sizes,
                             key_gen_obj=None, lineitem_type='PRICE_PRIORITY', currency_code='USD',
                             setup_type=None, creative_template_ids=None, same_adv_exception=False,
                             device_categories=None, device_capabilities=None,
                             roadblock_type='ONE_OR_MORE', durations=None, slot=None, video_position_type=None,
                             custom_targeting=None):

    if creative_template_ids is None:
        creative_template_ids = []
    if durations is None:
        durations = []
    if sizes is None:
        sizes = []
    if placement_ids is None:
        placement_ids = []
    if ad_unit_ids is None:
        ad_unit_ids = []

    creative_placeholders = []
    if setup_type in ('NATIVE', 'IN_APP_NATIVE'):
        for template_id in creative_template_ids:
            creative_placeholders.append({
                'size': {'width': 1, 'height': 1},
                'creativeTemplateId': template_id,
                'creativeSizeType': 'NATIVE'
            })
    elif setup_type == 'ADPOD':
        for duration in durations:
            creative_placeholders.append({
                'size': sizes[0],
                'targetingName': f"{slot}_{duration}second_ad"
            })
    else:
        for size in sizes:
            creative_placeholders.append({'size': size})

    # Get custom targeting
    if custom_targeting is not None:
        top_set = custom_targeting
    elif key_gen_obj is not None:
        top_set = key_gen_obj.get_dfp_targeting()
    else:
        top_set = None

    crv_targeting = None
    if setup_type == 'ADPOD':
        crv_targeting = [{
            'name': f"{slot}_{d}second_ad",
            'targeting': {
                'customTargeting': key_gen_obj.get_creative_targeting(d),
            }
        } for d in durations]

    config = {
        'name': name,
        'orderId': order_id,
        'targeting': {
            'inventoryTargeting': {},
            'geoTargeting': {'excludedLocations': []},
        },
        'startDateTimeType': 'IMMEDIATELY',
        'unlimitedEndDateTime': True,
        'lineItemType': lineitem_type,
        'costType': 'CPM',
        'costPerUnit': {'currencyCode': currency_code, 'microAmount': cpm_micro_amount},
        'valueCostPerUnit': {'currencyCode': currency_code, 'microAmount': cpm_micro_amount},
        'roadblockingType': roadblock_type,
        'creativeRotationType': 'EVEN',
        'primaryGoal': {'goalType': 'NONE'},
        'creativePlaceholders': creative_placeholders,
        'disableSameAdvertiserCompetitiveExclusion': same_adv_exception,
        'creativeTargetings': crv_targeting
    }

    # Only add customTargeting if it is not None, not empty, and not invalid
    if top_set and not is_invalid_custom_targeting(top_set):
        config['targeting']['customTargeting'] = top_set

    if lineitem_type in ('NETWORK', 'HOUSE'):
        config['primaryGoal'] = {'goalType': 'DAILY', 'units': 100}

    if lineitem_type == 'SPONSORSHIP':
        config['primaryGoal'] = {'unitType': 'IMPRESSIONS', 'goalType': 'DAILY', 'units': 100}
        config['skipInventoryCheck'] = True
        config['allowOverbook'] = True

    if device_categories:
        config['targeting']['technologyTargeting'] = {
            'deviceCategoryTargeting': {'targetedDeviceCategories': [{'id': str(dc)} for dc in device_categories]}
        }

    if device_capabilities:
        config['targeting']['technologyTargeting'] = {
            'deviceCapabilityTargeting': {'targetedDeviceCapabilities': [{'id': str(dc)} for dc in device_capabilities]}
        }

    if placement_ids:
        config['targeting']['inventoryTargeting']['targetedPlacementIds'] = placement_ids

    if ad_unit_ids:
        config['targeting']['inventoryTargeting']['targetedAdUnits'] = [{'adUnitId': ad_id} for ad_id in ad_unit_ids]

    if setup_type in ('VIDEO', 'JWPLAYER', 'IN_APP_VIDEO', 'ADPOD'):
        config['environmentType'] = 'VIDEO_PLAYER'
        config['videoMaxDuration'] = 15000 if setup_type == 'IN_APP_VIDEO' else 60000
        platforms = ['MOBILE_APP', 'VIDEO_PLAYER'] if setup_type == 'IN_APP_VIDEO' else ['VIDEO_PLAYER']
        config['targeting']['requestPlatformTargeting'] = {'targetedRequestPlatforms': platforms}

    if setup_type in ('VIDEO', 'ADPOD') and video_position_type:
        config['targeting']['videoPositionTargeting'] = {
            'targetedPositions': [{'videoPosition': {'positionType': video_position_type}}]
        }

    return config

def is_invalid_custom_targeting(top_set):
    # Check for placeholder IDs (123456 for keyId, 1 for valueIds)
    if not top_set:
        return True
    children = top_set.get('children', [])
    # children can be a dict or a list
    if isinstance(children, dict):
        children = [children]
    for child in children:
        if str(child.get('keyId')) == '123456' or str(child.get('valueIds')) == '1':
            return True
    return False
