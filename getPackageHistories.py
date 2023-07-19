import os
import sys
from utils import files, packages


def saveJsonToFile(packages, key):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")
    # creates "RESULTS" folder directory
    response_dir = current_dir + "/RESULTS"
    os.makedirs(response_dir, exist_ok=True)
    
    # names the file
    FILE_NAME = f"{key}_HISTORIES.json"

    # this is the complete directory and where the file will be saved
    final_dir = os.path.join(response_dir, FILE_NAME)

    result = f"File {FILE_NAME} containing the complete response "

    with open(final_dir, "w") as json_file:
        try:
            json_file.write(packages)
            result += f"was created SUCCESSFULLY and can be accessed on ./RESULTS/{FILE_NAME}!"
        except Exception as e:
            result += f"COULD NOT be created. See exception bellow:\n\n{e}"

    print(result)


def main(KEY, KEY_TYPE):
    response = {}
    pkgs = packages.get_packages_histories(KEY_TYPE=KEY_TYPE, KEY=KEY)["histories"]

    if pkgs != []:
        for package in pkgs:
            packages.print_package_histories(package)
    
    formattedResponse = files.format_json(response)
    saveJsonToFile(packages=formattedResponse, key=KEY)


# get command line argument
if (len(sys.argv) < 3):
    print(
        "\nNO ARGS PROVIDED!\n"+
        "Please, check the correct script usage bellow:\n\n"+
        
        "SCRIPT USAGE:\n"+
        "--> python getPackageHistories.py <KEY> <KEY_TYPE>\n\n"+
        "-> Accepted keyTypes:\n"+
        "\n".join(map(str, packages.VALID_KEY_TYPES))+
        
        "\n\nSCRIPT EXAMPLE:\n"+
        "--> python getBulkPackageHistories.py 8506 bc\n"+
        "> This will load all the barcodes on 8506.txt and print the "+
        "HTTP response for each of them on a json file\n\n"+
        
        "NOTES:\n"+
        "> Check comments on code to update relevant data such as KEY_TYPE (bc, ori, etc), nextDeliveryDate (if dispatcher wants a specific date that is not the next day) accordingly to your needs\n"
    )
    sys.exit(1)

# The file name must be to the requester's hub name (e.g. 8506)
KEY = sys.argv[1].replace(".txt", "").replace(".\\", "")
# A KeyType arg must be provided. provide one of the following keyTypes:
# -> pi (Package Id)
# -> tn (Tracking Number)
# -> ci (Container Id)
# -> bc (Shipment Barcode)
# -> oi (Order Id)
# -> ori (Order Reference Id)
# -> ji (Job Id)
KEY_TYPE = sys.argv[2].lower()
main(KEY, KEY_TYPE)