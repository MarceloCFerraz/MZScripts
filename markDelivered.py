from datetime import datetime
import requests
import sys

# CHANGE THIS FROM .prod. TO .stage. IF YOU WANT TO TEST THIS SCRIPT
API = "http://switchboard.prod.milezero.com/switchboard-war/api/"
STANDARD_TIMEOUT = 5 # seconds
SUCCESSES = []
ERRORS = []
ORGS = { # this is not used by the script
    "PROD": {
        "STAPLES": "3c897e84-3957-4958-b54d-d02c01b14f15",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "ca3ffc06-b583-409f-a249-bdd014e21e31",
        "CUB": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "CUBPHARMA": "706660ca-71f6-4c01-a9ff-3a480acebaf4",
        "SHOPRITE": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        "LOWES": "8c381810-baf7-4ebe-a5f2-13c28b1ec7a4",
    },
    "STAGE": {
        "STAPLES": "3e59b207-cea5-4b00-8035-eed1ae26e566",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "4a00ea0a-ebe2-4a77-8631-800e0daa50c5",
        "CUB": "12d035f7-16c7-4c02-9b38-f1212b6f92f3",
        "CUBPHARMA": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "SHOPRITE": "397190aa-18ab-4bef-a8aa-d5875d738911",
        "LOWES": "",
    }
}


#assumptions: all provided input barcodes will be from same hub
def dequeRoute(packages):
    if not packages:
        return
    hubLocationId = packages[0]["packageDetails"]["sourceLocation"]["locationId"]
    orgId = packages[0]["orgId"]

    print("Deque for org {} locationId {}".format(orgId, hubLocationId))
 
    response = requests.post("http://alamo.prod.milezero.com/alamo-war/api/constraints/{}/{}/dequeue".format(orgId, hubLocationId), json={})
    print(response.read())


def markDelivered(orgId, packageId):
    url = f"{API}package/update/{orgId}/{packageId}/DELIVERED/status"
    body = {
        "notes": "Requested by dispatcher"
    }

    result = requests.post(url=url, json=body)

    print(result)

def getPackages(keyType, key):
    endpoint = "{}package?keyType={}&keyValue={}&includeCancelledPackage=true".format(API, keyType, key)
    print(">>>>> Retrieving Packages From {} {} <<<<<".format(keyType.upper(), key)+
          "\n> {}".format(endpoint))
    return requests.get(endpoint, timeout=STANDARD_TIMEOUT).json()


def revivePackage(package):
    orgId = package["orgId"]
    packageId = package["packageId"]
    requestData = {
        "notes": "Requested by dispatcher"
    }

    endpoint = "{}package/revive/{}/{}".format(API, orgId, packageId)

    print(">>>>> Reviving package <<<<<"+
          "\n> {}".format(endpoint))

    response = requests.post(endpoint, json=requestData, timeout=STANDARD_TIMEOUT)
    print(response.status_code)


def deliveryFailed(package):
    orgId = package["orgId"]
    packageId = package["packageId"]

    requestData = {
        "notes": "Requested By Dispatcher"
    }

    endpoint = "{}package/update/{}/{}/DELIVERY_FAILED/status".format(API, orgId, packageId)

    print(">>>>> Marking package as DELIVERY_FAILED <<<<<")
    
    try:
        response = requests.post(endpoint, json=requestData, timeout=STANDARD_TIMEOUT)
        print("> Package Marked as DELIVERY_FAILED Sucessfuly ({})\n".format(response))
    except Exception as e:
        print("> Package couldn't be marked as DELIVERY_FAILED. See error bellow")
        print(e)

def resubmitRequest(package, next_delivery_date):
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
        response = requests.post(endpoint, json=requestData, timeout=STANDARD_TIMEOUT).json()
        print("> Package Resubmitted Sucessfuly\n\n")
        SUCCESSES.append(packageId)
    except Exception as e: 
        ERRORS.append(packageId)
        print("> Package couldn't be resubmitted. See error bellow")
        print(e)


def getDataLines(fileName):
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
    
    print("{} lines in file {}\n".format(len(results), fileName))
    return results


def main(fileName, keyType):
    lines = getDataLines(fileName)
    
    print("Key Types: {}\n".format(keyType.upper())+
        "Keys: \n".format(lines)+
        "\n".join(map(str, lines))+"\n")
    
    packages = []
    
    for line in lines:

        # getting packages from barcode present in file line
        packages = getPackages(keyType, line)["packageRecords"]

        if (len(packages) == 0):
            print("> NO PACKAGES FOUND <\n")
    
        for package in packages:

            orgId = package["orgId"]
            provider = str(package["providerDetails"]["providerName"]).upper()
            status = package["packageStatuses"]["status"]
            packageID = package["packageId"]
            hubName = package["packageDetails"]["sourceLocation"]["name"]


            if status != "DELIVERED":
                print(f"----> PACKAGE ID: {packageID} (OK)")
                print(f"--> PROVIDER: {provider}")
                print(f"--> STATUS: {status}\n")
                print(f"--> HUB: {hubName}")

                markDelivered(orgId, packageID)
            else:
                print(f"\n----> PACKAGE ID: {packageID} (Ignored - already DELIVERED)\n")



# get command line argument
if (len(sys.argv) < 3):
    print(
        "Please, check the correct script usage bellow:\n\n"+
        "PRE REQUISITES:\n"+
        "> A file <file>.txt should be created in this same directory. You should paste the barcodes/ORIs/PIs/etc there\n"+
        "SCRIPT USAGE:\n"+
        "--> python markDelivered.py <fileName> <keyType>\n\n"+
        "-> Accepted keyTypes:\n"+
        "> pi (Package Id)\n"+
        "> tn (Tracking Number)\n"+
        "> ci (Container Id)\n"+
        "> bc (Shipment Barcode)\n"+
        "> oi (Order Id)\n"+
        "> ori (Order Reference Id)\n"+
        "> ji (Job Id)\n\n"
        "SCRIPT EXAMPLE:\n"+
        "--> python replanPackages.py 8506 bc\n"+
        "> This will load all the barcodes on 8506.txt and mark delivered packages that are not already delivered\n\n"+
        "NOTES:\n"+
        "> Check comments on code to update relevant data such as keyType (bc, ori, etc), ORG Environment accordingly to your needs\n"
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
