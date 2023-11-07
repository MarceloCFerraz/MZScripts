import requests


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
    "pi (Package Id)",
    "tn (Tracking Number)",
    "ci (Container Id)",
    "bc (Shipment Barcode)",
    "oi (Order Id)",
    "ori (Order Reference Id)",
    "ji (Job Id)"
]


def move_package_to_hub(env, orgId, newHub, packageId, dispatcher, userName):
    """
    Moves a package to a new hub.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization ID.
        newHub (str): The name of the new hub.
        packageId (str): The ID of the package.
        dispatcher (str): The name of the dispatcher.
        userName (str): The name of the user executing the move.

    Returns:
        None
    """
    url = f"https://switchboard.{env}.milezero.com/switchboard-war/api/package/update/{orgId}/{packageId}/hub"
    
    payload = {
        "hubName": newHub,
        "notes": f"Requested by {dispatcher}. Executed by {userName}"
    }
    response = requests.post(url=url, json=payload, timeout=15)
    print(f"{response} {response.text if response.status_code >= 400 else ''}")


def move_packages_to_route(env, orgId, newRouteId, packageIdsList):
    """
    Moves multiple packages to a new route.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization ID.
        newRouteId (str): The ID of the new route.
        packageIdsList (list): A list of package IDs to be moved.

    Returns:
        response (object): The response object from the API call.
    """
    url = f"http://alamo.{env}.milezero.com/alamo-war/api/constraints/{orgId}/packages/move"

    payload = {
    "packageIds": packageIdsList,
    "newRouteId": newRouteId,
        "associate": {
            "associateId": "0ebaddf3-83ea-4713-97da-66552323fc0c",
            "associateName": "Marcelo Superuser",
            "associateType": "ORG_SUPERUSER"
        }
    }
    
    response = requests.post(url=url, json=payload, timeout=60)
    print(f"{response} {response.text if response.status_code >= 400 else ''}")

    return response


def bulk_cancel_packages(env, orgId, packageIds):
    """
    Cancels multiple packages.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization ID.
        packageIds (list): A list of package IDs to be cancelled.

    Returns:
        None
    """
    # newStatus = "CANCELLED"

    API = f"https://switchboard.{env}.milezero.com/switchboard-war/api/package/cancel"
    
    requestData = {
        "orgId": orgId,
        "packageIds": packageIds,
        # "associate": {
        #     "name": "string",
        #     # "id": "string",
        #     # "type": "string"
        # },
        "notes": "Requested by dispatcher"
    }
    
    try:
        response = requests.post(url=API, json=requestData, timeout=10)
        print(f"> Result: ({response.status_code})\n")
        print(f"{response.text}")
    except Exception as e:
        print(f"> {packageIds} couldn't be CANCELLED. See error bellow")
        print(e)


def mark_package_as_delivered(orgId, packageId):
    """
    Marks a package as delivered.

    Parameters:
        orgId (str): The organization ID.
        packageId (str): The ID of the package.

    Returns:
        None
    """
    API = "http://switchboard.prod.milezero.com/switchboard-war/api/"
    url = f"{API}package/update/{orgId}/{packageId}/DELIVERED/status"
    body = {
        "notes": "Requested by dispatcher"
    }
    print(f">>>>> Marking {packageId} as DELIVERED <<<<<")

    result = requests.post(url=url, json=body)

    print(f"{result.status_code} {result.text if result.status_code > 400 else ''}")


def get_packages_details(env, orgId, KEY_TYPE, key):
    """
    Retrieves details of packages based on a specific key.

    Parameters:
        env (str): The environment (e.g., "stage", "prod").
        orgId (str): The organization ID.
        KEY_TYPE (str): The type of key to search for (e.g. 'bc', 'pi').
        key (str): The value of the key.

    Returns:
        response (object): The response object from the API call.
    """
    API = f"http://switchboard.{env}.milezero.com/switchboard-war/api/"
    endpoint = f"{API}package?keyType={KEY_TYPE}&keyValue={key}&orgId={orgId}&includeCancelledPackage=true"

    print(f">>>>> Retrieving Packages From {KEY_TYPE.upper()} {key} <<<<<")

    return requests.get(endpoint, timeout=5).json()



def get_packages_histories(env, orgId, keyType, key):
    """
    Retrieves the histories of packages based on a specific key.

    Parameters:
        keyType (str): The type of key to search for (e.g. 'bc', 'pi').
        key (str): The value of the key.

    Returns:
        response (object): The response object from the API call.
    """
    endpoint = f"https://switchboard.{env}.milezero.com/switchboard-war/api/package/histories?keyValue={key}&keyType={keyType}&orgId={orgId}&orderBy=timestamp"

    print(">>>>> Retrieving Packages From {} {} <<<<<".format(keyType.upper(), key))

    return requests.get(endpoint).json()


def print_minimal_package_details(package):
    """
    Prints reduced details of a package.

    Parameters:
        package (dict): The package object containing the details.

    Returns:
        None
    """
    packageID = package["packageId"]
    ori = package["orderDetails"]["orderReferenceId"]            
    hubName = package["packageDetails"]["sourceLocation"]["name"]
    barcode = package["packageDetails"]["shipmentBarcode"]
    status = package["packageStatuses"]["status"]

    print(f"HUB Name: {hubName}")
    print(f"Package ID: {packageID}")
    print(f"Order Reference ID: {ori}")
    print(f"Scannable Barcode: {barcode}")
    print(f"Curent Status {status}")


def print_package_details(package):
    """
    Prints the details of a package.

    Parameters:
        package (dict): The package object containing the details.

    Returns:
        None
    """
    packageID = package["packageId"]
    orgId = package["orgId"]
    hubId = package["hubId"]
    ori = package["orderDetails"]["orderReferenceId"]            
    hubName = package["packageDetails"]["sourceLocation"]["name"]
    barcode = package["packageDetails"]["shipmentBarcode"]
    try:
        routeId = package["planningDetails"]["plannerRouteId"]
    except Exception as e:
        print("This package/route was probably not executed (not ROUTE_ID found)")
    previousRouteId = package["planningDetails"]["originalRouteId"]
    routeName = package["planningDetails"]["plannerRouteName"]
    deliveryWindow = package["planningDetails"]["requestedTimeWindow"]["start"] + " - " + package["planningDetails"]["requestedTimeWindow"]["end"]
    status = package["packageStatuses"]["status"]

    half_divisor = "==================="

    print(f"\n{half_divisor} PACKAGE {half_divisor}")
    print(f"Package ID: {packageID}")
    print(f"Scannable Barcode: {barcode}")
    print(f"Order Reference ID: {ori}")
    print(f"Delivery Window: {deliveryWindow}")
    print(f"Curent Status {status}")

    print(f"\n{half_divisor} ORG & HUB {half_divisor}")
    print(f"Org ID: {orgId}")
    print(f"HUB Name: {hubName}")
    print(f"HUB ID: {hubId}")

    print(f"\n{half_divisor} ROUTE {half_divisor}")
    print(f"Route Name: {routeName}")
    print(f"Route ID: {routeId}")
    print(f"Original Route ID: {previousRouteId}\n")


def print_package_histories(package):
    """
    Prints the package histories.

    Args:
        package (dict): The package information.

    Returns:
        None
    """
    orgId = package["orgId"]
    ori = package["orderReferenceId"]            
    packageID = package["packageId"]
    hubName = package["hubName"]
    barcode = package["barcode"]
    histories = package["histories"]

    half_divisor = "==================="

    print(f"\n{half_divisor} PACKAGE {half_divisor}")
    print(f"Package ID: {packageID}")
    print(f"Scannable Barcode: {barcode}")
    print(f"Order Reference ID: {ori}")

    print(f"\n{half_divisor} ORG & HUB {half_divisor}")
    print(f"Org ID: {orgId}")
    print(f"HUB Name: {hubName}")

    print(f"\n{half_divisor} HISTORIES {half_divisor}")
    for index in range(0, len(histories)):
        print(f"{index}:")
        when = histories[index]["timestamp"]
        print(f"\tTime Stamp: {when}")
        action = histories[index]["action"]
        print(f"\tAction: {action}")
        status = histories[index]["neoStatus"]
        print(f"\tStatus: {status}")
        associate_name = histories[index]["associateName"]
        print(f"\tResponsible: {associate_name}")
        try:
            routeId = histories[index]["optionalValues"]["ROUTE_ID"]
            print(f"\tRoute ID: '{routeId}'")
        except Exception as e:
            pass
        try:
            notes = histories[index]["notes"]
            print(f"\tNotes: '{notes}'\n")
        except Exception as e:
            pass


def revive_package(env, package):
    """
    Revives a package.

    Args:
        env (str): The environment.
        package (dict): The package information.

    Returns:
        None
    """
    API = f"http://switchboard.{env}.milezero.com/switchboard-war/api/"
    orgId = package["orgId"]
    packageId = package["packageId"]
    requestData = {
        "notes": "Requested by dispatcher"
    }

    endpoint = "{}package/revive/{}/{}".format(API, orgId, packageId)

    print(">>>>> Reviving package <<<<<")

    response = requests.post(endpoint, json=requestData, timeout=15)
    print(f"{response.status_code} {response.text if response.status_code > 400 else ''}")


def mark_package_as_delivery_failed(env, package):
    """
    Marks a package as DELIVERY_FAILED.

    Args:
        env (str): The environment.
        package (dict): The package information.

    Returns:
        None
    """
    API = f"http://switchboard.{env}.milezero.com/switchboard-war/api/"
    orgId = package["orgId"]
    packageId = package["packageId"]

    requestData = {
        "notes": "Requested By Dispatcher"
    }

    endpoint = "{}package/update/{}/{}/DELIVERY_FAILED/status".format(API, orgId, packageId)

    print(">>>>> Marking package as DELIVERY_FAILED <<<<<")
    
    try:
        response = requests.post(endpoint, json=requestData, timeout=15)
        print("> Package Marked as DELIVERY_FAILED Sucessfuly ({})\n".format(response))
    except Exception as e:
        print("> Package couldn't be marked as DELIVERY_FAILED. See error bellow")
        print(e)


def resubmit_package(env, orgId, packageId, next_delivery_date):
    """
    Resubmits a package for a specific delivery date.

    Args:
        env (str): The environment.
        orgId (str): The organization ID.
        packageId (str): The package ID.
        next_delivery_date (str): The next delivery date.

    Returns:
        dict: The response containing the success and error information.
    """
    response = {
        "SUCCESS": None,
        "ERROR": None
    }
    API = f"http://switchboard.{env}.milezero.com/switchboard-war/api/"

    requestData = {
        "adjustTimeWindow": True,
        "treatEverydayAsProcessingDay": False,
        "targetLocalDate": next_delivery_date,
        "notes": "Requested by dispatcher"
    }

    endpoint = "{}fulfillment/resubmit/{}/{}".format(API, orgId, packageId)

    print(">>>>> Resubmitting {} for {} <<<<<".format(packageId, next_delivery_date))

    try: 
        response = requests.post(endpoint, json=requestData, timeout=15).json()
        response['SUCCESS'] = packageId
    except Exception as e: 
        response['ERROR'] = f"{packageId} → {e.__reduce__().__repr__()}"

    return response


def bulk_resubmit_packages(env, orgId, packageIDs, next_delivery_date):
    """
    Resubmits multiple packages in bulk for a specific delivery date.

    Args:
        env (str): The environment.
        orgId (str): The organization ID.
        packageIDs (list): The list of package IDs.
        next_delivery_date (str): The next delivery date.

    Returns:
        dict: The response containing the success and error information.
    """
    res = {
        "SUCCESS": [],
        "ERROR": []
    }
    API = f"https://switchboard.{env}.milezero.com/switchboard-war/api/"

    requestData = {
        "packageIds": packageIDs,
        "adjustTimeWindow": True,
        "treatEverydayAsProcessingDay": False,
        "targetLocalDate": next_delivery_date,
        "notes": "Requested by dispatcher"
    }

    endpoint = f"{API}fulfillment/resubmit/bulk/{orgId}"

    response = requests.post(endpoint, json=requestData, timeout=15).json()

    for success in response.get('succeededResubmits'):
        res['SUCCESS'].append(success.get('packageId'))
    
    for error in response.get('failedResubmits'):
        res['ERROR'].append(error.get('packageId'))

    print(f">>>>> Batch Resubmit to {next_delivery_date} <<<<<\n> {len(res['SUCCESS'])} OK\n> {len(res['ERROR'])} FAILED")

    return response


def get_all_packages_on_route(env, orgId, routeId):
    """
    Retrieves all packages on a specific route.

    Args:
        env (str): The environment.
        orgId (str): The organization ID.
        routeId (str): The route ID.

    Returns:
        list: The list of packages on the route.
    """
    url = f"http://sortationservices.{env}.milezero.com/SortationServices-war/api/monitor/packages/{orgId}/{routeId}"

    print(f">> Searching for packages in {routeId}")

    response = requests.get(url=url, timeout=15).json()

    print(f"Found {len(response)} packages in {routeId}")

    return response

def get_all_packages_for_hub(env, orgId, hubName, date):
    """
    Retrieves all packages for a specific hub and date.

    Args:
        env (str): The environment.
        orgId (str): The organization ID.
        hubName (str): The hub name.
        date (str): The date.

    Returns:
        list: The list of package IDs for the hub and date.
    """
    endpoint = f"http://sortationservices.{env}.milezero.com/SortationServices-war/api/monitor/getPackagesInWave/{orgId}/{hubName}/{date}/true"

    packageCount = 0
    packageIDs = []

    try:
        packages = requests.get(url=endpoint, timeout=10).json()["packagesMap"]        
        
        for statusGroup in packages.keys():
            for package in packages[statusGroup]:
                packageId = package["externalPackageId"]
                packageIDs.append(packageId)

    except Exception as e:
        pass
    
    if packageCount > 0: 
        print(f"{len(packageIDs)} packages")
    
    return packageIDs