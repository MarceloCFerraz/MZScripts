import requests

from utils import utils

VALID_STATUSES = [
    "CREATED",
    "PACKED",
    "OUT_FOR_DELIVERY",
    "PICKUP_FAILED",
    "DELIVERED",
    "DELIVERY_FAILED",
    "REJECTED",
    "RETURN_PICKUP_FAILED",
    "RETURN_PICKED_UP",
]
VALID_KEY_TYPES = [
    "pi",  # (Package Id)",
    "tn",  # (Tracking Number)",
    "ci",  # (Container Id)",
    "bc",  # (Shipment Barcode)",
    "oi",  # (Order Id)",
    "ori",  # (Order Reference Id)",
    "ji",  # (Job Id)",
]


def move_package_to_hub(env, org_id, newHub, packageId, dispatcher, userName):
    """
    Moves a package to a new hub.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        org_id (str): The organization ID.
        newHub (str): The name of the new hub.
        packageId (str): The ID of the package.
        dispatcher (str): The name of the dispatcher.
        userName (str): The name of the user executing the move.

    Returns:
        None
    """
    url = f"https://switchboard.{utils.convert_env(env)}.milezero.com/switchboard-war/api/package/update/{org_id}/{packageId}/hub"

    payload = {
        "hubName": newHub,
        "notes": f"Requested by {dispatcher}. Executed by {userName}",
    }
    response = requests.post(url=url, json=payload, timeout=15)
    print(f"{response} {response.text if response.status_code >= 400 else ''}")


def move_packages_to_route(env, org_id, newRouteId, packageIdsList):
    """
    Moves multiple packages to a new route.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        org_id (str): The organization ID.
        newRouteId (str): The ID of the new route.
        packageIdsList (list): A list of package IDs to be moved.

    Returns:
        response (object): The response object from the API call.
    """
    url = f"http://alamo.{utils.convert_env(env)}.milezero.com/alamo-war/api/constraints/{org_id}/packages/move"

    payload = {
        "packageIds": packageIdsList,
        "newRouteId": newRouteId,
        "associate": {
            # "associateId": "0ebaddf3-83ea-4713-97da-66552323fc0c",
            # "associateName": "Marcelo Superuser",
            "associateId": "MZSupport",
            "associateName": "MZSupport",
            "associateType": "ORG_SUPERUSER",
        },
    }

    response = requests.post(url=url, json=payload, timeout=60)
    print(f"{response} {response.text if response.status_code >= 400 else ''}")

    return response


def bulk_cancel_packages(env, org_id, packageIds):
    """
    Cancels multiple packages.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        org_id (str): The organization ID.
        packageIds (list): A list of package IDs to be cancelled.

    Returns:
        None
    """
    # newStatus = "CANCELLED"

    API = f"https://switchboard.{utils.convert_env(env)}.milezero.com/switchboard-war/api/package/cancel"

    requestData = {
        "orgId": org_id,
        "packageIds": packageIds,
        # "associate": {
        #     "name": "string",
        #     # "id": "string",
        #     # "type": "string"
        # },
        "notes": "Requested by dispatcher",
    }

    try:
        response = requests.post(url=API, json=requestData, timeout=10)
        print(f"> Result: ({response.status_code})\n")
        print(f"{response.text}")
    except Exception as e:
        print(f"> {packageIds} couldn't be CANCELLED. See error bellow")
        print(e)


def mark_package_as_delivered(env, org_id, packageId):
    """
    Marks a package as delivered.

    Parameters:
        org_id (str): The organization ID.
        packageId (str): The ID of the package.

    Returns:
        None
    """
    url = f"http://switchboard.{utils.convert_env(env)}.milezero.com/switchboard-war/api/package/update/{org_id}/{packageId}/DELIVERED/status"
    body = {"notes": "Requested by dispatcher"}
    print(f">>>>> Marking {packageId} as DELIVERED <<<<<")

    response = requests.post(url=url, json=body)

    print("> OK" if response.status_code < 400 else f"> FAIL\n{response.text}")


def bulk_get_package_details(env, org_id, key_type, keys):
    url = f"https://switchboard.{utils.convert_env(env)}.milezero.com/switchboard-war/api/package/search/bulk"

    payload = {
        "idType": key_type,
        "ids": keys,
        "filters": {
            "orgId": org_id,
            "includeCancelledPackage": True,
        },
    }

    return requests.post(url=url, json=payload, timeout=30).json()


def get_packages_details(env, org_id, key_type, key):
    """
    Retrieves details of packages based on a specific key.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        org_id (str): The organization ID.
        key_type (str): The type of key to search for (e.g. 'bc', 'pi').
        key (str): The value of the key.

    Returns:
        response (object): The response object from the API call.
    """
    API = (
        f"http://switchboard.{utils.convert_env(env)}.milezero.com/switchboard-war/api/"
    )
    endpoint = f"{API}package?keyType={key_type}&keyValue={key}&orgId={org_id}&includeCancelledPackage=true"

    print(f">>>>> Retrieving Packages From {key_type.upper()} {key} <<<<<")

    return requests.get(endpoint, timeout=5).json()


def get_packages_histories(env, org_id, key_type, key):
    """
    Retrieves the histories of packages based on a specific key.

    Parameters:
        key_type (str): The type of key to search for (e.g. 'bc', 'pi').
        key (str): The value of the key.

    Returns:
        response (object): The response object from the API call.
    """
    endpoint = f"https://switchboard.{utils.convert_env(env)}.milezero.com/switchboard-war/api/package/histories?keyValue={key}&keyType={key_type}&orgId={org_id}&orderBy=timestamp"

    print(">>>>> Retrieving Packages From {} {} <<<<<".format(key_type.upper(), key))

    return requests.get(url=endpoint, timeout=15).json()


def print_minimal_package_details(package):
    """
    Prints reduced details of a package.

    Parameters:
        package (dict): The package object containing the details.

    Returns:
        None
    """
    packageID = package.get("packageId")
    ori = package.get("orderDetails").get("orderReferenceId")
    hubName = package.get("packageDetails").get("sourceLocation").get("name")
    barcode = package.get("packageDetails").get("shipmentBarcode")
    status = package.get("packageStatuses").get("status")

    print(f"HUB Name:           {hubName}")
    print(f"Package ID:         {packageID}")
    print(f"Order Reference ID: {ori}")
    print(f"Scannable Barcode:  {barcode}")
    print(f"Curent Status:      {status}")


def print_package_details(package):
    """
    Prints the details of a package.

    Parameters:
        package (dict): The package object containing the details.

    Returns:
        None
    """
    packageID = package.get("packageId")
    org_id = package.get("orgId")
    hubId = package.get("hubId")
    ori = package.get("orderDetails").get("orderReferenceId")
    hubName = package.get("packageDetails").get("sourceLocation").get("name")
    barcode = package.get("packageDetails").get("shipmentBarcode")

    routeId = ""
    try:
        routeId = package.get("planningDetails").get("plannerRouteId")
    except Exception:
        print("This package/route was probably not executed (no ROUTE_ID found)")

    previousRouteId = package.get("planningDetails").get("originalRouteId")
    routeName = package.get("planningDetails").get("plannerRouteName")
    deliveryWindow = (
        package.get("planningDetails").get("requestedTimeWindow").get("start")
        + " - "
        + package.get("planningDetails").get("requestedTimeWindow").get("end")
    )
    status = package.get("packageStatuses").get("status")

    half_divisor = "==================="

    print(f"\n{half_divisor} PACKAGE {half_divisor}")
    print(f"Package ID:         {packageID}")
    print(f"Scannable Barcode:  {barcode}")
    print(f"Order Reference ID: {ori}")
    print(f"Delivery Window:    {deliveryWindow}")
    print(f"Curent Status       {status}")

    print(f"\n{half_divisor} ORG & HUB {half_divisor}")
    print(f"Org ID:             {org_id}")
    print(f"HUB Name:           {hubName}")
    print(f"HUB ID:             {hubId}")

    print(f"\n{half_divisor} ROUTE {half_divisor}")
    print(f"Route Name:         {routeName}")
    print(f"Route ID:           {routeId}")
    print(f"Original Route ID:  {previousRouteId}\n")


def print_package_histories(package):
    """
    Prints the package histories.

    Args:
        package (dict): The package information.

    Returns:
        None
    """
    org_id = package.get("orgId")
    ori = package.get("orderReferenceId")
    packageID = package.get("packageId")
    hubName = package.get("hubName")
    barcode = package.get("barcode")
    histories = package.get("histories")

    half_divisor = "==================="

    print(f"\n{half_divisor} PACKAGE {half_divisor}")
    print(f"Package ID: {packageID}")
    print(f"Scannable Barcode: {barcode}")
    print(f"Order Reference ID: {ori}")

    print(f"\n{half_divisor} ORG & HUB {half_divisor}")
    print(f"Org ID: {org_id}")
    print(f"HUB Name: {hubName}")

    print(f"\n{half_divisor} HISTORIES {half_divisor}")
    for index in range(0, len(histories)):
        print(f"{index}:")

        when = histories[index].get("timestamp")
        print(f"\tTime Stamp: {when}")

        action = histories[index].get("action")
        print(f"\tAction: {action}")

        status = histories[index].get("neoStatus")
        print(f"\tStatus: {status}")

        associate_name = histories[index].get("associateName")
        print(f"\tResponsible: {associate_name}")

        associate = histories[index].get("associate")
        if associate is not None:
            associate_id = associate.get("id")
            associate_type = associate.get("type")
            print(f"\tAssociate: {associate_id} ({associate_type})")

        optional_values = histories[index].get("optionalValues")
        if optional_values is not None:
            routeId = optional_values.get("ROUTE_ID")
            if routeId is not None:
                print(f"\tRoute ID: '{routeId}'")

        notes = histories[index].get("notes")
        print(f"\tNotes: '{notes}'\n")


def revive_package(env, package):
    """
    Revives a package.

    Args:
        env (str): The environment.
        package (dict): The package information.

    Returns:
        None
    """
    API = (
        f"http://switchboard.{utils.convert_env(env)}.milezero.com/switchboard-war/api/"
    )
    org_id = package["orgId"]
    packageId = package["packageId"]
    requestData = {"notes": "Requested by dispatcher"}

    endpoint = "{}package/revive/{}/{}".format(API, org_id, packageId)

    print(f">>>>> Reviving {packageId} <<<<<")

    response = requests.post(endpoint, json=requestData, timeout=15)
    print(
        f"{response.status_code} {response.text if response.status_code > 400 else ''}"
    )


def mark_package_as_delivery_failed(env, package):
    """
    Marks a package as DELIVERY_FAILED.

    Args:
        env (str): The environment.
        package (dict): The package information.

    Returns:
        None
    """
    org_id = package["orgId"]
    packageId = package["packageId"]

    url = f"http://switchboard.{utils.convert_env(env)}.milezero.com/switchboard-war/api/package/update/{org_id}/{packageId}/DELIVERY_FAILED/status"

    requestData = {"notes": "Requested By Dispatcher"}

    print(f">>>>> Marking {packageId} as DELIVERY_FAILED <<<<<")

    try:
        response = requests.post(url=url, json=requestData, timeout=15)
        print("> OK" if response.status_code < 400 else f"> FAIL\n{response.text}")
    except Exception as e:
        print("> Package couldn't be marked as DELIVERY_FAILED. See error bellow")
        print(e)


def resubmit_package(env, org_id, packageId, next_delivery_date):
    """
    Resubmits a package for a specific delivery date.

    Args:
        env (str): The environment.
        org_id (str): The organization ID.
        packageId (str): The package ID.
        next_delivery_date (str): The next delivery date.

    Returns:
        dict: The response containing the success and error information.
    """
    url = f"http://switchboard.{utils.convert_env(env)}.milezero.com/switchboard-war/api/fulfillment/resubmit/{org_id}/{packageId}"

    requestData = {
        "adjustTimeWindow": True,
        "treatEverydayAsProcessingDay": False,
        "targetLocalDate": next_delivery_date,
        "notes": "Requested by dispatcher",
    }

    print(f">>>>> Resubmitting {packageId} ({next_delivery_date}) <<<<<")
    res = {"SUCCESS": "", "ERROR": ""}

    response = requests.post(url=url, json=requestData, timeout=15).json()

    if response.get("timeWindow") is not None:
        res["SUCCESS"] = packageId
    else:
        res["ERROR"] = f"{packageId}"
        print(">> Package couldn't be submitted")
        print(">> Response: " + response)

    return res


def bulk_resubmit_packages(env, org_id, packageIDs, next_delivery_date):
    """
    Resubmits multiple packages in bulk for a specific delivery date.

    Args:
        env (str): The environment.
        org_id (str): The organization ID.
        packageIDs (list): The list of package IDs.
        next_delivery_date (str): The next delivery date.

    Returns:
        dict: The response containing the success and error information.
    """
    url = f"https://switchboard.{utils.convert_env(env)}.milezero.com/switchboard-war/api/fulfillment/resubmit/bulk/{org_id}"

    requestData = {
        "packageIds": packageIDs,
        "adjustTimeWindow": True,
        "treatEverydayAsProcessingDay": False,
        "targetLocalDate": next_delivery_date,
        "notes": "Requested by dispatcher",
    }

    response = requests.post(url=url, json=requestData, timeout=15).json()
    res = {"SUCCESS": [], "ERROR": []}

    for success in response.get("succeededResubmits"):
        res["SUCCESS"].append(success.get("packageId"))

    for error in response.get("failedResubmits"):
        res["ERROR"].append(error.get("packageId"))

    print(
        f">>>>> New Batch ({len(packageIDs)} {next_delivery_date}) <<<<<\n"
        + f"> {len(res['SUCCESS'])} OK\t {len(res['ERROR'])} FAILED"
    )

    return res


def get_all_packages_on_route(env, org_id, routeId):
    """
    Retrieves all packages on a specific route.

    Args:
        env (str): The environment.
        org_id (str): The organization ID.
        routeId (str): The route ID.

    Returns:
        list: The list of packages on the route.
    """
    url = f"http://sortationservices.{utils.convert_env(env)}.milezero.com/SortationServices-war/api/monitor/packages/{org_id}/{routeId}"

    print(f">> Searching for packages in {routeId}")

    response = requests.get(url=url, timeout=15).json()

    print(f"Found {len(response)} packages in {routeId}")

    return response


def get_all_packages_for_hub(env, org_id, hubName, date):
    """
    Retrieves all packages for a specific hub and date.

    Args:
        env (str): The environment.
        org_id (str): The organization ID.
        hubName (str): The hub name.
        date (str): The date.

    Returns:
        list: The list of package IDs for the hub and date.
    """
    endpoint = f"http://sortationservices.{utils.convert_env(env)}.milezero.com/SortationServices-war/api/monitor/getPackagesInWave/{org_id}/{hubName}/{date}/true"

    packageCount = 0
    packageIDs = []

    try:
        packages = requests.get(url=endpoint, timeout=10).json()["packagesMap"]

        for statusGroup in packages.keys():
            for package in packages[statusGroup]:
                packageId = package["externalPackageId"]
                packageIDs.append(packageId)

    except Exception:
        pass

    if packageCount > 0:
        print(f"{len(packageIDs)} packages")

    return packageIDs


def select_key_type():
    """
    Allows the user to select an environment.

    Returns:
        str: The selected environment.
    """
    key_type_ids = VALID_KEY_TYPES
    key_type = ""
    utils.print_formatted_message("SELECT THE KEY TYPE", len(key_type_ids), " ")
    utils.print_formatted_message("Options", len(key_type_ids))
    utils.print_array_items(key_type_ids)
    while key_type not in key_type_ids:
        key_type = str(input("> ")).lower().strip()

    return key_type


def get_list_of_keys(key_type):
    print(
        ">> Please, type the keys to search packages one per time.\n"
        + f">> They should all be of the same type ({str(key_type).upper()}) otherwise, the program will break.\n"
        + ">> At least one key is needed.\n"
        + ">> Leave blank and hit Enter once you're done.\n"
    )
    keys = set()

    while True:
        key = input(">> ")

        if key != "":
            keys.add(key)
        elif len(keys) > 0:
            break  # if key is an empty string and user already saved other keys, means he wants to continue

    return list(keys)


def get_package_hub(package):
    """
    Get the hub name associated with a package.

    Parameters:
    - package: A dictionary representing the package details.

    Returns:
    - hubName: The name of the hub associated with the package.
    """
    hubName = utils.extract_property(
        package, ["packageDetails", "sourceLocation", "name"]
    )

    if hubName is not None:
        return hubName

    hubName = utils.extract_property(package, ["packageDetails", "clientHub"])

    if hubName is not None:
        return hubName

    hubName = utils.extract_property(package, ["packageDetails", "destination", "name"])

    if hubName is not None:
        return hubName

    return None
