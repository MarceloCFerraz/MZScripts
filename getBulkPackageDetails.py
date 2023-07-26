import os
import sys
from utils import files, packages



def getStatusList(STATUSES):
    status = ""
    status_list = []

    for char in STATUSES:
        if char != " ":
            status += char.upper()
        else:
            status_list.append(status)
            status = ""
    
    # to get the last status provided, since there aren't any spaces left
    status_list.append(status)

    return status_list


def saveJsonToFile(packages, file_name):
    # get current file directory and replaces "\" for "/"
    # even in windows this works out just fine
    current_dir = os.path.realpath(os.path.dirname(__name__)).replace("\\", "/")
    # creates "RESULSTS" folder directory
    response_dir = current_dir + "/RESULTS"
    os.makedirs(response_dir, exist_ok=True)
    
    # names the file
    FILE_NAME = f"{file_name}_DETAILS.json"

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


def main(FILE_NAME, KEY_TYPE, STATUSES):
    status_list = []
    
    if STATUSES != "":
        status_list = getStatusList(STATUSES)
    
    keys = files.get_data_from_file(FILE_NAME)
    response = {}
    valid_packages = []
    invalid_packages = 0

    for key in keys:
        pkgs = packages.get_packages_details(KEY_TYPE=KEY_TYPE, key=key)["packageRecords"]
        for package in pkgs:
            status = package["packageStatuses"]["status"]

            if status_list != [] and status not in status_list:
                print(f"Package ignored (not marked as {', '.join(status_list)})")
                invalid_packages += 1
            else:
                packages.print_package_details(package)
                print(f"Package added to final response ({status})")
                valid_packages.append(package)
    
    response["packageRecords"] = valid_packages
    response["count"] = len(valid_packages)

    print(f"\nValid Packages: {len(valid_packages)}")
    print(f"Invalid Packages: {invalid_packages}\n")

    if valid_packages != []:
        formatted_response = files.format_json(response)
        saveJsonToFile(packages=formatted_response, file_name=FILE_NAME)



# get command line argument
if len(sys.argv) < 3:
    print(
        "\nNO ARGS PROVIDED!\n"+
        "Please, check the correct script usage bellow:\n\n"+

        "PRE REQUISITES:\n"+
        "> A file <hubName>.txt should be created in this same directory.\n"+
        "You should paste the barcodes/ORIs to be replanned there\n"+
        "--> hubName: the hub that requested support\n\n"+

        "SCRIPT USAGE:\n"+
        "--> python getBulkPackageDetails.py <HUB_NAME> <KEY_TYPE> (OPTIONAL) <STATUSES>\n\n"+

        "-> Accepted KEY_TYPEs:\n"+
        "\n".join(map(str, packages.VALID_KEY_TYPES))+

        "\n\n--> Valid Statuses:\n"+
        "\n".join(map(str, packages.VALID_STATUSES))+

        "\n\nSCRIPT EXAMPLE:\n"+
        "--> python getBulkPackageDetails.py 8506 bc 'cancelled delivered'\n"+
        "> This will load all the barcodes on 8506.txt, print the HTTP request for "+
        "each of them on a json file and console IF their status corresponds to"+
        " 'CANCELLED' or 'DELIVERED'.\n\n"+
        
        " If no filter status is informed, all statuses will be displayed\n\n"+

        "NOTES:\n"+
        "> Check comments on code to update relevant data such as KEY_TYPE (bc, ori, etc)\n"
    )
    sys.exit(1)

# The file name must be to the requester's hub name (e.g. 8506)
FILE_NAME = sys.argv[1].replace(".txt", "").replace(".\\", "")
KEY_TYPE = sys.argv[2].lower()
STATUSES = ""
try:
    STATUSES = sys.argv[3]
except Exception as e:
    pass
main(FILE_NAME, KEY_TYPE, STATUSES)
