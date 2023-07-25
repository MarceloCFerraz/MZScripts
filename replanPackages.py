from datetime import datetime
from utils import files, packages
import sys


SUCCESSES = []
ERRORS = []


def replan(fileName, keyType, next_delivery_date):
    lines = files.get_data_from_file(fileName)
    
    print("Key Types: {}\n".format(keyType.upper())+
        "Keys: {}\n".format(lines))
    
    pkgs = []
    
    for line in lines:
        # getting packages from barcode present in file line
        pkgs = packages.get_packages_details(keyType, line)["packageRecords"]

        if (len(pkgs) == 0):
            print("> NO PACKAGES FOUND <\n")
    
        for package in pkgs:
            status = package["packageStatuses"]["status"]
            packageID = package["packageId"]
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
                        sys.exit()

            print("----> PACKAGE ID: {}".format(packageID))
            print("--> STATUS: {}".format(status))
            print("--> HUB: {}\n".format(hubName))
            
            # if package is from the correct hub, continues.
            if hubName == fileName:
            
                # if package is marked as cancelled, 
                # revive the package
                if status == "CANCELLED":
                    packages.revive_package(package)
                
                # if package is marked as rejected or delivered,
                # change its status to DELIVERY_FAILED
                if status == "DELIVERED" or status == "REJECTED":
                    packages.mark_package_as_delivery_failed(package)

                response = packages.resubmit_package(
                    package, 
                    next_delivery_date
                )

                for s in response["SUCCESSES"]:
                    SUCCESSES.append(s)
                for e in response["ERRORS"]:
                    ERRORS.append(e)
            else:
                print("---> Ignored because it isn't from hub {}\n".format(fileName))
    print("Successful Resubmits ({}/{}): ".format(len(SUCCESSES), len(SUCCESSES) + len(ERRORS)))
    for success in SUCCESSES:
        print("> {}".format(success))

    print("Unsuccessful Resubmits ({}/{}): ".format(len(ERRORS), len(SUCCESSES) + len(ERRORS)))
    for error in ERRORS:
        print("> {}".format(error))


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
replan(fileName, keyType, next_delivery_date)
