from datetime import datetime
import requests
import sys

# CHANGE THIS FROM .prod. TO .stage. IF YOU WANT TO TEST THIS SCRIPT
API = "http://switchboard.prod.milezero.com/switchboard-war/api/"
STANDARD_TIMEOUT = 5 # seconds
SUCCESSES = []
ERRORS = []


#assumptions: all provided input barcodes will be from same hub
def dequeRoute(packages):
    if not packages:
        return
    hubLocationId = packages[0]["packageDetails"]["sourceLocation"]["locationId"]
    orgId = packages[0]["orgId"]

    print("Deque for org {} locationId {}".format(orgId, hubLocationId))
 
    response = requests.post("http://alamo.prod.milezero.com/alamo-war/api/constraints/{}/{}/dequeue".format(orgId, hubLocationId), json={})
    print(response.read())


def markDelivered(packageId):
    url = f"{API}package/update/3c897e84-3957-4958-b54d-d02c01b14f15/{packageId}/DELIVERED/status"

    result = requests.post(url=url, data={"notes": "Requested by dispatcher"}).json()

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


def replan(fileName, keyType, next_delivery_date):
    lines = getDataLines(fileName)
    
    print("Key Types: {}\n".format(keyType.upper())+
        "Keys: {}\n".format(lines))
    
    packages = []
    
    for line in lines:

        # getting packages from barcode present in file line
        packages = getPackages(keyType, line)["packageRecords"]

        if (len(packages) == 0):
            print("> NO PACKAGES FOUND <\n")
    
        for package in packages:

            status = package["packageStatuses"]["status"]
            packageID = package["packageId"]
            try:
                hubName = package["packageDetails"]["sourceLocation"]["name"]
            except:
                try:
                    hubName = package["packageDetails"]["clientHub"]
                except:
                    try:
                        hubName = package["packageDetails"]["destination"]["name"]
                    except Exception as e:
                        print(e)
                        sys.exit()

            print("----> PACKAGE ID: {}".format(packageID))
            print("--> STATUS: {}".format(status))
            print("--> HUB: {}\n".format(hubName))
            
            # if package is from the correct hub, continues.
            if hubName == fileName:
            
                # if package is marked as cancelled, 
                # revive the package
                if status == "CANCELLED":
                    revivePackage(package)
                
                # if package is marked as rejected or delivered,
                # change its status to DELIVERY_FAILED
                if status == "DELIVERED" or status == "REJECTED":
                    deliveryFailed(package)

                resubmitRequest(
                    package, 
                    next_delivery_date
                )
            else:
                print("---> Ignored because it isn't from hub {}\n".format(fileName))
    print("Successful Resubmits ({}/{}): ".format(len(SUCCESSES), len(SUCCESSES) + len(ERRORS)))
    for success in SUCCESSES:
        print("> {}".format(success))

    print("Unsuccessful Resubmits ({}/{}): ".format(len(ERRORS), len(SUCCESSES) + len(ERRORS)))
    for error in ERRORS:
        print("> {}".format(error))


# get command line argument
if (len(sys.argv) < 4):
    print(
        "\nNO ARGS PROVIDED!\n"+
        "Please, check the correct script usage bellow:\n\n"+
        "PRE REQUISITES:\n"+
        "> A file <hubName>.txt should be created in this same directory. You should paste the barcodes/ORIs to be replanned there\n"+
        "--> hubName: the hub that requested a replan in number format\n\n"+
        "SCRIPT USAGE:\n"+
        "--> python replanPackages.py <hubName> <keyType> <next_delivery_date>\n\n"+
        "-> Accepted keyTypes:\n"+
        "> pi (Package Id)\n"+
        "> tn (Tracking Number)\n"+
        "> ci (Container Id)\n"+
        "> bc (Shipment Barcode)\n"+
        "> oi (Order Id)\n"+
        "> ori (Order Reference Id)\n"+
        "> ji (Job Id)\n\n"
        "SCRIPT EXAMPLE:\n"+
        "--> python replanPackages.py 8506 bc 2023-04-06\n"+
        "> This will load all the barcodes on 8506.txt and replan only BARCODES from hub 8506 to 2023, April 6th\n\n"+
        "NOTES:\n"+
        "> Check comments on code to update relevant data such as keyType (bc, ori, etc), next_delivery_date (if dispatcher wants a specific date that is not the next day) accordingly to your needs\n"
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
# A date to do the replan must be provided with the yyyy-mm-dd format
next_delivery_date = datetime.strptime(sys.argv[3], "%Y-%m-%d")
next_delivery_date = next_delivery_date.strftime("%Y-%m-%d")
replan(fileName, keyType, next_delivery_date)
