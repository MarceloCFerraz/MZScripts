import concurrent.futures
from datetime import datetime
from utils import files, packages, utils
import sys


SUCCESSES = []
ERRORS = []
PACKAGES = []


def get_package_hub(package):
    """
    Get the hub name associated with a package.

    Parameters:
    - package: A dictionary representing the package details.

    Returns:
    - hubName: The name of the hub associated with the package.
    """
    hubName = ""
    
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
                # sys.exit()
    
    return hubName


def fill_packages_list(env, orgId, keyType, key):
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
    pkgs = packages.get_packages_details(env, orgId, keyType, key)["packageRecords"]

    if (len(pkgs) == 0):
        print("> NO PACKAGES FOUND <\n")
    for pkg in pkgs:
        PACKAGES.append(pkg)


def replan_batches(env, orgId, hubRequested, batch, next_delivery_date):
    """
    Replan packages in batches based on specific criteria.

    Parameters:
    - env: The environment.
    - orgId: The organization ID.
    - hubRequested: The requested hub name.
    - batch: A list of packages in a batch.
    - next_delivery_date: The next delivery date.

    Returns:
    None
    """
    packageIDs = []

    for package in batch:
        status = package["packageStatuses"]["status"]
        packageID = package["packageId"]
        hubName = get_package_hub(package)
        
        # if package is from the correct hub, continues.
        if hubName == hubRequested:
        
            # if package is marked as cancelled or damaged, 
            # revive the package
            if status == "CANCELLED":
                packages.revive_package(env, package)
            
            # if package is marked as rejected or delivered,
            # change its status to DELIVERY_FAILED
            if status == "DELIVERED" or status == "REJECTED":
                packages.mark_package_as_delivery_failed(env, package)

            packageIDs.append(packageID)

    result = packages.bulk_resubmit_packages(env, orgId, packageIDs, next_delivery_date)
    
    for success in result('SUCCESS'):
        SUCCESSES.append(success)
    
    for error in result.get('ERROR'):
        ERRORS.append(error)


def replan(env, orgId, hubRequested, package, next_delivery_date):
    """
    Replan a single package based on specific criteria.

    Parameters:
    - env: The environment.
    - orgId: The organization ID.
    - hubRequested: The requested hub name.
    - package: A dictionary representing the package details.
    - next_delivery_date: The next delivery date.

    Returns:
    None
    """
    status = package["packageStatuses"]["status"]
    packageID = package["packageId"]
    hubName = get_package_hub(package)
    
    # if package is from the correct hub, continues.
    if hubName == hubRequested:
    
        # if package is marked as cancelled or damaged, 
        # revive the package
        if status == "CANCELLED":
            packages.revive_package(env, package)
        
        # if package is marked as rejected or delivered,
        # change its status to DELIVERY_FAILED
        if status == "DELIVERED" or status == "REJECTED":
            packages.mark_package_as_delivery_failed(env, package)

        response = packages.resubmit_package(
            env,
            orgId,
            packageID,
            next_delivery_date
        )

        if response["SUCCESS"]:
            SUCCESSES.append(response["SUCCESS"])
        if response["ERROR"]:
            ERRORS.append(response["ERROR"])
    else:
        print(f"---> {packageID} Ignored because it isn't from hub {hubRequested} (it is from {hubName})\n")


def main(fileName, keyType, next_delivery_date, env=None, orgId=None):
    """
    The main function that orchestrates the package resubmission process.

    Parameters:
    - fileName: The name of the file.
    - keyType: The type of key.
    - next_delivery_date: The next delivery date.
    - env: Optional. The environment. Defaults to None.
    - orgId: Optional. The organization ID. Defaults to None.

    Returns:
        None
    """
    if not env:
        env = utils.select_env()
    if not orgId:
        orgId = utils.select_org(env)

    lines = files.get_data_from_file(fileName)

    print("Key Types: {}\n".format(keyType.upper())+
        "Keys: {}\n".format(lines))

    # Using multithreading to fetch multiple packages simultaneosly
    with concurrent.futures.ThreadPoolExecutor() as pool:
        for key in lines:
            # getting packages from key (ori, bc, etc) present in file line
            pool.submit(fill_packages_list, env, orgId, keyType, key)

    pool.shutdown(wait=True)

    print()
    print("===============================")
    for pkg in PACKAGES:
        packages.print_minimal_package_details(pkg)
        print("===============================")
    print()

    # If there are a lot of packages to re-submit, we'll split them in batches
    # to reduce the amount of API calls by calling the 'bulk resubmit' endpoint
    # Using multithreading to replan multiple packages simultaneosly
    with concurrent.futures.ThreadPoolExecutor() as pool:
        if len(PACKAGES) >= 20:
            batches = utils.divide_into_batches(PACKAGES)

            for batch in batches:
                pool.submit(replan_batches, env, orgId, fileName, batch, next_delivery_date)
        else:
            for package in PACKAGES:
                pool.submit(replan, env, orgId, fileName, package, next_delivery_date)

    pool.shutdown(wait=True)
    
    print("Successful Resubmits ({}/{}): ".format(len(SUCCESSES), len(SUCCESSES) + len(ERRORS)))
    for success in SUCCESSES:
        print("> {}".format(success))

    print("Unsuccessful Resubmits ({}/{}): ".format(len(ERRORS), len(SUCCESSES) + len(ERRORS)))
    for error in ERRORS:
        print("> {}".format(error))
        # TODO: add where it failed to the error line and remove logging prints


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

main(fileName, keyType, next_delivery_date)
