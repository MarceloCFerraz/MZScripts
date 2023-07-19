import os
import sys
from datetime import datetime
from utils import files, packages


def saveJsonToFile(packages, hubName):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")
    # creates "RESULTS" folder directory
    response_dir = current_dir + "/RESULTS"
    os.makedirs(response_dir, exist_ok=True)
    
    dateTime = str(
        datetime.now().replace(second=0, microsecond=0)
    ).replace(':', '-').replace(' ', 'T')

    # names the file
    FILE_NAME = f"{dateTime}_{hubName}_PKG_HISTORIES.json"

    # this is the complete directory and where the file will be saved
    final_dir = os.path.join(response_dir, FILE_NAME)

    result = f"File {FILE_NAME} containing the complete response "

    with open(final_dir, "w") as json_file:
        try:
            json_file.write(str(packages))
            result += f"was created SUCCESSFULLY and can be accessed on ./RESULTS/{FILE_NAME}!"
        except Exception as e:
            result += f"COULD NOT be created. See exception bellow:\n\n{e}"

    print(result)



def main(fileName, keyType):
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
    saveJsonToFile(packages=formattedResponse, hubName=fileName)


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