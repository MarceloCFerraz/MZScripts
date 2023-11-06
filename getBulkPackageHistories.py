import os
import sys
from datetime import datetime
from utils import files, packages


def main(fileName, keyType):
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
    keys = files.get_data_from_file(fileName)
    historyList = []
    formattedResponse = {}

    for key in keys:
        pkgs = packages.get_packages_histories(keyType=keyType, key=key)["histories"]

        if pkgs != []:
            historyList.append(pkgs)
            # for package in pkgs:
                # packages.print_package_histories(package)
    
    formattedResponse["histories"] = historyList
    formattedResponse = files.format_json(formattedResponse)
    files.save_json_to_file(formattedResponse, "PKGS_HISTORIES")


# get command line argument
if (len(sys.argv) < 3):
    print(
        "\nNO ARGS PROVIDED!\n"+
        "Please, check the correct script usage bellow:\n\n"+
        
        "PRE REQUISITES:\n"+
        "> A file <hubName>.txt should be created in this same directory. You should paste the barcodes/ORIs to be replanned there\n"+
        "--> hubName: the hub that requested a replan in number format\n\n"+
        
        "SCRIPT USAGE:\n"+
        "--> python getBulkPackageHistories.py <hubName> <keyType>\n\n"+
        "-> Accepted keyTypes:\n"+
        "\n".join(map(str, packages.VALID_KEY_TYPES))+
        
        "\n\nSCRIPT EXAMPLE:\n"+
        "--> python getBulkPackageHistories.py 8506 bc\n"+
        "> This will load all the barcodes on 8506.txt and print the "+
        "HTTP response for each of them on a json file\n\n"+
        
        "NOTES:\n"+
        "> Check comments on code to update relevant data such as keyType (bc, ori, etc), nextDeliveryDate (if dispatcher wants a specific date that is not the next day) accordingly to your needs\n"
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