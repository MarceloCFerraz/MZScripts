import requests


def get_hub_config(env, orgId, hubId):
    """
    Retrieves the configuration for a specific hub.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization ID.
        hubId (str): The ID of the hub.

    Returns:
        dict: The configuration for the hub.
    """
    url = f"http://alamo.{env}.milezero.com/alamo-war/api/hubconfig/key/orgId/{orgId}?key={hubId}&keyType=HUB_ID"

    response = requests.get(url=url, timeout=30)

    return response.json().get('config')


def get_all_hubs(env, orgId):
    """
    Retrieves all hubs within an organization.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization ID.

    Returns:
        list: A list of all hubs within the organization.
    """
    endpoint = f"http://cromag.{env}.milezero.com/retail/api/hubs/org/{orgId}?hubType=HUB"

    return requests.get(url=endpoint, timeout=10).json()["hubs"]


def search_hub_by_name(env, orgId, hubName):
    """
    Searches for a hub by its name within an organization.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization ID.
        hubName (str): The name of the hub.

    Returns:
        list: A list of hubs matching the search criteria.
    """
    url = f"http://cromag.{env}.milezero.com/retail/api/hubs/org/{orgId}?hubType=HUB&keyType=name&key={hubName}"

    response = requests.get(url=url, timeout=5).json()["hubs"]
    # print(response)

    return response


def search_hub_by_id(env, orgId, hubId):
    """
    Searches for a hub by its ID within an organization.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization ID.
        hubId (str): The ID of the hub.

    Returns:
        list: A list of hubs matching the search criteria.
    """
    url = f"http://cromag.{env}.milezero.com/retail/api/hubs/org/{orgId}?hubType=HUB&keyType=id&key={hubId}"

    return requests.get(url=url, timeout=5).json()["hubs"]
