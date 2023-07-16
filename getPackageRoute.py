from datetime import datetime
import os
import sys
import json
import requests


API = "http://switchboard.prod.milezero.com/switchboard-war/api/"


def get_formated_now():
    return str(
        datetime.now().replace(second=0, microsecond=0)
    ).replace(':', '-').replace(' ', 'T')


def create_file_name():    
    
    # Get the name of the current script file
    script_file = os.path.basename(sys.argv[0])

    # Remove the file extension from the script name
    script_name = os.path.splitext(script_file)[0]

    # Create the log file name
    file_name = script_name + f"{get_formated_now()}.txt"

    return file_name


def create_logs_file():
    file_name = create_file_name()

    # Open the log file to redirect the standard output
    log_file = open(f"./{file_name}", "w")

    return log_file


def close_logs_file(log_file):
    log_file.close()


def start_logging(log_file):
    # Redirect the standard output to the log file
    sys.stdout = log_file


def stop_logging():
    sys.stdout = sys.__stdout__


def getPackages(KEY_TYPE, key):
    # f"{API}package/histories?keyValue={key}&keyType={keyType}"
    endpoint = f"{API}package?keyType={KEY_TYPE}&keyValue={key}&includeCancelledPackage=true"

    # print(
    #     f">>>>> Retrieving Packages From {KEY_TYPE.upper()} {key} <<<<<"+
    #     f"\n> {endpoint}"
    # )
    
    return requests.get(endpoint, timeout=5).json()


def printPackageDetails(package):
    packageID = package["packageId"]

    try:
        routeId = package["planningDetails"]["plannerRouteId"]
    except Exception as e:
        pass

    previousRouteId = package["planningDetails"]["originalRouteId"]
    routeName = package["planningDetails"]["plannerRouteName"]
    

    half_divisor = "==================="

    print(f"\n{half_divisor} ROUTE {half_divisor}")
    print(f"Package ID: {packageID}")
    print(f"Route Name: {routeName}")
    print(f"Route ID: {routeId}")
    print(f"Original Route ID: {previousRouteId}\n")


def get_data_from_file(fileName):
    file = open(fileName+".txt", "r")
    lines = file.readlines()
    file.close()

    results = []
    
    for line in lines:
        results.append(line.strip())

    # removing duplicates from list
    # this make the list unordered. Comment this line if
    # this impact your workflow somehow
    results = list(set(results))
    
    print("{} unique lines in file {}\n".format(len(results), fileName))
    return results


def main(FILENAME, KEY_TYPE):
    lines = get_data_from_file(FILENAME)

    print("Script is generating your file with the full response... ")

    logFile = create_logs_file()
    start_logging(logFile)
    
    for line in lines:
        packages = getPackages(KEY_TYPE=KEY_TYPE, key=line)["packageRecords"]
        for package in packages:
            printPackageDetails(package)

    stop_logging()
    close_logs_file(logFile)

    print(f"Script finished. Check for {create_file_name()}")


valid_key_types = [
    "pi (Package Id)",
    "tn (Tracking Number)",
    "ci (Container Id)",
    "bc (Shipment Barcode)",
    "oi (Order Id)",
    "ori (Order Reference Id)",
    "ji (Job Id)"
]
# get command line argument
if len(sys.argv) < 3:
    print(
        "\nNO ARGS PROVIDED!\n"+
        "Please, check the correct script usage bellow:\n\n"+

        "SCRIPT USAGE:\n"+
        "--> python getPackageRoute.py <FILE> <KEY_TYPE>\n\n"+

        "-> Accepted KEY_TYPEs:\n"+
        "\n".join(map(str, valid_key_types))+

        "\n\nSCRIPT EXAMPLE:\n"+
        "--> python getPackageRoute.py 'barcodes' bc\n"+
        "> This will load all the barcodes on barcodes.txt and print out their routeIds\n\n"+

        "NOTES:\n"+
        "> Check comments on code to update relevant data such as KEY_TYPE (bc, ori, etc)\n"
    )
    sys.exit(1)

# The file name must be to the requester's hub name (e.g. 8506)
FILENAME = sys.argv[1].replace(".txt", "").replace(".\\", "")
KEY_TYPE = sys.argv[2].lower()
main(FILENAME, KEY_TYPE)
