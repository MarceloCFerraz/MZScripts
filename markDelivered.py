import sys
from concurrent.futures import ThreadPoolExecutor

from utils import files, packages, utils

STANDARD_TIMEOUT = 5  # seconds
SUCCESSES = []
ERRORS = []


def main(fileName, keyType):
    """
    The main function that reads data from a file, retrieves package details based on the specified key type, and performs operations on the packages, such as marking them as delivered.

    Parameters:
    - fileName (str): The name of the file to read data from. Every line should be a package reference (ori, pi, bc)
    - keyType (str): The type of key to use for retrieving package details such as bc, ori, pi and so on.

    Returns:
    None
    """
    lines = files.get_data_from_file(fileName)
    env = utils.select_env()
    orgId = utils.select_org(env)

    print(
        "Key Types: {}\n".format(keyType.upper())
        + "Keys: \n"
        + "\n".join(map(str, lines))
        + "\n"
    )

    pkgs = []

    for line in lines:
        # getting packages from barcode present in file line
        pkgs = packages.get_package_details(env, orgId, keyType, line)["packageRecords"]

        if len(pkgs) == 0:
            print("> NO PACKAGES FOUND <\n")

        print(f"\n{'':=<50}")
        print(f"Found {len(pkgs)} packages, Applying filters")

        with ThreadPoolExecutor() as pool:
            for package in pkgs:
                orgId = package["orgId"]
                provider = str(package["providerDetails"]["providerName"]).upper()
                status = package["packageStatuses"]["status"]
                package_id = package["packageId"]
                hub_name = package["packageDetails"]["sourceLocation"]["name"]

                print(
                    f"\n---> PACKAGE ID: {package_id}" + " (DELIVERED)"
                    if status == "DELIVERED"
                    else "OK"
                )
                print(f"--> PROVIDER: {provider}")
                print(f"--> STATUS: {status}\n")
                print(f"--> HUB: {hub_name}")

                pool.submit(packages.mark_package_as_delivered, env, orgId, package_id)


# get command line argument
if len(sys.argv) < 3:
    print(
        "Please, check the correct script usage bellow:\n\n"
        + "PRE REQUISITES:\n"
        + "> A file <file>.txt should be created in this same directory. You should paste the barcodes/ORIs/PIs/etc there\n"
        + "SCRIPT USAGE:\n"
        + "--> python markDelivered.py <fileName> <keyType>\n\n"
        + "-> Accepted keyTypes:\n"
        + "> pi (Package Id)\n"
        + "> tn (Tracking Number)\n"
        + "> ci (Container Id)\n"
        + "> bc (Shipment Barcode)\n"
        + "> oi (Order Id)\n"
        + "> ori (Order Reference Id)\n"
        + "> ji (Job Id)\n\n"
        "SCRIPT EXAMPLE:\n"
        + "--> python replanPackages.py 8506 bc\n"
        + "> This will load all the barcodes on 8506.txt and mark delivered packages that are not already delivered\n\n"
        + "NOTES:\n"
        + "> Check comments on code to update relevant data such as keyType (bc, ori, etc), ORG Environment accordingly to your needs\n"
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
