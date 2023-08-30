from utils import packages, files, utils


# fileName = input("Type in file name containing the package ids?\n> ").strip()

def main():
    env = utils.select_env()
    orgId = utils.select_org(env)
    
    fileName = str(input("Type the file name (without extension): ")).strip()
    lines = files.get_data_from_file(fileName)

    keyType = str(input("Type the key types (e.g. bc, ori, pi, etc): ")).strip()
    packageIDs = []

    print("Filling Package IDs Array now...\n")

    for line in lines:
        pkgs = packages.get_packages_details(env, orgId, keyType, line)['packageRecords']

        for pkg in pkgs:
            status = pkg["packageStatuses"]["status"]
            # if package is marked as cancelled, 
            # revive the package
            # if status == "CANCELLED":
            #     packages.revive_package(env, pkg)
            
            # if package is marked as rejected or delivered,
            # change its status to DELIVERY_FAILED
            if status == "REJECTED" or status == "DAMAGED":# or status == "DELIVERED":
                packages.mark_package_as_delivery_failed(env, pkg)
                
            if len(packageIDs) < 100:
                packageIDs.append(pkg['packageId'])
            else:
                packages.bulk_cancel_packages(env, orgId, packageIDs)
                packageIDs = [pkg['packageId']]

    packages.bulk_cancel_packages(env, orgId, packageIDs)
                

main()
