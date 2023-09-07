import requests


def get_associate_data(env, orgId, associateId):
    url = f"http://lmx.{env}.milezero.com/lmx-war/api/associate/org/{orgId}/{associateId}"

    print(f"Searching for ({env})\n" +
          f"> OrgId {orgId}\n" +
          f"> AssociateId {associateId}")
    response = requests.get(url=url, timeout=10).json()

    try:
        test = response["organizationId"]
        return response
    except Exception as e:
        print("An error has occurred")
        print(e)
        return None


def search_associate(env, org_id, key_type_index, search_key):
    time = 30
    url = f"http://lmx.{env}.milezero.com/lmx-war/api/associate/all"

    key_types = [
        "orgId", "referenceId", "name", "email", "userName", "state", "type", "associateType", "skill",
        "skillRatingValue", "rating", "fleetId", "clusterId", "hubId", "locationId",
        "worldViewId", "availabilityFleetId", "availabilityClusterId"
    ]

    requestData = {}

    if key_type_index > 0:
        requestData["orgId"] = org_id
        time = 30
    
    key_type = str(key_types[key_type_index])
    
    requestData[key_type] = search_key

    p = "Searching for associates with\n"
    for key in requestData.keys():
        p += f"> {key} {requestData[key]}\n"
    print(p)
    response = requests.post(url=url, json=requestData, timeout=time).json()

    try:
        return response["associates"]
    except Exception as e:
        print("Couldn't find associates with provided data")
        print(e)
        return None


def change_associate_state(env, associateData, userName):
    state = associateData["state"]
    print(f"Was {state}.", end=" ")

    if state == "ACTIVE":
        state = "INACTIVE"
    else:
        state = "ACTIVE"

    print(f"Updating to {state}")
    associateData["state"] = state

    return update_associate_data(env, associateData, userName)


def update_associate_data(env, associateData, userName):
    print("Updating Associate data")
    url = f"http://lmx.{env}.milezero.com/lmx-war/api/associate?requestor={str(userName).replace(' ', '%20')}&requestorIdType=NAME"
    return requests.put(url=url, json=associateData, timeout=5)
