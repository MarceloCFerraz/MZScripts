import requests
import organizations


def search_fleet(env, orgId, fleetId=None):
    """
    Searches for a fleet by organization ID and optional fleet ID.

    Parameters:
        env (str): The environment name.
        orgId (int): The ID of the organization.
        fleetId (int, optional): The ID of the fleet (default: None).

    Returns:
        dict: Matching fleet
        list: All org fleets if no fleet ID is provided.
    """
    url = f"http://qilin.{env}.milezero.com/qilin-war/api/fleets/{orgId}"
    if fleetId is not None:
        url += f"?fleetId={fleetId}"

    # print(f"Searching for:")
    # print(f"ORG ID: {orgId}")
    # print(f"Fleet ID: {fleetId}\n")

    return requests.get(url=url, timeout=10).json()


def get_hubs_from_fleet(env, orgId, fleetId):
    """
    Retrieves the hub IDs associated with a fleet.

    Parameters:
        env (str): The environment name.
        orgId (int): The ID of the organization.
        fleetId (int): The ID of the fleet.

    Returns:
        list: The list of hub IDs.
    """
    return search_fleet(env, orgId, fleetId)[0]["hubIds"]


def search_fleet_with_hubs(env, orgId, hubIdsList):
    """
    Searches for a fleet that contains a specific list of hub IDs.

    Parameters:
        env (str): The environment name.
        orgId (int): The ID of the organization.
        hubIdsList (list): The list of hub IDs to search for.

    Returns:
        int or None: The fleet ID if found, or None if no fleet is found.
    """
    print(f"Searching for a fleet that contains {hubIdsList}")
    hubIdsList.sort()
    fleets = search_fleet(env, orgId)

    for fleet in fleets:
        try:
            fleetHubs = fleet["hubIds"].sort()
            if fleetHubs == hubIdsList:
                return fleet["fleetId"]
        except Exception:
            pass

    print("No fleets found!")

    return None


def create_fleet(env, orgId, hubsList, fleetName=None, fleetLogo=None):
    """
    Creates a new fleet with the given hub IDs.

    Parameters:
        env (str): The environment name.
        orgId (int): The ID of the organization.
        hubsList (list): The list of hubs for the fleet.

    Returns:
        int: The ID of the created fleet.
    """
    hubNames = []
    hubIds = []
    for hub in hubsList:
        hubNames.append(hub["name"])
        hubIds.append(hub["id"])

    customer = organizations.get_org_by_id(env, orgId)

    url = f"http://qilin.{env}.milezero.com/qilin-war/api/fleets/{orgId}"


    requestData = {
      "fleetName": fleetName if fleetName != None else f"{customer['name'].upper()}",
      "description": f"{customer['name'].upper()} {' '.join(hubNames)} Fleet",
      "hubIds": hubIds,
      "logoUrl": fleetLogo if fleetLogo != None else f"{customer['logo']}",
      "active": True
    }

    return requests.post(url=url, json=requestData, timeout=5).json()["fleetId"]


def update_fleet(env, orgId, fleet):
    """
    Updates an existing fleet with new information.

    Parameters:
        env (str): The environment name.
        orgId (int): The ID of the organization.
        fleet (dict): The updated fleet information.

    Returns:
        Response: The response object from the update request.
    """
    url = f"http://qilin.{env}.milezero.com/qilin-war/api/fleets/{orgId}/{fleet['fleetId']}"
    return requests.post(url=url, json=fleet, timeout=5)


def update_fleet_hubs(env, orgId, fleetId, hubsList):
    """
    Updates the hub IDs and description of a fleet.

    Parameters:
        env (str): The environment name.
        orgId (int): The ID of the organization.
        fleetId (int): The ID of the fleet.
        hubsList (list): The updated list of hubs for the fleet.

    Returns:
        Response: The response object from the update request.
    """
    customer = organizations.get_org_by_id(env, orgId)

    # print(f"Updating {fleetId} with hubs", end=" ")

    hubNames = []
    hubIds = []

    for hub in hubsList:
        hubNames.append(hub["name"])
        hubIds.append(hub["id"])
    # print(' '.join(hubNames))

    fleet = search_fleet(env, orgId, fleetId)[0]
    fleet["description"] = f"{customer['name'].upper()} {' '.join(hubNames)} Fleet"
    fleet["hubIds"] = hubIds

    return update_fleet(env, orgId, fleet)


def remove_hub_from_fleet(env, orgId, fleetId, hubId):
    """
    Removes a hub from a fleet.

    Parameters:
        env (str): The environment name.
        orgId (int): The ID of the organization.
        fleetId (int): The ID of the fleet.
        hubId (int): The ID of the hub to remove.

    Returns:
        Response: The response object from the update request.
    """
    fleet = search_fleet(env, orgId, fleetId)[0]

    fleet["hubIds"].remove(hubId)

    return update_fleet(env, orgId, fleet)


def delete_fleet(env, orgId, fleetId):
    """
    Deletes a fleet by ID.

    Parameters:
        env (str): The environment name.
        orgId (int): The ID of the organization.
        fleetId (int): The ID of the fleet to delete.

    Returns:
        Response: The response object from the delete request.
    """
    url = f"http://qilin.{env}.milezero.com/qilin-war/api/fleets/{orgId}/{fleetId}"

    return requests.delete(url=url, timeout=5)
