import os
from datetime import datetime

import requests

import getRoutePackages
from utils import hubs, routes, utils

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


def get_all_hubs(env, orgId):
    """
    Retrieves all hubs for the specified organization.

    This function sends a GET request to the Cromag API to retrieve all hubs associated with the organization ID. It returns a list of hubs.

    Parameters:
    - None

    Returns:
    - List of hubs
    """
    endpoint = f"http://cromag.{utils.convert_env(env)}.milezero.com/retail/api/hubs/org/{orgId}"

    return requests.get(url=endpoint, timeout=10).json()["hubs"]


def get_all_packages_for_hub(env, orgId, hubName, oldDate, status):
    """
    Retrieves all packages for a specific hub, date, and status.

    This function sends a GET request to the Sortation Services API to retrieve all packages in a wave for the specified organization ID, hub name, date, and status. It returns a list of package IDs that does have the status defined in `status`.

    Parameters:
    - hubName: The name of the hub (string)
    - oldDate: The desired date (string)
    - status: The desired status of the packages (string)

    Returns:
    - List of valid package IDs
    """
    all_routes = routes.get_all_routes_from_hub_alamo(env, orgId, hubName, oldDate)[
        "routes"
    ]
    valid_packages = set()

    route_pkgs = getRoutePackages.main(
        env, orgId, [r["metadata"]["routeId"] for r in all_routes]
    )
    for route in route_pkgs:
        pkgs = route_pkgs[route]
        for pkg in pkgs:
            print(pkg)
            valid_packages.add(pkg)

    return valid_packages


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


def save_file(hubName, oldDate):
    """
    Saves the successes and fails to separate files.

    This function creates a directory named "RESULTS" and saves two separate files: one for the successes and one for the fails. The file names are based on the old date and new date. It calls the createFile() function to create the files.

    Parameters:
    - oldDate: The old date (string)
    - newDate: The new date (string)

    Returns:
    - None
    """
    oldDate = str(oldDate.strftime("%Y-%m-%d")).replace("T16%3A00%3A00Z", "")
    directory = create_dir(directoryName="RESULTS")

    # names the file
    successesFileName = f"{hubName}_{oldDate}_PACKAGES.txt"
    # complete directory and where the files will be saved
    successesDir = os.path.join(directory, successesFileName)
    # saving file
    create_file(directory=successesDir, fileName=successesFileName, content=SUCCESSES)


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
    env = utils.select_env()
    orgId = utils.select_org(env)

    oldDate = datetime.strptime(
        input("Input the Original Date (yyyy-mm-dd): ").strip(), "%Y-%m-%d"
    )
    oldDateCpt = oldDate.strftime("%Y-%m-%d")

    status = "a"

    print_valid_statuses()
    while status not in STATUSES:
        status = str(input("Input the Package Status (optional): ")).upper().strip()

    for hubName in [
        input(">> Type the Hub Name: "),
    ]:
        print(f"Working on {hubName}")
        # hub = hubs.search_hub_by_name(env, orgId, input(">> Type the Hub Name: "))
        hub = hubs.search_hub_by_name(env, orgId, hubName)

        if hub:
            hub = hub[0]

            print("Searching for packages...")

            hubName = hub["name"]
            SUCCESSES = get_all_packages_for_hub(
                env, orgId, hubName, oldDateCpt, status
            )

            if len(SUCCESSES) > 0:
                print("\nCreating files with results")
                save_file(hubName=hubName, oldDate=oldDate)
            else:
                print("No packages found")
        else:
            print("HUB NOT FOUND!")


if __name__ == "__main__":
    main()
