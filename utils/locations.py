import json
import requests

def get_location(env, locationId):
    """
    Retrieves an specific location.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        locationId (str): The ID of the location.

    Returns:
        dict: The lockbox location data.
    """
    url = f"http://lockbox.{env}.milezero.com/lockbox-war/api/location/{locationId}"

    return requests.get(url=url, timeout=5).json()


def get_all_addresses_from_hub(env, orgId, hubName, index):
    """
    Retrieves up to 500 locations linked to a HUB. Max addresses is 10000, use index to navigate in intervals of 500

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization's ID (e.g., 3c897e84-3957-4958-b54d-d02c01b14f15 for Staples on PROD)
        hubName (str): The HUB which locations are related to.
        index (int): The location index number. This endpoint works with pagination, Index is used to navigate through pages

    Returns:
        dict: {
            locations (dict): {
                locationId (dict): {
                    id (int): Lockbox location ID, same as the key of the dict (locationId),
                    name (str): Lockbox location name,
                    hubNames (list): Hubs which this location is linked to
                    address (dict): Object containing address details (e.g. street 1, city, zip)
                    contact (dict): Object containing contact details (e.g. phone number). Usually empty
                }
                ...
            },
            count (int): Number of matches returned with pagination,
            total (int): Total number of matches for the search without pagination,
            latency (int): Amount of miliseconds to get the response,
            error (str): Error message if something went wrong, else, doesn't come on the response
        }.
    """
    url = f"https://gazetteer.{env}.milezero.com/gazetteer-war/api/location/matching/org/{orgId}"

    headers = {'content-type': 'application/json'}

    payload = {
        "hubName": f"{hubName}",
        "queryMode": "MATCH_ALL_IN_ORDER",
        "pagination": {
            "from": index,
            "size": 500
        }
    }

    response = requests.post(
        url=url,
        data=json.dumps(payload), 
        headers=headers
    )

    return response