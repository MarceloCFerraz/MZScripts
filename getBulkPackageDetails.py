import concurrent.futures

import getPackageDetails
from utils import files, packages, utils

PACKAGES = []


def search_packages(env: str, org_id: str, key_type: str, key: str, pids: set[str]):
    pkgs = packages.search_for_package(env, org_id, key, hub_name)["packages"]

    if len(pkgs) <= 0:
        return

    if len(pkgs) > 1 and key_type == "bc":
        raise Exception(
            f"Provided key is a barcode, which means it should have returned only 1 package. Please select the appropriate barcode from the objects below and try again:\n{pkgs}"
        )

    pids.add(pkgs[0]["packageId"])


def get_pkgs_from_pkg_seeker(
    env: str, org_id: str, key_type: str, batch: list[str], hub_name: str
):
    pids = set()

    with concurrent.futures.ThreadPoolExecutor() as pool:
        for key in batch:
            pool.submit(search_packages, env, org_id, key_type, key, pids)
    pool.shutdown(wait=True)

    print(f"Found {len(pids)} packages for batch" + f" for {hub_name}")

    if len(pids) == 0:
        raise Exception(
            "packageSeeker couldn't find any of the packages from this batch"
        )

    return packages.bulk_get_package_details(env, org_id, "pi", list(pids))


def fill_packages_list(
    env: str,
    org_id: str,
    key_type: str,
    key_batch: list[str],
    hub_name: str,
    use_pkg_seeker=False,
):
    """
    Fill the PACKAGES list with package details.

    Parameters:
    - env: The environment.
    - org_id: The organization ID.
    - key_type: The type of key.
    - key: The key.

    Returns:
    None
    """
    if use_pkg_seeker:
        pkgs = get_pkgs_from_pkg_seeker(env, org_id, key_type, key_batch, hub_name)
    else:
        pkgs = packages.bulk_get_package_details(env, org_id, key_type, key_batch)

    print(f"{len(pkgs)} packages found")

    if len(pkgs) == 0 and not use_pkg_seeker:
        print("We'll try again with Package Seeker + Switchboard")
        fill_packages_list(
            env, org_id, key_type, key_batch, hub_name, use_pkg_seeker=True
        )

    for pkg in pkgs:
        PACKAGES.append(pkg)


def main(
    env: str, org_id: str, key_type: str, keys: list[str], hub_name: str, statuses=""
):
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

    valid_statuses = []

    if statuses != "":
        valid_statuses = getPackageDetails.get_status_list(statuses)

    response = {}
    valid_packages = []
    invalid_packages = []

    batches = utils.divide_into_batches(keys)

    # Using multithreading to fetch multiple packages simultaneosly
    with concurrent.futures.ThreadPoolExecutor() as pool:
        for batch in batches:
            pool.submit(fill_packages_list, env, org_id, key_type, batch, hub_name)
            # getting packages from key (ori, bc, etc) present in file line

    pool.shutdown(wait=True)

    for package in PACKAGES:
        status = package["packageStatuses"]["status"]

        if valid_statuses != [] and status not in valid_statuses:
            invalid_packages.append(package)
            continue

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
    env = utils.select_env()
    org_id = utils.select_org(env)

    file_name = input("Type the file with the package keys: ").strip()

    keys = files.get_data_from_file(file_name)
    key_type = packages.select_key_type()

    hub_name = input("Type the hub name these packages belong to (optional): ").strip()

    statuses = ""
    if utils.select_answer("Do you want to filter by package status?") == "Y":
        statuses = input(
            "Type the status you want to see separated by spaces (e.g. cancelled delivered packed): "
        )

    main(env, org_id, key_type, keys, hub_name, statuses)
