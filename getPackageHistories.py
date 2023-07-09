import os
import requests, sys, json
from datetime import datetime, timedelta


API = "http://switchboard.prod.milezero.com/switchboard-war/api/"


def getPackages(KEY_TYPE, KEY):
    # 
    endpoint = f"{API}package/histories?keyValue={KEY}&keyType={KEY_TYPE}"
    print(">>>>> Retrieving Packages From {} {} <<<<<".format(KEY_TYPE.upper(), KEY)+
          "\n> {}".format(endpoint))
    return requests.get(endpoint).json()


def formatJson(packages):
    return json.dumps(packages, indent=2)


def saveJsonToFile(packages, key):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")
    # creates "RESULTS" folder directory
    response_dir = current_dir + "/RESULTS"
    os.makedirs(response_dir, exist_ok=True)
    
    # names the file
    FILE_NAME = f"{key}_HISTORIES.json"

    # this is the complete directory and where the file will be saved
    final_dir = os.path.join(response_dir, FILE_NAME)

    result = f"File {FILE_NAME} containing the complete response "

    with open(final_dir, "w") as json_file:
        try:
            json_file.write(packages)
            result += f"was created SUCCESSFULLY and can be accessed on ./RESULTS/{FILE_NAME}!"
        except Exception as e:
            result += f"COULD NOT be created. See exception bellow:\n\n{e}"

    print(result)


def printPackageHistories(package):
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


def main(KEY, KEY_TYPE):
    response = {}
    packages = getPackages(KEY_TYPE=KEY_TYPE, KEY=KEY)["histories"]

    if packages != []:
        for package in packages:
            printPackageHistories(package)
    
    formattedResponse = formatJson(response)
    saveJsonToFile(packages=formattedResponse, key=KEY)


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
if (len(sys.argv) < 3):
    print(
        "\nNO ARGS PROVIDED!\n"+
        "Please, check the correct script usage bellow:\n\n"+
        
        "SCRIPT USAGE:\n"+
        "--> python getPackageHistories.py <KEY> <KEY_TYPE>\n\n"+
        "-> Accepted keyTypes:\n"+
        "\n".join(map(str, valid_key_types))+
        
        "\n\nSCRIPT EXAMPLE:\n"+
        "--> python getBulkPackageHistories.py 8506 bc\n"+
        "> This will load all the barcodes on 8506.txt and print the "+
        "HTTP response for each of them on a json file\n\n"+
        
        "NOTES:\n"+
        "> Check comments on code to update relevant data such as KEY_TYPE (bc, ori, etc), nextDeliveryDate (if dispatcher wants a specific date that is not the next day) accordingly to your needs\n"
    )
    sys.exit(1)

# The file name must be to the requester's hub name (e.g. 8506)
KEY = sys.argv[1].replace(".txt", "").replace(".\\", "")
# A KeyType arg must be provided. provide one of the following keyTypes:
# -> pi (Package Id)
# -> tn (Tracking Number)
# -> ci (Container Id)
# -> bc (Shipment Barcode)
# -> oi (Order Id)
# -> ori (Order Reference Id)
# -> ji (Job Id)
KEY_TYPE = sys.argv[2].lower()
main(KEY, KEY_TYPE)