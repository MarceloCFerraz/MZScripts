import requests


def get_org_by_id(env, orgId):
    url = f"http://cromag.{env}.milezero.com/retail/api/organization/{orgId}"

    return requests.get(url=url, timeout=5).json()


def search_fleet(env, orgId, fleetId=None):
    url = f"http://qilin.{env}.milezero.com/qilin-war/api/fleets/{orgId}"
    if fleetId is not None:
        url += f"?fleetId={fleetId}"

    return requests.get(url=url, timeout=5).json()


def get_hubs_from_fleet(env, orgId, fleetId):
    return search_fleet(env, orgId, fleetId)[0]["hubIds"]


def search_fleet_with_hubs(env, orgId, hubIdsArray):
    print(f"Searching for a fleet that contains {hubIdsArray}")
    hubIdsArray.sort()
    fleets = search_fleet(env, orgId)

    for fleet in fleets:
        try:
            fleetHubs = fleet["hubIds"].sort()
            if fleetHubs == hubIdsArray:
                return fleet["fleetId"]
        except Exception:
            pass

    print("No fleets found!")

    return None


def create_fleet(env, orgId, hubsArray):
    print(f"Creating new fleet with hubs", end=" ")
    customer = get_org_by_id(env, orgId)

    url = f"http://qilin.{env}.milezero.com/qilin-war/api/fleets/{orgId}"

    hubNames = []
    hubIds = []
    for hub in hubsArray:
        hubNames.append(hub["name"])
        hubIds.append(hub["id"])
    print(hubIds)

    requestData = {
      "fleetName": f"{customer['name'].upper()}",
      "description": f"{customer['name'].upper()} {' '.join(hubNames)} Fleet",
      "hubIds": hubIds,
      "logoUrl": f"{customer['logo']}",
      "active": True
    }

    return requests.post(url=url, json=requestData, timeout=5).json()["fleetId"]


def update_fleet(env, orgId, fleet):
    fleetId = fleet["fleetId"]
    url = f"http://qilin.{env}.milezero.com/qilin-war/api/fleets/{orgId}/{fleetId}"
    return requests.post(url=url, json=fleet, timeout=5)


def update_fleet_hubs(env, orgId, fleetId, hubsArray):
    customer = get_org_by_id(env, orgId)

    print(f"Updating fleet {fleetId} with hubs", end=" ")

    hubNames = []
    hubIds = []

    for hub in hubsArray:
        hubNames.append(hub["name"])
        hubIds.append(hub["id"])
    print(hubIds)

    fleet = search_fleet(env, orgId, fleetId)[0]
    fleet["description"] = f"{customer['name'].upper()} {' '.join(hubNames)} Fleet"
    fleet["hubIds"] = hubIds

    return update_fleet(env, orgId, fleet)


def remove_hub_from_fleet(env, orgId, fleetId, hubId):
    fleet = search_fleet(env, orgId, fleetId)[0]

    fleet["hubIds"].remove(hubId)

    return update_fleet(env, orgId, fleet)
