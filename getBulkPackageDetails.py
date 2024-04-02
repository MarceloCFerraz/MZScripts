import concurrent.futures
import sys

import getPackageDetails
from utils import files, packages, utils

PACKAGES = []


def fill_packages_list(env, orgId, key_type, key):
    """
    Fill the PACKAGES list with package details.

    Parameters:
    - env: The environment.
    - orgId: The organization ID.
    - keyType: The type of key.
    - key: The key.

    Returns:
    None
    """
    pkgs = packages.get_packages_details(env, orgId, key_type, key)["packageRecords"]

    if len(pkgs) == 0:
        print("> NO PACKAGES FOUND <\n")
    for pkg in pkgs:
        PACKAGES.append(pkg)


def main(file_name, key_type, statuses):
    """
    Retrieves and processes package details.

    This function prompts the user to select the environment and organization ID. It then retrieves a list of status values based on the provided statuses parameter. Next, it reads a file containing keys and retrieves package details for each key. The function checks if the package status matches the provided status list. If it does, the package details are printed and added to the final response. The function also keeps track of the number of valid and invalid packages.

    Parameters:
    - file_name (str): The name of the file containing the keys.
    - key_type (str): The type of key.
        - "pi" (Package Id)
        - "tn" (Tracking Number)
        - "ci" (Container Id)
        - "bc" (Shipment Barcode)
        - "oi" (Order Id)
        - "ori" (Order Reference Id)
        - "ji" (Job Id)
    - statuses (str): A comma-separated string of statuses to filter the packages. If empty, all statuses are considered valid.

    Returns:
    - None
    """
    env = utils.select_env()
    orgId = utils.select_org(env)

    valid_statuses = []

    if statuses != "":
        valid_statuses = getPackageDetails.get_status_list(statuses)

    keys = files.get_data_from_file(file_name)
    response = {}
    valid_packages = []
    invalid_packages = []

    # Using multithreading to fetch multiple packages simultaneosly
    with concurrent.futures.ThreadPoolExecutor() as pool:
        for key in keys:
            # getting packages from key (ori, bc, etc) present in file line
            pool.submit(fill_packages_list, env, orgId, key_type, key)

    pool.shutdown(wait=True)

    for package in PACKAGES:
        status = package["packageStatuses"]["status"]

        if valid_statuses != [] and status not in valid_statuses:
            invalid_packages.append(package)
        else:
            if len(PACKAGES) > 10:
                packages.print_minimal_package_details(package)
                print(f"\nPackage added to final response ({status})\n\n")
                valid_packages.append(package)
            else:
                packages.print_package_details(package)

    response["packageRecords"] = valid_packages
    response["count"] = len(valid_packages)

    print(f"\nValid Packages: {len(valid_packages)}")
    print(f"Invalid Packages: {len(invalid_packages)}\n")
    for pkg in invalid_packages:
        packages.print_minimal_package_details(pkg)
        print()

    if valid_packages != [] and len(valid_packages) > 10:
        formatted_response = files.format_json(response)
        invalid_response = files.format_json(
            {"packageRecords": invalid_packages, "count": len(invalid_packages)}
        )

        files.save_json_to_file(formatted_response, "PKGS_DETAILS_VALID")
        files.save_json_to_file(invalid_response, "PKGS_DETAILS_INVALID")


if __name__ == "__main__":
    # get command line argument
    if len(sys.argv) < 3:
        print(
            "\nNO ARGS PROVIDED!\n"
            + "Please, check the correct script usage bellow:\n\n"
            + "PRE REQUISITES:\n"
            + "> A file <hubName>.txt should be created in this same directory.\n"
            + "You should paste the barcodes/ORIs to be replanned there\n"
            + "--> hubName: the hub that requested support\n\n"
            + "SCRIPT USAGE:\n"
            + "--> python getBulkPackageDetails.py <HUB_NAME> <key_type> (OPTIONAL) <statuses>\n\n"
            + "-> Accepted key_types:\n"
            + "\n".join(map(str, packages.VALID_KEY_TYPES))
            + "\n\n--> Valid Statuses:\n"
            + "\n".join(map(str, packages.VALID_STATUSES))
            + "\n\nSCRIPT EXAMPLE:\n"
            + "--> python getBulkPackageDetails.py 8506 bc 'cancelled delivered'\n"
            + "> This will load all the barcodes on 8506.txt, print the HTTP request for "
            + "each of them on a json file and console IF their status corresponds to"
            + " 'CANCELLED' or 'DELIVERED'.\n\n"
            + " If no filter status is informed, all statuses will be displayed\n\n"
            + "NOTES:\n"
            + "> Check comments on code to update relevant data such as key_type (bc, ori, etc)\n"
        )
        sys.exit(1)

    # The file name must be to the requester's hub name (e.g. 8506)
    file_name = sys.argv[1].replace(".txt", "").replace(".\\", "")
    key_type = sys.argv[2].lower()
    statuses = ""
    try:
        statuses = sys.argv[3]
    except Exception:
        pass
    main(file_name, key_type, statuses)
