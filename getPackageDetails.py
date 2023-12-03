from datetime import datetime
import os
import sys
from utils import files, packages, utils


def get_status_list(STATUSES):
    """
    Extracts a list of statuses from a string of space-separated statuses.

    Parameters:
    STATUSES (str): A string of space-separated statuses.

    Returns:
    list: A list of extracted statuses.
    """
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


def main(KEY, KEY_TYPE, STATUSES):
    """
    Retrieves and processes package details.

    This function prompts the user to select the environment and organization ID. It then retrieves a list of status values based on the provided STATUSES parameter. Next, it reads a file containing keys and retrieves package details for each key. The function checks if the package status matches the provided status list. If it does, the package details are printed and added to the final response. The function also keeps track of the number of valid and invalid packages.

    Parameters:
    KEY (str): The key value corresponding to the specified key type.
    KEY_TYPE (str): The type of key used for package retrieval. Valid options include:
        - "pi" (Package Id)
        - "tn" (Tracking Number)
        - "ci" (Container Id)
        - "bc" (Shipment Barcode)
        - "oi" (Order Id)
        - "ori" (Order Reference Id)
        - "ji" (Job Id)
    STATUSES (str): A string of space-separated statuses to filter the packages.

    Returns:
    None
    """
    env = utils.select_env()
    orgId = utils.select_org(env)

    status_list = []
    
    if STATUSES != "":
        status_list = get_status_list(STATUSES)
    
    response = {}
    valid_packages = []
    invalid_packages = 0

    pkgs = packages.get_packages_details(env, orgId, KEY_TYPE, KEY)["packageRecords"]
    for package in pkgs:
        status = package["packageStatuses"]["status"]

        if status_list != [] and status not in status_list:
            print(f"Package ignored (not marked as {', '.join(status_list)})")
            invalid_packages += 1
        else:
            packages.print_package_details(package)
            print(f"Package added to final response ({status})")
            valid_packages.append(package)
    
    response["packageRecords"] = valid_packages
    response["count"] = len(valid_packages)

    print(f"\nValid Packages: {len(valid_packages)}")
    print(f"Invalid Packages: {invalid_packages}\n")

    if valid_packages != []:
        formatted_response = files.format_json(response)
        files.save_json_to_file(formatted_response, "PKG_DETAILS")

# get command line argument
if len(sys.argv) < 3:
    print(
        "\nNO ARGS PROVIDED!\n"+
        "Please, check the correct script usage bellow:\n\n"+

        "SCRIPT USAGE:\n"+
        "--> python getPackageDetails.py <KEY> <KEY_TYPE> (OPTIONAL) <STATUSES>\n\n"+

        "-> Accepted KEY_TYPEs:\n"+
        "\n".join(map(str, packages.VALID_KEY_TYPES))+

        "\n\n--> Valid Statuses:\n"+
        "\n".join(map(str, packages.VALID_STATUSES))+

        "\n\nSCRIPT EXAMPLE:\n"+
        "--> python getPackageDetails.py 8506 bc 'cancelled delivered'\n"+
        "> This will load all the barcodes on 8506.txt, print the HTTP request for "+
        "each of them on a json file and console IF their status corresponds to"+
        " 'CANCELLED' or 'DELIVERED'.\n\n"+
        
        " If no filter status is informed, all statuses will be displayed\n\n"+

        "NOTES:\n"+
        "> Check comments on code to update relevant data such as KEY_TYPE (bc, ori, etc)\n"
    )
    sys.exit(1)


if __name__ == "__main__":
    # The file name must be to the requester's hub name (e.g. 8506)
    KEY = sys.argv[1].replace(".txt", "").replace(".\\", "")
    KEY_TYPE = sys.argv[2].lower()
    STATUSES = ""
    try:
        STATUSES = sys.argv[3]
    except Exception as e:
        pass
    main(KEY, KEY_TYPE, STATUSES)
