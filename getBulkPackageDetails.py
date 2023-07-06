import os
import sys
import json
import requests


API = "http://switchboard.prod.milezero.com/switchboard-war/api/"


def getPackages(KEY_TYPE, key):
    # f"{API}package/histories?keyValue={key}&keyType={keyType}"
    endpoint = f"{API}package?keyType={KEY_TYPE}&keyValue={key}&includeCancelledPackage=true"
    print(f">>>>> Retrieving Packages From {KEY_TYPE.upper()} {key} <<<<<"+
          f"\n> {endpoint}")
    return requests.get(endpoint, timeout=5).json()


def getStatusList(STATUSES):
    status = ""
    status_list = []

    for char in STATUSES:
        if char != " ":
            status += char.upper()
        else:
            status_list.append(status)
            status = ""
    
    # to get the last status provided, since there aren't any spaces left
    status_list.append(status)

    return status_list

def getKeysFromFile(FILE_NAME):
    file = open(FILE_NAME+".txt", "r", encoding="utf-8")
    lines = file.readlines()
    file.close()

    results = []
    for line in lines:
        results.append(line.strip())

    # removing duplicates from list
    # this make the list unordered
    # add ".sort()" if it impact your workflow somehow
    results = list(set(results))

    print(f"{len(results)} lines in file {FILE_NAME}.txt\n")
    return results


def formatJson(packages):
    return json.dumps(packages, indent=2)


def saveJsonToFile(packages, file_name):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")
    # creates "Responses" folder directory
    response_dir = current_dir + "/Responses"
    os.makedirs(response_dir, exist_ok=True)
    
    # names the file
    FILE_NAME = f"{file_name}_DETAILS.json"

    # this is the complete directory and where the file will be saved
    final_dir = os.path.join(response_dir, FILE_NAME)

    result = f"File {FILE_NAME} containing the complete response "

    with open(final_dir, "w") as json_file:
        try:
            json_file.write(packages)
            result += f"was created SUCCESSFULLY and can be accessed on ./Responses/{FILE_NAME}!"
        except Exception as e:
            result += f"COULD NOT be created. See exception bellow:\n\n{e}"

    print(result)


def printPackageDetails(package):
    packageID = package["packageId"]
    orgId = package["orgId"]
    hubId = package["hubId"]
    ori = package["orderDetails"]["orderReferenceId"]            
    hubName = package["packageDetails"]["sourceLocation"]["name"]
    barcode = package["packageDetails"]["shipmentBarcode"]
    routeId = package["planningDetails"]["plannerRouteId"]
    previousRouteId = package["planningDetails"]["originalRouteId"]
    routeName = package["planningDetails"]["plannerRouteName"]
    deliveryWindow = package["planningDetails"]["requestedTimeWindow"]["start"] + " - " + package["planningDetails"]["requestedTimeWindow"]["end"]
    status = package["packageStatuses"]["status"]
    picked = bool(package["packageStatuses"]["deliveryFlags"]["pickedUp"])

    half_divisor = "==================="

    print(f"\n{half_divisor} PACKAGE {half_divisor}")
    print(f"Package ID: {packageID}")
    print(f"Scannable Barcode: {barcode}")
    print(f"Order Reference ID: {ori}")
    print(f"Picked Up? {'YES' if picked else 'NO'}")
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


def main(FILE_NAME, KEY_TYPE, STATUSES):
    status_list = []
    
    if STATUSES != "":
        status_list = getStatusList(STATUSES)
    
    keys = getKeysFromFile(FILE_NAME)
    response = {}
    valid_packages = []
    invalid_packages = 0

    for key in keys:
        packages = getPackages(KEY_TYPE=KEY_TYPE, key=key)["packageRecords"]
        for package in packages:
            status = package["packageStatuses"]["status"]

            if status_list != [] and status not in status_list:
                print(f"Package ignored (not marked as {', '.join(status_list)})")
                invalid_packages += 1
            else:
                printPackageDetails(package)
                print(f"Package added to final response ({status})")
                valid_packages.append(package)
    
    response["packageRecords"] = valid_packages
    response["count"] = len(valid_packages)

    print(f"\nValid Packages: {len(valid_packages)}")
    print(f"Invalid Packages: {invalid_packages}\n")

    if valid_packages != []:
        formatted_response = formatJson(response)
        saveJsonToFile(packages=formatted_response, file_name=FILE_NAME)


valid_statuses = [
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
valid_key_types = [
    "pi (Package Id)",
    "tn (Tracking Number)",
    "ci (Container Id)",
    "bc (Shipment Barcode)",
    "oi (Order Id)",
    "ori (Order Reference Id)",
    "ji (Job Id)"
]
# get command line argument
if len(sys.argv) < 3:
    print(
        "\nNO ARGS PROVIDED!\n"+
        "Please, check the correct script usage bellow:\n\n"+

        "PRE REQUISITES:\n"+
        "> A file <hubName>.txt should be created in this same directory.\n"+
        "You should paste the barcodes/ORIs to be replanned there\n"+
        "--> hubName: the hub that requested support\n\n"+

        "SCRIPT USAGE:\n"+
        "--> python getBulkPackageDetails.py <HUB_NAME> <KEY_TYPE> (OPTIONAL) <STATUSES>\n\n"+

        "-> Accepted KEY_TYPEs:\n"+
        "\n".join(map(str, valid_key_types))+

        "\n\n--> Valid Statuses:\n"+
        "\n".join(map(str, valid_statuses))+

        "\n\nSCRIPT EXAMPLE:\n"+
        "--> python getBulkPackageDetails.py 8506 bc 'cancelled delivered'\n"+
        "> This will load all the barcodes on 8506.txt, print the HTTP request for "+
        "each of them on a json file and console IF their status corresponds to"+
        " 'CANCELLED' or 'DELIVERED'.\n\n"+
        
        " If no filter status is informed, all statuses will be displayed\n\n"+

        "NOTES:\n"+
        "> Check comments on code to update relevant data such as KEY_TYPE (bc, ori, etc)\n"
    )
    sys.exit(1)

# The file name must be to the requester's hub name (e.g. 8506)
FILE_NAME = sys.argv[1].replace(".txt", "").replace(".\\", "")
KEY_TYPE = sys.argv[2].lower()
STATUSES = ""
try:
    STATUSES = sys.argv[3]
except Exception as e:
    pass
main(FILE_NAME, KEY_TYPE, STATUSES)
