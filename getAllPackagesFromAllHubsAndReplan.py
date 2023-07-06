import os
import requests
from datetime import datetime

ORGS = {
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
ENV = "stage"
ORGID = ORGS[ENV.upper()]["STAPLES"]

STATUSES = [
    "CANCELLED",
    "CREATED",
    "DAMAGED",
    "DELETED",
    "DELIVERED",
    "DELIVERY_FAILED",
    "OUT_FOR_DELIVERY",
    "PACKED",
    "PICKUP_FAILED",
    "REJECTED",
    "RETURN_PICKED_UP",
    "RETURN_PICKUP_FAILED",
    "RE_PLANNED",
    "RE_SCHEDULED",
    "RE_SUBMITTED",
    "SC_SHORT",
    ""
]

SUCCESSES = []
FAILS = []


def getAllHubs():
    endpoint = f"http://cromag.{ENV}.milezero.com/retail/api/hubs/org/{ORGID}"

    return requests.get(url=endpoint, timeout=10).json()["hubs"]


def getAllPackagesForHub(hubName, oldDate, status):
    endpoint = f"http://sortationservices.{ENV}.milezero.com/SortationServices-war/api/monitor/getPackagesInWave/{ORGID}/{hubName}/{oldDate}/true"

    packageCount = 0
    validPackages = []

    try:
        packages = requests.get(url=endpoint, timeout=10).json()["packagesMap"]        
        
        for statusGroup in packages.keys():
            packageCount += len(packages[statusGroup])
            # sortation services groups packages by status
            if status == "" or statusGroup == status:
                for package in packages[statusGroup]:
                    packageId = package["externalPackageId"]
                    validPackages.append(packageId)

    except Exception as e:
        pass
    
    if packageCount > 0: 
        print(f"{len(validPackages)} (valid) / {packageCount} (total) packages")
    
    return validPackages


def resubmitPackages(packageId, newDate, notes):
    endpoint = f"https://switchboard.{ENV}.milezero.com/switchboard-war/api/fulfillment/resubmit/{ORGID}/{packageId}"

    payload = {
        "adjustTimeWindow": True,
        "treatEverydayAsProcessingDay": False,
        "targetLocalDate": newDate,
        "notes": notes
    }

    response = requests.post(url=endpoint, json=payload, timeout=5).json()

    try:
        message = response["message"]
        print(f"(FAIL): \n{message}")
        FAILS.append(packageId + f" ({message})")
    except Exception as e:
        print(f"(OK {response['timeWindow']['start']})")
        SUCCESSES.append(packageId)


def createDirectory(directoryName):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    currentDir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")
    # creates "RESULTS" folder directory
    newDir = currentDir + f"/{directoryName}"
    os.makedirs(newDir, exist_ok=True)

    return newDir


def createFile(directory, fileName, content):

    creationResult = f"Creating file... "
    fail = False

    with open(directory, "w") as file:
        for line in content:
            try:
                file.write(line + "\n")
            except Exception as e:
                fail = True
        if fail:
            creationResult += f"(FAIL)\n\n{e}"
        else:
            print(f"File path:\n> {directory}")
            creationResult += f"(OK)"

    # prints if the creationResult file was created or not
    print(creationResult)


def saveFile(oldDate, newDate):
    oldDate = str(oldDate).replace('T16%3A00%3A00Z', '')
    directory = createDirectory(directoryName="RESULTS")
    
    # names the file
    successesFileName = f"{oldDate}_{newDate}_SUCCESSES.txt"
    # complete directory and where the files will be saved
    successesDir = os.path.join(directory, successesFileName)
    # saving file
    createFile(directory=successesDir, fileName=successesFileName, content=SUCCESSES)

    # names the file
    failsFileName = f"{oldDate}_{newDate}_FAILS.txt"
    # complete directory and where the files will be saved
    failsDir = os.path.join(directory, failsFileName)
    # saving file
    createFile(directory=failsDir, fileName=failsFileName, content=FAILS)


def printValidStatuses():
    for status in STATUSES:
        if status == "":
            print("''")
        else:
            print(status)
    

def getInvalidHubsCount(hubs):
    count = 0

    for hub in hubs:
        if not str(hub["name"]).isnumeric():
            count += 1

    return count


def getValidHubs(hubs):
    validHubs = []

    for hub in hubs:
        if str(hub["name"]).isnumeric():
            validHubs.append(hub)
    
    return validHubs


def main():
    print(
        "\n"
        "This script aims to automate the complex process of capturing all packages from all hubs and replan them to a new date.\n"+
        "This was inspired by the request #3280 (https://milezero.zendesk.com/agent/tickets/3280)\n"+
        "\n"+
        "What should you expect to input:\n"+
        "— The Original Date (only packages planned to this date will be searched)\n"+
        "— The Packages' Status (Optional. This will consider only packages that have matching status such as DELIVERED, CANCELLED and so on. A list of valid statuses will be listed and only a valid status will be accepted)\n"+
        "— The New Date (all valid the packages found in the previous date will be replanned)\n"+
        "— Resubmit Notes (Optional. A simple message that will be displayed if someone searches for this event later on. Good practices suggest — but is not limited to — including the action's requester and responsible for doing the action)\n"
    )

    today = datetime.now()
    newDate = datetime.min

    oldDate = datetime.strptime(
        input("Input the Original Date (yyyy-mm-dd): ").strip(), 
        "%Y-%m-%d"
    )
    oldDate = oldDate.strftime("%Y-%m-%d")
    oldDate = str(oldDate + "T16:00:00Z")
    oldDate = oldDate.replace(":", "%3A")

    status = "a"
    print(f"Valid Statuses:")
    printValidStatuses()
    while status not in STATUSES:
        status = str(input("Input the Package Status (optional): ")).upper().strip()

    hubs = getAllHubs()

    hubsCount = len(hubs)
    invalidHubsCount = getInvalidHubsCount(hubs)
    validHubsCount = hubsCount - invalidHubsCount

    print(f"{len(hubs)} hubs found ({validHubsCount} valid and {invalidHubsCount} invalid)")
    print("Searching for packages...")

    packages = []

    for hub in getValidHubs(hubs):
        hubName = hub["name"]
        print(f"> {hubName}")

        hubPackages = getAllPackagesForHub(hubName, oldDate, status)
        
        # this needs to be done in order to add all packages from all hubs to the array
        for package in hubPackages:
            packages.append(package)

    if len(packages) > 0:
        print(f"Total Valid Packages to be Replanned: {len(packages)}\n")

        while newDate < today:
            newDate = datetime.strptime(
                input("Input the New Date (yyyy-mm-dd. Later than today): ").strip(), 
                "%Y-%m-%d"
            )
        newDate = newDate.strftime("%Y-%m-%d")

        notes = input("Type in the resubmit notes (optional): ").strip()

        print("\nResubmitting...")
        for packageId in packages:
            print(f"> {packageId}", end=" ")
            resubmitPackages(packageId, newDate, notes)

        succeededResubmits = len(SUCCESSES)
        failedResubmits = len(FAILS)
        totalResubmits = succeededResubmits + failedResubmits

        if totalResubmits > 100:
            print("\nCreating files with resubmit results")
            saveFile(oldDate=oldDate, newDate=newDate)
        else:
            print(f"\n({succeededResubmits}/{totalResubmits}) SUCCESSFUL resubmits:")
            for resubmit in SUCCESSES:
                print(f"> {resubmit}")

            print(f"({failedResubmits}/{totalResubmits}) FAILED resubmits:")
            for resubmit in FAILS:
                print(f"> {resubmit}")
    else:
        print("0 Packages found. Finishing script")


main()
