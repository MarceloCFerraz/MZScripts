import os
import requests, sys, json
from datetime import datetime, timedelta


API = "http://switchboard.prod.milezero.com/switchboard-war/api/"


def getPackages(keyType, key):
    # 
    endpoint = f"{API}package/histories?keyValue={key}&keyType={keyType}"
    print(">>>>> Retrieving Packages From {} {} <<<<<".format(keyType.upper(), key)+
          "\n> {}".format(endpoint))
    return requests.get(endpoint).json()


def getKeysFromFile(fileName):
    file = open(fileName+".txt", "r")
    lines = file.readlines()
    file.close()

    results = []
    
    for line in lines:
        results.append(line.strip())

    # removing duplicates from list
    # this make the list unordered. Comment this line if
    # this impact your workflow somehow
    results = list(set(results))
    
    print("{} lines in file {}.txt\n".format(len(results), fileName))
    return results


def formatJson(packages):
    return json.dumps(packages, indent=2)


def saveJsonToFile(packages, hubName):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")
    # creates "Responses" folder directory
    response_dir = current_dir + "/Responses"
    os.makedirs(response_dir, exist_ok=True)
    
    # names the file
    FILE_NAME = f"{hubName}_HISTORIES.json"

    # this is the complete directory and where the file will be saved
    final_dir = os.path.join(response_dir, FILE_NAME)

    result = f"File {FILE_NAME} containing the complete response "

    with open(final_dir, "w") as json_file:
        try:
            json_file.write(str(packages))
            result += f"was created SUCCESSFULLY and can be accessed on ./Responses/{FILE_NAME}!"
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


def main(fileName, keyType):
    keys = getKeysFromFile(fileName)
    response = []
    formattedResponse = {}

    for key in keys:
        packages = getPackages(keyType=keyType, key=key)["histories"]

        if packages != []:
            for package in packages:
                printPackageHistories(package)
    
    formattedResponse["histories"] = packages
    formattedResponse = formatJson(formattedResponse)
    saveJsonToFile(packages=formattedResponse, hubName=fileName)


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
        
        "PRE REQUISITES:\n"+
        "> A file <hubName>.txt should be created in this same directory. You should paste the barcodes/ORIs to be replanned there\n"+
        "--> hubName: the hub that requested a replan in number format\n\n"+
        
        "SCRIPT USAGE:\n"+
        "--> python getBulkPackageHistories.py <hubName> <keyType>\n\n"+
        "-> Accepted keyTypes:\n"+
        "\n".join(map(str, valid_key_types))+
        
        "\n\nSCRIPT EXAMPLE:\n"+
        "--> python getBulkPackageHistories.py 8506 bc\n"+
        "> This will load all the barcodes on 8506.txt and print the "+
        "HTTP response for each of them on a json file\n\n"+
        
        "NOTES:\n"+
        "> Check comments on code to update relevant data such as keyType (bc, ori, etc), nextDeliveryDate (if dispatcher wants a specific date that is not the next day) accordingly to your needs\n"
    )
    sys.exit(1)

# The file name must be to the requester's hub name (e.g. 8506)
fileName = sys.argv[1].replace(".txt", "").replace(".\\", "")
# A KeyType arg must be provided. provide one of the following keyTypes:
# -> pi (Package Id)
# -> tn (Tracking Number)
# -> ci (Container Id)
# -> bc (Shipment Barcode)
# -> oi (Order Id)
# -> ori (Order Reference Id)
# -> ji (Job Id)
keyType = sys.argv[2].lower()
main(fileName, keyType)