from googleads import ad_manager
from Openwrap_DFP_Setup.dfp.client import get_client


def get_order_id_by_name(order_name):
    client = get_client()
    order_service = client.GetService('OrderService', version='v202502')
    query = f"WHERE name = '{order_name}'"
    response = order_service.getOrdersByStatement({'query': query})
    # Handle API response object properly
    if hasattr(response, 'results') and response.results and len(response.results) > 0:
        return response.results[0].id
    return None

def create_order(order_name, advertiser_name, trafficker_email):
    from Openwrap_DFP_Setup.dfp.get_advertisers import get_advertiser_id_by_name
    
    client = get_client()
    user_service = client.GetService('UserService', version='v202502')
    order_service = client.GetService('OrderService', version='v202502')

    # Get trafficker ID
    users = user_service.getUsersByStatement({'query': f"WHERE email = '{trafficker_email}'"})
    # Handle API response object properly - check if results exist and have content
    if not hasattr(users, 'results') or not users.results or len(users.results) == 0:
        raise Exception(f"No user found with email: {trafficker_email}")
    trafficker_id = users.results[0].id

    # Get advertiser ID using the proper function that handles creation if needed
    try:
        advertiser_id = get_advertiser_id_by_name(advertiser_name)
    except Exception as e:
        raise Exception(f"Failed to get/create advertiser '{advertiser_name}': {str(e)}")

    order = {
        'name': order_name,
        'advertiserId': advertiser_id,
        'traffickerId': trafficker_id
    }
    created = order_service.createOrders([order])
    return created[0].id
