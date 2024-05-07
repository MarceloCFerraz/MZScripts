from utils import files, packages, utils

# fileName = input("Type in file name containing the package ids?\n> ").strip()


def main():
    """
    Main function to process data and perform package operations.

    This function serves as the entry point for processing data and performing package operations. It prompts the user to select an environment and organization, loads data from a file, and iterates over each line to retrieve package details based on the provided key type. It then performs various operations on the packages, such as reviving cancelled packages and marking rejected or damaged packages as delivery failed. It also handles bulk cancellation of packages when the package IDs exceed 100.

    Parameters:
    None

    Returns:
    None
    """
    env = utils.select_env()
    orgId = utils.select_org(env)

    fileName = str(input("Type the file name (without extension): ")).strip()
    lines = files.get_data_from_file(fileName)

    keyType = str(input("Type the key types (e.g. bc, ori, pi, etc): ")).strip()
    packageIDs = []

    print("Filling Package IDs Array now...\n")

    for line in lines:
        pkgs = packages.get_package_details(env, orgId, keyType, line)["packageRecords"]

        for pkg in pkgs:
            status = pkg["packageStatuses"]["status"]
            # if package is marked as cancelled,
            # revive the package
            # if status == "CANCELLED":
            #     packages.revive_package(env, pkg)

            # if package is marked as rejected or delivered,
            # change its status to DELIVERY_FAILED
            if status == "REJECTED" or status == "DAMAGED":  # or status == "DELIVERED":
                packages.mark_package_as_delivery_failed(env, pkg)

            if len(packageIDs) < 100:
                packageIDs.append(pkg["packageId"])
            else:
                packages.bulk_cancel_packages(env, orgId, packageIDs)
                packageIDs = [pkg["packageId"]]

    packages.bulk_cancel_packages(env, orgId, packageIDs)


main()
