import sys

import requests

from utils import utils


def get_hub_config(env, orgId, hubId) -> dict | None:
    """
    Retrieves the configuration for a specific hub.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization ID.
        hubId (str): The ID of the hub.

    Returns:
        dict: The configuration for the hub.
    """
    url = f"http://alamo.{utils.convert_env(env)}.milezero.com/alamo-war/api/hubconfig/key/orgId/{orgId}?key={hubId}&keyType=HUB_ID"

    response = requests.get(url=url, timeout=10)

    if response.status_code >= 400:
        raise Exception(f"Error getting hubs: {response.status_code} {response.text}")

    if not response.json().get("config"):
        print(f"Hub not found: {hubId}")
        return None

    return response.json()["config"]


def get_all_hubs(env, orgId) -> list:
    """
    Retrieves all hubs within an organization.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization ID.

    Returns:
        list: A list of all hubs within the organization.
        None: if
    """
    endpoint = f"http://cromag.{utils.convert_env(env)}.milezero.com/retail/api/hubs/org/{orgId}?hubType=HUB"

    try:
        response = requests.get(url=endpoint, timeout=10)
        response = response.json()["hubs"]
        return response
    except Exception as e:
        print(f"An error occurred, please check the error message and try again!\n {e}")
        return []


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
    url = f"http://cromag.{utils.convert_env(env)}.milezero.com/retail/api/hubs/org/{orgId}?hubType=HUB&keyType=name&key={hubName}"
    response = requests.Response()

    try:
        response = requests.get(url=url, timeout=5)
        response = response.json()["hubs"]
        return response
    except ConnectionError as e:
        print(f"Connection Error. Please connect to the VPN!\n {e}")
    # print(response)
    except Exception as e:
        print(f"Something Went wrong: {e}")

    sys.exit(1)


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
    url = f"http://cromag.{utils.convert_env(env)}.milezero.com/retail/api/hubs/org/{orgId}?hubType=HUB&keyType=id&key={hubId}"
    response = None

    try:
        response = requests.get(url=url, timeout=5).json()["hubs"]
    except ConnectionError as e:
        print(f"Connection Error. Please connect to the VPN!\n {e}")

    return response
