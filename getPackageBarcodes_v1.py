from datetime import datetime
import os
import sys
import json
import requests


API = "http://switchboard.prod.milezero.com/switchboard-war/api/"


def get_formated_now():
    """
    Returns the current date and time in a formatted string.

    Returns:
    str: The formatted current date and time.
    """
    return str(
        datetime.now().replace(second=0, microsecond=0)
    ).replace(':', '-').replace(' ', 'T')


def create_file_name():
    """
    Creates a file name based on the current script name and formatted current time.

    Returns:
    str: The created file name.
    """    
    # Get the name of the current script file
    script_file = os.path.basename(sys.argv[0])

    # Remove the file extension from the script name
    script_name = os.path.splitext(script_file)[0]

    # Create the log file name
    file_name = script_name + f"{get_formated_now()}.txt"

    return file_name


def create_logs_file():
    """
    Creates a log file and returns the file object.

    Returns:
    file: The log file object.
    """
    file_name = create_file_name()

    # Open the log file to redirect the standard output
    log_file = open(f"./{file_name}", "w")

    return log_file


def close_logs_file(log_file):
    """
    Closes the log file.

    Parameters:
    log_file (file): The log file object to be closed.
    """
    log_file.close()


def start_logging(log_file):
    """
    Redirects the standard output to the log file.

    Parameters:
    log_file (file): The log file object to redirect the output to.
    """
    # Redirect the standard output to the log file
    sys.stdout = log_file


def stop_logging():
    """
    Stops redirecting the standard output to the log file.
    """
    sys.stdout = sys.__stdout__


def get_packages(KEY_TYPE, key):
    """
    Retrieves packages based on the specified key type and key value.

    Parameters:
    KEY_TYPE (str): The type of key used for package retrieval.
    key (str): The key value corresponding to the specified key type.

    Returns:
    dict: The JSON response containing the package details.
    """
    # f"{API}package/histories?keyValue={key}&keyType={keyType}"
    endpoint = f"{API}package?keyType={KEY_TYPE}&keyValue={key}&includeCancelledPackage=true"

    # print(
    #     f">>>>> Retrieving Packages From {KEY_TYPE.upper()} {key} <<<<<"+
    #     f"\n> {endpoint}"
    # )
    
    return requests.get(endpoint, timeout=5).json()


def get_data_from_file(fileName):
    """
    Retrieves data from a file.

    Parameters:
    fileName (str): The name of the file to retrieve data from.

    Returns:
    list: The list of retrieved data.
    """
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


def print_package_details(package):
    """
    Prints the details of a package.

    Parameters:
    package (dict): The package details.

    Returns:
    None
    """
    packageID = package["packageId"]
    ori = package["orderDetails"]["orderReferenceId"]            
    barcode = package["packageDetails"]["shipmentBarcode"]
    

    half_divisor = "==================="

    print(f"\n{half_divisor} PACKAGE {half_divisor}")
    print(f"Package ID: {packageID}")
    print(f"Scannable Barcode: {barcode}")
    print(f"Order Reference ID: {ori}")


def main(FILENAME, KEY_TYPE):
    """
    The main function for processing the data from a file and retrieving package details.

    Parameters:
    FILENAME (str): The name of the file to process.
    KEY_TYPE (str): The type of key used for package retrieval.

    Returns:
    None
    """
    lines = get_data_from_file(FILENAME)

    print("Script is generating your file with the full response... ")
    
    logFile = create_logs_file()
    start_logging(logFile)
    
    for line in lines:
        pkgs = get_packages(KEY_TYPE=KEY_TYPE, key=line)["packageRecords"]
        for pkg in pkgs:
            print_package_details(pkg)

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
if len(sys.argv) < 2:
    print(
        "\nNO ARGS PROVIDED!\n"+
        "Please, check the correct script usage bellow:\n\n"+

        "SCRIPT USAGE:\n"+
        "--> python getPackageBarcodes.py <FILE>\n\n"+

        "\n\nSCRIPT EXAMPLE:\n"+
        "--> python getPackageBarcodes.py 'barcodes'\n"+
        "> This will load all the barcodes on barcodes.txt and print out their barcodes\n\n"+

        "NOTES:\n"+
        "> Check comments on code to update relevant data such as KEY_TYPE (bc, ori, etc)\n"
    )
    sys.exit(1)

# The file name must be to the requester's hub name (e.g. 8506)
FILENAME = sys.argv[1].replace(".txt", "").replace(".\\", "")
KEY_TYPE = "pi"
main(FILENAME, KEY_TYPE)
