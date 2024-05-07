import concurrent.futures
import sys

from utils import files, packages, utils

PACKAGES = []


def fill_packages_list(env, orgId, key_type, key):
    """
    Fill the PACKAGES list with package details.

    Parameters:
    - env: The environment.
    - orgId: The organization ID.
    - key_type: The type of key.
    - key: The key.

    Returns:
    None
    """
    pkgs = packages.get_package_histories(env, orgId, key_type, key)["histories"]

    if len(pkgs) == 0:
        print("> NO PACKAGES FOUND <\n")
    for pkg in pkgs:
        PACKAGES.append(pkg)


def main(file_name, key_type):
    """
    The main function for retrieving package histories.

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

    Returns:
    None
    """
    env = utils.select_env()
    orgId = utils.select_org(env)
    keys = files.get_data_from_file(file_name)
    response = {}
    valid_packages = []
    invalid_packages = 0

    # Using multithreading to fetch multiple packages simultaneosly
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        for key in keys:
            # getting packages from key (ori, bc, etc) present in file line
            pool.submit(fill_packages_list, env, orgId, key_type, key)

    pool.shutdown(wait=True)

    print(f"Gathered {len(PACKAGES)} packages")

    for package in PACKAGES:
        # packages.print_package_histories(package)
        # print(f"\nPackage added to final response ({status})\n\n")
        valid_packages.append(package)

    response["histories"] = valid_packages
    response["count"] = len(valid_packages)

    print(f"\nValid Packages: {len(valid_packages)}")
    print(f"Invalid Packages: {invalid_packages}\n")

    if valid_packages != [] and len(valid_packages) > 20:
        formatted_response = files.format_json(response)
        files.save_json_to_file(formatted_response, "PKGS_HISTORIES")


# get command line argument
if len(sys.argv) < 3:
    print(
        "\nNO ARGS PROVIDED!\n"
        + "Please, check the correct script usage bellow:\n\n"
        + "PRE REQUISITES:\n"
        + "> A file <hubName>.txt should be created in this same directory. You should paste the barcodes/ORIs to be replanned there\n"
        + "--> hubName: the hub that requested a replan in number format\n\n"
        + "SCRIPT USAGE:\n"
        + "--> python getBulkPackageHistories.py <hubName> <key_type>\n\n"
        + "-> Accepted key_types:\n"
        + "\n".join(map(str, packages.VALID_KEY_TYPES))
        + "\n\nSCRIPT EXAMPLE:\n"
        + "--> python getBulkPackageHistories.py 8506 bc\n"
        + "> This will load all the barcodes on 8506.txt and print the "
        + "HTTP response for each of them on a json file\n\n"
        + "NOTES:\n"
        + "> Check comments on code to update relevant data such as key_type (bc, ori, etc), nextDeliveryDate (if dispatcher wants a specific date that is not the next day) accordingly to your needs\n"
    )
    sys.exit(1)

# The file name must be to the requester's hub name (e.g. 8506)
file_name = sys.argv[1].replace(".txt", "").replace(".\\", "")
# A key_type arg must be provided. provide one of the following key_types:
# -> pi (Package Id)
# -> tn (Tracking Number)
# -> ci (Container Id)
# -> bc (Shipment Barcode)
# -> oi (Order Id)
# -> ori (Order Reference Id)
# -> ji (Job Id)
key_type = sys.argv[2].lower()
main(file_name, key_type)
