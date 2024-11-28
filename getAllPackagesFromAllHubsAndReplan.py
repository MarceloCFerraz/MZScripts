import os
from datetime import datetime

import requests

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
    },
}
ENV = "prod"
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
    "",
]

SUCCESSES = []
FAILS = []


def get_all_hubs():
    """
    Retrieves all hubs for the specified organization.

    This function sends a GET request to the Cromag API to retrieve all hubs associated with the organization ID. It returns a list of hubs.

    Parameters:
    - None

    Returns:
    - List of hubs
    """
    endpoint = f"http://cromag.{ENV}.milezero.com/retail/api/hubs/org/{ORGID}"

    return requests.get(url=endpoint, timeout=10).json()["hubs"]


def get_all_packages_for_hub(hubName, oldDate, status):
    """
    Retrieves all packages for a specific hub, date, and status.

    This function sends a GET request to the Sortation Services API to retrieve all packages in a wave for the specified organization ID, hub name, date, and status. It returns a list of valid package IDs based on the specified status.

    Parameters:
    - hubName: The name of the hub (string)
    - oldDate: The desired date (string)
    - status: The desired status of the packages (string)

    Returns:
    - List of valid package IDs
    """
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

    except Exception:
        pass

    if packageCount > 0:
        print(f"{len(validPackages)} (valid) / {packageCount} (total) packages")

    return validPackages


def resubmit_packages(packageId, newDate, notes):
    """
    Resubmits packages with a new date and notes.

    This function sends a POST request to the Switchboard API to resubmit a package with the specified package ID, new date, and notes. It handles the response and prints the success or failure message.

    Parameters:
    - packageId: The ID of the package to resubmit (string)
    - newDate: The new date for the package (string)
    - notes: Additional notes for the resubmission (string)

    Returns:
    - None
    """
    endpoint = f"https://switchboard.{ENV}.milezero.com/switchboard-war/api/fulfillment/resubmit/{ORGID}/{packageId}"

    payload = {
        "adjustTimeWindow": True,
        "treatEverydayAsProcessingDay": False,
        "targetLocalDate": newDate,
        "notes": notes,
    }

    response = requests.post(url=endpoint, json=payload, timeout=5).json()

    try:
        message = response["message"]
        print(f"(FAIL): \n{message}")
        FAILS.append(packageId + f" ({message})")
    except Exception:
        print(f"(OK {response['timeWindow']['start']})")
        SUCCESSES.append(packageId)



def divide_into_batches(lst, batch_size=100):
    """
    Divides a list into batches of a specified size.

    Args:
        lst (list): The list to divide.
        batch_size (int): The size of each batch. Defaults to 100.

    Returns:
        list: The list of batches.
    """
    batches = []
    for i in range(0, len(lst), batch_size):
        batch = lst[i : i + batch_size]
        batches.append(batch)
    return batches


def bulk_resubmit_packages(packageIDs, next_delivery_date, notes = ""):
    """
    Resubmits multiple packages in bulk for a specific delivery date.

    Args:
        packageIDs (list): The list of package IDs.
        next_delivery_date (str): The next delivery date.
        notes (str): A description to why packages are being resubmitted

    Returns:
        dict: The response containing the success and error information.
    """
    url = f"https://switchboard.{ENV}.milezero.com/switchboard-war/api/fulfillment/resubmit/bulk/{ORGID}"

    requestData = {
        "packageIds": packageIDs,
        "adjustTimeWindow": True,
        "treatEverydayAsProcessingDay": False,
        "targetLocalDate": next_delivery_date,
        "notes": notes,
    }

    response = requests.post(url=url, json=requestData, timeout=15).json()
    sCount = 0
    eCount = 0

    successes = response.get("succeededResubmits")
    errors = response.get("failedResubmits")

    if successes:
        sCount += len(successes)
        for success in successes:
            SUCCESSES.append(success.get("packageId"))

    if errors:
        eCount += len(errors)
        for error in errors:
            FAILS.append(error.get("packageId"))

    print(
        f">>>>> New Batch ({len(packageIDs)} {next_delivery_date}) <<<<<\n"
        + f"> {sCount} OK\t {eCount} FAILED"
    )

    return response


def create_dir(directoryName):
    """
    Creates a directory with the specified name.

    This function creates a directory with the specified name in the current file directory. It returns the path of the created directory.

    Parameters:
    - directoryName: The name of the directory (string)

    Returns:
    - Path of the created directory (string)
    """
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    currentDir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")
    # creates "RESULTS" folder directory
    newDir = currentDir + f"/{directoryName}"
    os.makedirs(newDir, exist_ok=True)

    return newDir


def create_file(directory, fileName, content):
    """
    Creates a file with the specified name and content in the specified directory.

    This function creates a file with the specified name and writes the content to the file in the specified directory. It handles any exceptions that occur during the file creation process and prints the result.

    Parameters:
    - directory: The directory where the file will be created (string)
    - fileName: The name of the file (string)
    - content: The content to write to the file (list of strings)

    Returns:
    - None
    """

    creationResult = f"Creating {fileName}... "
    fail = False

    with open(directory, "w") as file:
        for line in content:
            try:
                file.write(line + "\n")
            except Exception as e:
                creationResult += f"(FAIL)\n\n{e}"
                fail = True
        if not fail:
            print(f"File path:\n> {directory}")
            creationResult += "(OK)"

    # prints if the creationResult file was created or not
    print(creationResult)


def save_file(oldDate, newDate):
    """
    Saves the successes and fails to separate files.

    This function creates a directory named "RESULTS" and saves two separate files: one for the successes and one for the fails. The file names are based on the old date and new date. It calls the createFile() function to create the files.

    Parameters:
    - oldDate: The old date (string)
    - newDate: The new date (string)

    Returns:
    - None
    """
    oldDate = str(oldDate).replace("T16%3A00%3A00Z", "")
    directory = create_dir(directoryName="RESULTS")

    # names the file
    successesFileName = f"{oldDate}_{newDate}_SUCCESSES.txt"
    # complete directory and where the files will be saved
    successesDir = os.path.join(directory, successesFileName)
    # saving file
    create_file(directory=successesDir, fileName=successesFileName, content=SUCCESSES)

    # names the file
    failsFileName = f"{oldDate}_{newDate}_FAILS.txt"
    # complete directory and where the files will be saved
    failsDir = os.path.join(directory, failsFileName)
    # saving file
    create_file(directory=failsDir, fileName=failsFileName, content=FAILS)


def print_valid_statuses():
    """
    Prints the valid statuses.

    This function prints the valid statuses stored in the STATUSES list.

    Parameters:
    - None

    Returns:
    - None
    """
    for status in STATUSES:
        if status == "":
            print("''")
        else:
            print(status)


def get_invalid_hubs_count(hubs):
    """
    Retrieves the count of invalid hubs.

    This function takes a list of hubs and returns the count of hubs that have a non-numeric name.

    Parameters:
    - hubs: List of hubs

    Returns:
    - Count of invalid hubs (integer)
    """
    count = 0

    for hub in hubs:
        if not str(hub["name"]).isnumeric():
            count += 1

    return count


def get_valid_hubs(hubs):
    """
    Retrieves the list of valid hubs.

    This function takes a list of hubs and returns a new list containing only the hubs with a numeric name.

    Parameters:
    - hubs: List of hubs

    Returns:
    - List of valid hubs
    """
    validHubs = []

    for hub in hubs:
        if str(hub["name"]).isnumeric():
            validHubs.append(hub)

    return validHubs

def get_all_routes_for_hub(hubName: str, oldDates: [str]):
    routeIds = set()

    for date in oldDates:
        url = f"https://alamo.{ENV}.milezero.com/alamo-war/api/routes/search/matching/orgId/{ORGID}?key={hubName}&keyType=HUB_NAME&localDate={date}"

        response = requests.get(url=url)
        if response.status_code != 200:
            print(f"Something happened: {response.text}")
            continue
        
        routeIds = {r["metadata"]["routeId"] for r in response.json()["routes"]}

        for routeId in routeIds:
            routeIds.add(routeId)
    
    return list(routeIds)


def get_pkgs_from_alamo(routeId):
    url = f"http://alamo.{ENV}.milezero.com/alamo-war/api/plannedroutes/stopdetails/{routeId}"

    response = requests.get(url=url).json()
    # print(f">> Searching for packages in {routeId}")

    if response.get("routeStopDetail") is None:
        print(response.get("message"))
        return []

    stops = response["routeStopDetail"]["stops"]
    pids = set()

    for stop in stops:
        stopPackages = stop["stopPackages"]

        for pkgs in stopPackages:
            pid = pkgs.get("packageId")

            if pid is not None:
                print(f">>> {pid}")
                pids.add(pid)

    # print(f">> Found {len(pids)} packages\n")

    return list(pids)


def main():
    """
    This script aims to automate the complex process of capturing all packages from all hubs and replan them to a new date.

    User Input:
    - The Original Date (yyyy-mm-dd): The date for which packages will be searched.
    - The Packages' Status (optional): Only packages with matching status will be considered.
    - The New Date (yyyy-mm-dd): The new date to which the packages will be replanned.
    - Resubmit Notes (optional): A message to be displayed for future reference.

    Steps:
    1. Retrieve the list of all hubs.
    2. Calculate the count of valid and invalid hubs.
    3. Search for packages by iterating over the valid hubs.
    4. Store the retrieved packages in an array.
    5. If there are valid packages found:
        - Prompt the user for the new date and resubmit notes.
        - Resubmit the packages.
        - Keep track of successful and failed resubmits.
        - If the total number of resubmits is greater than 100, create separate files to save the resubmit results.
        - Otherwise, print the successful and failed resubmits.
    """
    print(
        "\n"
        "This script aims to automate the complex process of capturing all packages from all hubs and replan them to a new date.\n"
        + "This was inspired by the request #3280 (https://milezero.zendesk.com/agent/tickets/3280)\n"
        + "\n"
        + "What should you expect to input:\n"
        + "— The Original Date (only packages planned to this date will be searched)\n"
        + "— The Packages' Status (Optional. This will consider only packages that have matching status such as DELIVERED, CANCELLED and so on. A list of valid statuses will be listed and only a valid status will be accepted)\n"
        + "— The New Date (all valid the packages found in the previous date will be replanned)\n"
        + "— Resubmit Notes (Optional. A simple message that will be displayed if someone searches for this event later on. Good practices suggest — but is not limited to — including the action's requester and responsible for doing the action)\n"
    )

    today = datetime.now()
    newDate = datetime.min

    oldDates = list()

    while len(oldDates) < 2: # inform up to two dates (thu & fri)
        oldDate = datetime.strptime(
            input("Input the Original Date (yyyy-mm-dd): ").strip(), "%Y-%m-%d"
        )
        oldDate = oldDate.strftime("%Y-%m-%d")
        oldDates.append(oldDate)

    status = "a"
    print("Valid Statuses:")
    print_valid_statuses()
    while status not in STATUSES:
        status = str(input("Input the Package Status (optional): ")).upper().strip()

    hubs = get_all_hubs()

    hubsCount = len(hubs)
    invalidHubsCount = get_invalid_hubs_count(hubs)
    validHubsCount = hubsCount - invalidHubsCount

    print(
        f"{len(hubs)} hubs found ({validHubsCount} valid and {invalidHubsCount} invalid)"
    )
    print("Searching for packages...")

    packages = list()

    validHubs = get_valid_hubs(hubs)

    for hub in validHubs:
        hubName = hub["name"]
        print(f"> {hubName}")

        routes = get_all_routes_for_hub(hubName, oldDates)

        for routeId in routes:
            pkgIds = get_pkgs_from_alamo(routeId)
            
            for pkgId in pkgIds:
                packages.append(pkgId)

        # hubPackages = get_all_packages_for_hub(hubName, oldDate, status)

        # this needs to be done in order to add all packages from all hubs to the array
        # for package in hubPackages:
        #     packages.append(package)

    if len(packages) > 0:
        print(f"Total Valid Packages to be Replanned: {len(packages)}\n")

        while newDate < today:
            newDate = datetime.strptime(
                input("Input the New Date (yyyy-mm-dd. Later than today): ").strip(),
                "%Y-%m-%d",
            )
        newDate = newDate.strftime("%Y-%m-%d")

        notes = input("Type in the resubmit notes (optional): ").strip()

        print("\nResubmitting...")
        batches = divide_into_batches(packages)

        for batch in batches:
            bulk_resubmit_packages(batch, newDate, notes)
            # print(f"> {packageId}", end=" ")
            # resubmit_packages(packageId, newDate, notes)

        succeededResubmits = len(SUCCESSES)
        failedResubmits = len(FAILS)
        totalResubmits = succeededResubmits + failedResubmits

        if totalResubmits > 100:
            print("\nCreating files with resubmit results")
            save_file(oldDate=oldDate, newDate=newDate)
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
