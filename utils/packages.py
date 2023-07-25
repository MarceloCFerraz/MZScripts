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
    url = f"https://switchboard.{env}.milezero.com/switchboard-war/api/package/update/{orgId}/{packageId}/hub"
    
    payload = {
        "hubName": newHub,
        "notes": f"Requested by {dispatcher}. Executed by {userName}"
    }
    response = requests.post(url=url, json=payload, timeout=15)
    print(f"{response} {response.text['message'] if response.status_code >= 400 else ''}")


def move_packages_to_route(env, orgId, newRouteId, packageIdsList):
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
    API = "http://switchboard.prod.milezero.com/switchboard-war/api/"
    url = f"{API}package/update/{orgId}/{packageId}/DELIVERED/status"
    body = {
        "notes": "Requested by dispatcher"
    }
    print(f">>>>> Marking {packageId} as DELIVERED <<<<<")

    result = requests.post(url=url, json=body)

    print(f"{result.status_code} {result.text if result.status_code > 400 else ''}")


def get_packages_details(KEY_TYPE, key):
    API = "http://switchboard.prod.milezero.com/switchboard-war/api/"
    # f"{API}package/histories?keyValue={key}&keyType={keyType}"
    endpoint = f"{API}package?keyType={KEY_TYPE}&keyValue={key}&includeCancelledPackage=true"
    print(f">>>>> Retrieving Packages From {KEY_TYPE.upper()} {key} <<<<<")

    return requests.get(endpoint, timeout=5).json()



def get_packages_histories(keyType, key):
    API = "http://switchboard.prod.milezero.com/switchboard-war/api/"
    
    endpoint = f"{API}package/histories?keyValue={key}&keyType={keyType}"
    
    print(">>>>> Retrieving Packages From {} {} <<<<<".format(keyType.upper(), key))
    
    return requests.get(endpoint).json()


def print_package_details(package):
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


def revive_package(package):
    API = "http://switchboard.prod.milezero.com/switchboard-war/api/"
    orgId = package["orgId"]
    packageId = package["packageId"]
    requestData = {
        "notes": "Requested by dispatcher"
    }

    endpoint = "{}package/revive/{}/{}".format(API, orgId, packageId)

    print(">>>>> Reviving package <<<<<")

    response = requests.post(endpoint, json=requestData, timeout=15)
    print(response.status_code)


def mark_package_as_delivery_failed(package):
    API = "http://switchboard.prod.milezero.com/switchboard-war/api/"
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


def resubmit_package(package, next_delivery_date):
    errors = []
    successes = []
    API = "http://switchboard.prod.milezero.com/switchboard-war/api/"
    orgId = package["orgId"]
    packageId = package["packageId"]

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
        print("> Package Resubmitted Sucessfuly\n\n")
        successes.append(packageId)
    except Exception as e: 
        errors.append(packageId)
        print("> Package couldn't be resubmitted. See error bellow")
        print(e)

    return {
        "SUCCESSES": successes,
        "ERRORS": errors
    }


def get_all_packages_on_route(env, orgId, routeId):
    url = f"http://sortationservices.{env}.milezero.com/SortationServices-war/api/monitor/packages/{orgId}/{routeId}"

    print(f">> Searching for packages in {routeId}")

    return requests.get(url=url, timeout=15).json()
