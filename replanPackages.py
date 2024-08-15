import concurrent.futures
from datetime import datetime

from utils import files, packages, utils

SUCCESSES = []
ERRORS = []
PACKAGES = []
FORCE_REPLAN = False
ALREADY_ASKED = False


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
    add_to_packages_list(
        packages.get_package_details(env, orgId, keyType, key)["packageRecords"]
    )


def search_pkgs(env, orgId, keyType, batch, hubName: str | None):
    pids = set()

    try:
        for pkg in batch:
            p = packages.search_for_package(env, orgId, pkg, hubName)["packages"]

            if len(p) <= 0:
                print(
                    f"Package Seeker couldn't find {pkg}" + f" for {hubName}"
                    if hubName
                    else ""
                )
                continue

            pids.add(p[0]["packageId"])

        print(
            f"Found {len(pids)} packages for batch" + f" for {hubName}"
            if hubName
            else ""
        )
    except Exception as e:
        print(e)

    if len(pids) == 0:
        print("packageSeeker couldn't find any of the packages from this batch")
        return

    add_to_packages_list(
        packages.bulk_get_package_details(env, orgId, "pi", list(pids))[
            "packageRecords"
        ]
    )


def fill_packages_list_batch(env, orgId, keyType, batch, hubName: str | None):
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
    add_to_packages_list(
        packages.bulk_get_package_details(env, orgId, keyType, batch)["packageRecords"]
    )


def add_to_packages_list(pkgs):
    global ALREADY_ASKED, FORCE_REPLAN

    print(f">Found {len(pkgs)} packages")

    if len(pkgs) == 0:
        print("> Quitting\n")
        return

    print(f"{' Applying filters ':=^50}")

    if FORCE_REPLAN is False and ALREADY_ASKED is False:
        ALREADY_ASKED = True

        answer = input(
            "> Do you want to force replan all packages? Type 'Y' or leave blank to continue: "
        )

        if answer.upper() == "Y":
            print("Forcing replan for all packages")
            FORCE_REPLAN = True
        else:
            print("We'll ignore any DELIVERED packages")

    for pkg in pkgs:
        statuses = pkg["packageStatuses"]

        # replanning only undelivered packages. Comment this if statement if you need to replan a package marked as delivered in error
        if statuses["status"] == "DELIVERED" or (
            statuses.get("deliveryFlags")
            and (
                statuses["deliveryFlags"].get("delivered") is True
                and statuses["deliveryFlags"].get("deliveryDay") is not None
            )
        ):
            print(
                f"> {pkg['packageId']} was already DELIVERED." + " Ignoring"
                if not FORCE_REPLAN
                else " but will be replanned"
            )

            if not FORCE_REPLAN:
                continue

        PACKAGES.append(pkg)


def replan_batch(env, orgId, batch: list[dict], next_delivery_date, hubRequested=None):
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
        hubName = packages.get_package_hub(package)

        # if package is from the correct hub or if we don't want to filter by hub, continues
        if hubName == hubRequested or not hubRequested:
            prepare_package_for_replan(env, package)

            packageIDs.append(package["packageId"])

    if packageIDs:
        result = packages.bulk_resubmit_packages(
            env, orgId, packageIDs, next_delivery_date
        )

        for success in result["SUCCESS"]:
            SUCCESSES.append(success)

        for error in result["ERROR"]:
            ERRORS.append(error)
    else:
        print(f">> Packages not from {hubRequested} or packages doesn't exist")


def replan(env, orgId, package, next_delivery_date, hubRequested=None):
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
    packageID = package["packageId"]
    hubName = packages.get_package_hub(package)

    # if package is from the correct hub, continues.
    if hubRequested and hubName != hubRequested:
        print(
            f">> {packageID} Ignored because it isn't from hub {hubRequested} (it is from {hubName})\n"
        )
        return

    prepare_package_for_replan(env, package)

    response = packages.resubmit_package(env, orgId, packageID, next_delivery_date)

    if response["SUCCESS"]:
        SUCCESSES.append(response["SUCCESS"])
    if response["ERROR"]:
        ERRORS.append(response["ERROR"])


def prepare_package_for_replan(env, package):
    status = package["packageStatuses"]["status"]
    REVIVE_STATUSES = ["CANCELLED"]
    DELIVERY_FAILED_STATUSES = ["REJECTED", "DAMAGED", "DELIVERED"]

    # if package is has terminal status,
    # revive the package
    if status in REVIVE_STATUSES:
        packages.revive_package(env, package)

    # if package is not being seen by the planner and needs to,
    # change status to DELIVERY_FAILED
    if status in DELIVERY_FAILED_STATUSES:
        packages.mark_package_as_delivery_failed(env, package)


def load_inputs(
    env=None,
    orgId=None,
    hubName=None,
    fileName=None,
    keyType=None,
    keys=None,
    next_delivery_date=None,
):
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
    if env is None:
        env = utils.select_env()

    if orgId is None:
        orgId = utils.select_org(env)

    if fileName is None:
        # The file name must be to the requester's hub name (e.g. 8506)
        if utils.select_answer(">> Do you have a file with the package keys?") == "Y":
            fileName = (
                input(">> Type the file name: ")
                .strip()
                .replace(".txt", "")
                .replace("./", "")
                .replace(".\\", "")
            )
            # if user wants to read packages from a file, get them now
            keys = files.get_data_from_file(fileName)
            if not keys:
                return

    if keyType is None:
        keyType = packages.select_key_type()

    if keys is None:
        keys = packages.get_list_of_keys(keyType)

    if hubName is None:
        if utils.select_answer(">> Do you wish filter by hub name?") == "Y":
            hubName = input(">> Type the Hub Name: ").strip().upper()

    if next_delivery_date is None:
        # A date to do the replan must be provided with the yyyy-mm-dd format
        # reads a string in a yyyy-mm-dd from user input and creates a datetime object with it
        next_delivery_date = datetime.strptime(
            input(">> Type the next delivery date: "), "%Y-%m-%d"
        )

        # converts the datetime object to a string with the yyyy-mm-dd format
        next_delivery_date = next_delivery_date.strftime("%Y-%m-%d")

    main(
        env,
        orgId,
        keys,
        keyType,
        next_delivery_date,
        hubName,
    )


def main(
    env: str,
    orgId: str,
    keys: list[str],
    keyType: str,
    next_delivery_date: str,
    hubName=None,
):
    print(f"Key Types: {keyType.upper()}\nKeys: {keys}\n")
    load_packages(env, orgId, keyType, keys, hubName)

    if len(PACKAGES) == 0:
        print("Trying to search again with Package Seeker + Switchboard")
        # time.sleep(5)
        load_packages(env, orgId, keyType, keys, hubName, usePkgSeeker=True)

    process_packages(env, orgId, next_delivery_date, hubName)


def load_packages(
    env: str,
    orgId: str,
    keyType: str,
    keys: list[str],
    hubName: str | None,
    usePkgSeeker: bool = False,
):
    # Using multithreading to fetch multiple packages simultaneosly
    # also split in batches to make less api calls and also accelerate the whole process
    # with concurrent.futures.ThreadPoolExecutor(8) as pool:
    # getting packages in Switchboard with keys (ori, bc, etc) provided in the file <fileName>.txt

    batches = utils.divide_into_batches(keys)

    for batch in batches:
        if usePkgSeeker:
            # pool.submit(search_pkgs, env, orgId, keyType, batch, hubName)
            search_pkgs(env, orgId, keyType, batch, hubName)
        else:
            # pool.submit(fill_packages_list_batch, env, orgId, keyType, batch, hubName)
            fill_packages_list_batch(env, orgId, keyType, batch, hubName)
    #    pool.shutdown(wait=True)
    print()
    print("===============================")

    for pkg in PACKAGES:
        if len(PACKAGES) <= 10:
            packages.print_package_details(pkg)
            print("\n\n")

    print("===============================")
    print(f">> {len(PACKAGES)} packages loaded out of {len(keys)} keys")
    print()


def process_packages(env, orgId, next_delivery_date, hubName=None, packages=None):
    if packages is None:
        packages = PACKAGES

    # If there are a lot of packages to re-submit, we'll split them in batches
    # to reduce the amount of API calls by calling the 'bulk resubmit' endpoint
    # Using multithreading to replan multiple packages simultaneosly
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        if len(packages) > 1:
            batches = utils.divide_into_batches(packages)

            for batch in batches:
                pool.submit(
                    replan_batch, env, orgId, batch, next_delivery_date, hubName
                )
        else:
            for package in packages:
                pool.submit(replan, env, orgId, package, next_delivery_date, hubName)

    pool.shutdown(wait=True)

    print_results()


def print_results():
    print(
        "Successful Resubmits ({}/{}): ".format(
            len(SUCCESSES), len(SUCCESSES) + len(ERRORS)
        )
    )
    print(SUCCESSES)
    # for success in SUCCESSES:
    #     print(f"> {success}")

    print(
        "Unsuccessful Resubmits ({}/{}): ".format(
            len(ERRORS), len(SUCCESSES) + len(ERRORS)
        )
    )
    print(ERRORS)
    # for error in ERRORS:
    #     print(f"> {error}")


if __name__ == "__main__":
    load_inputs()
