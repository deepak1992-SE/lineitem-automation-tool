from googleads import ad_manager
from Openwrap_DFP_Setup.dfp.client import get_client


def get_order_id_by_name(order_name):
    client = get_client()
    order_service = client.GetService('OrderService', version='v202502')
    query = f"WHERE name = '{order_name}'"
    response = order_service.getOrdersByStatement({'query': query})
    if 'results' in response and len(response['results']) > 0:
        return response['results'][0]['id']
    return None

def create_order(order_name, advertiser_name, trafficker_email):
    client = get_client()
    user_service = client.GetService('UserService', version='v202502')
    order_service = client.GetService('OrderService', version='v202502')
    company_service = client.GetService('CompanyService', version='v202502')

    # Get trafficker ID
    users = user_service.getUsersByStatement({'query': f"WHERE email = '{trafficker_email}'"})
    trafficker_id = users['results'][0]['id']

    # Get advertiser ID
    companies = company_service.getCompaniesByStatement({'query': f"WHERE name = '{advertiser_name}'"})
    advertiser_id = companies['results'][0]['id']

    order = {
        'name': order_name,
        'advertiserId': advertiser_id,
        'traffickerId': trafficker_id
    }
    created = order_service.createOrders([order])
    return created[0]['id']
