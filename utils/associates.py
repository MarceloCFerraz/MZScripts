import requests

from utils import utils


def choose_associate(associatesList: list) -> dict | None:
    """
    Iterates through each associate in associates list and gives the user the option to select a associate that offers a better fit or select none.

    The section below prints something like this:
        ```text
        >> 0 - NAME 1 - E-MAIL 1 - ID 1
        >> 1 - NAME 2 - E-MAIL 2 - ID 2
        >> 2 - NAME 3 - E-MAIL 3 - ID 3
        ```

    Returns:
        associate (dict): the associate data if the user selected a associate from the options array
    """
    print(f">> We found {len(associatesList)} compatible associates:")
    index = 0

    for index in range(0, len(associatesList)):
        id = associatesList[index]["associateId"]
        name = associatesList[index]["contact"]["name"]
        email = associatesList[index]["contact"]["email"]
        accountType = associatesList[index]["associateType"]
        state = associatesList[index]["state"]
        hubId = associatesList[index]["hubId"]

        print(f"{index}:")
        print(f"\tID: {id}")
        print(f"\tName: {name}")
        print(f"\tEmail: {email}")
        print(f"\tAccount Type: {accountType}")
        print(f"\tState: {state}")
        print(f"\tHub ID: {hubId}")

    selection = -1
    quit = -7

    print(f"\n>> Please type the number of the associate or '{quit}' to quit")
    while selection not in range(0, len(associatesList)):
        try:
            selection = int(input("> ").strip())

            if selection == quit:
                return None

        except ValueError:
            print(
                "\n>> Please type only the number of the desired associate. For example:"
            )
            print(">> 0 << - NAME 1 - E-MAIL 1 - ID 1")
            print(">> 1 << - NAME 2 - E-MAIL 2 - ID 2")

    return associatesList[selection]


def get_associate_by_id(env, orgId, acceptBlank) -> dict | None:
    """
    Retrieves associate data based on the associate's ID.

    Parameters:
    - env (str): The environment in which the associate data is stored.
    - orgId (str): The organization ID associated with the associate.
    - acceptBlank (bool): Whether to accept blank input from the user.

    Returns:
    - associate (dict): an associate LMX data.
    - None: if an associate wasn't found or if blank input is allowed
    """
    while True:
        print(
            ">> Insert the Associate ID ",
            (
                "(leave blank and hit enter if done)"
                if acceptBlank
                else "(or hit Ctrl + C to quit program)"
            ),
        )
        associateId = input("> ")

        if associateId == "":
            if acceptBlank:
                return None
            else:
                print(
                    ">> Can't accept blank. Try again (or hit Ctrl + C to quit program)"
                )
        else:
            return get_associate_data(env, orgId, associateId)


def get_associate_by_name_or_email(env, orgId, acceptBlank) -> dict | None:
    """
    Retrieves associate data based on the associate's name or email.

    Parameters:
    - env (str): The environment in which the associate data is stored.
    - orgId (str): The organization ID associated with the associate.
    - acceptBlank (bool): Whether to accept blank input from the user.

    Returns:
    - associate (dict): an associate LMX data.
    - None: if an associate wasn't found or if blank input is allowed
    """
    # TODO: list associates found and ask user to select one
    while True:
        print(
            ">> Type the associate's e-mail or name ",
            (
                "(leave blank and hit enter if done)"
                if acceptBlank
                else "(or hit Ctrl + C to quit program)"
            ),
        )
        search_key = input("> ")
        print()

        if search_key == "" and acceptBlank:
            return None

        search_key_index = 3 if "@" in search_key else 2
        # based on key_types list in associates.search_associate()

        associate = search_associate(env, orgId, search_key_index, search_key)

        if not associate:
            msg = ">> Associate not found"
            blankMsg = " and blank is not allowed"
            end = ". Try again or hit CTRL + C to quit"

            if not acceptBlank:
                print(msg + blankMsg + end)
            else:
                print(msg + " but we'll continue anyway")
                return None

            continue

        if len(associate) > 0:
            associate = choose_associate(associate)
        elif associate:
            associate = associate[0]

        return None


def get_associate_data(env, orgId, associateId):
    """
    Retrieves associate data by organization ID and associate ID.

    Parameters:
        env (str): The environment name.
        orgId (int): The ID of the organization.
        associateId (int): The ID of the associate.

    Returns:
        dict or None: The associate data if found, or None if not found.
    """
    url = f"http://lmx.{utils.convert_env(env)}.milezero.com/lmx-war/api/associate/org/{orgId}/{associateId}"

    # print(f"\nSearching for ({utils.convert_env(env)})\n" +
    #       f"> OrgId {orgId}\n" +
    #       f"> AssociateId {associateId}")
    response = requests.get(url=url, timeout=10).json()

    if response.get("organizationId") is not None:
        return response
    else:
        print("Associate not found or another an error has occurred")
        return None


def get_associate_device_and_app(env, org_id, associate_id):
    url = f"http://wv.{utils.convert_env(env)}.milezero.com/wv/api/search/v3/org/{org_id}/container/id/{associate_id}?containerType=WORKER"

    response = requests.get(url=url, timeout=15).json()

    if response.get("stackTrace") is not None:
        print(f"{response['status']} > {response['message']}")
        return None

    return response


def search_associate(env, org_id, key_type_index, search_key) -> list | None:
    """
    Searches for associates based on a specific key type and search key.

    Parameters:
        env (str): The environment name.
        org_id (int): The ID of the organization.
        key_type_index (int): The index of the key type in the key_types list.
            0: "orgId"
            1: "referenceId"
            2: "name"
            3: "email"
            4: "userName"
            5: "state"
            6: "type"
            7: "associateType"
            8: "skill"
            9: "skillRatingValue"
            10: "rating"
            11: "fleetId"
            12: "clusterId"
            13: "hubId"
            14: "locationId"
            15: "worldViewId"
            16: "availabilityFleetId"
            17: "availabilityClusterId"
        search_key (str): The search key.

    Returns:
        list or None: The list of associates if found, or None if not found.
    """
    time = 30
    url = f"http://lmx.{utils.convert_env(env)}.milezero.com/lmx-war/api/associate/all"

    key_types = [
        "orgId",
        "referenceId",
        "name",
        "email",
        "userName",
        "state",
        "type",
        "associateType",
        "skill",
        "skillRatingValue",
        "rating",
        "fleetId",
        "clusterId",
        "hubId",
        "locationId",
        "worldViewId",
        "availabilityFleetId",
        "availabilityClusterId",
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
    """
    Changes the state of an associate from ACTIVE to INACTIVE or vice versa.

    Parameters:
        env (str): The environment name.
        associateData (dict): The associate data.
        userName (str): The name of the user.

    Returns:
        Response: The response object from the update request.
    """
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
    """
    Updates the data of an associate.

    Parameters:
        env (str): The environment name.
        associateData (dict): The associate data.
        userName (str): The name of the user.

    Returns:
        Response: The response object from the update request.
    """
    url = f"http://lmx.{utils.convert_env(env)}.milezero.com/lmx-war/api/associate?requestor={str(userName).replace(' ', '%20')}&requestorIdType=NAME"
    return requests.put(url=url, json=associateData, timeout=5)


def get_telemetries(env, orgId, associateId, startTime, endTime):
    """
    Retrieve telemetries for a specific associate within a given time range.

    Parameters:
    - env: The environment.
    - orgId: The ID of the organization.
    - associateId: The ID of the associate.
    - startTime: The start time of the telemetry range.
    - endTime: The end time of the telemetry range.

    Returns:
    - events: A list of telemetry events.
    """
    formattedStart = str(startTime).replace(":", "%3A")
    formattedEnd = str(endTime).replace(":", "%3A")

    endpoint = f"http://lmx.{utils.convert_env(env)}.milezero.com/lmx-war/api/lmxtelemetry/org/{orgId}/owner/{associateId}?startTime={formattedStart}&endTime={formattedEnd}"

    return requests.get(url=endpoint, timeout=10).json()["events"]


def get_associate_latest_itinerary(env, org_id, associate_id):
    url = f"http://redeux.{utils.convert_env(env)}.milezero.com/redeux-server/api/drivers/{associate_id}/itineraries/latest"
    headers = {"Accept": "application/json", "X-Consumer-Custom-ID": f"{org_id}"}

    return requests.get(url=url, headers=headers).json()
