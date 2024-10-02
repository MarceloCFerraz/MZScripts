import os
import sys

from utils import files, packages, utils


def get_file_name():
    """
    Create a unique log file name based on the current script name and timestamp.

    Returns:
    str: The unique log file name in the format "<script_name><timestamp>.txt".
    """

    # Get the name of the current script file
    script_file = os.path.basename(sys.argv[0])

    # Remove the file extension from the script name
    script_name = os.path.splitext(script_file)[0]

    # Create the log file name
    file_name = script_name + f"{utils.get_formated_now()}.txt"

    return file_name


def main(FILENAME, KEY_TYPE):
    """
    The main function for retrieving package details.

    Parameters:
    FILENAME (str): The name of the file containing the key values.
    KEY_TYPE (str): The type of key used for package retrieval. Valid options include:
        - "pi" (Package Id)
        - "bc" (Shipment Barcode)
        - "ori" (Order Reference Id)

    Returns:
    None
    """
    env = utils.select_env()
    orgId = utils.select_org(env)

    lines = files.get_data_from_file(FILENAME)

    print("Script is generating your file with the full response... ")

    logFile = files.create_logs_file()
    files.start_logging(logFile)

    for line in lines:
        pkgs = packages.get_package_details(env, orgId, KEY_TYPE, line)

        for package in pkgs:
            packageID = package["packageId"]
            hubName = package["packageDetails"]["sourceLocation"]["name"]
            try:
                routeId = package["planningDetails"]["plannerRouteId"]
            except Exception:
                print(
                    "This package/route was probably not executed (not ROUTE_ID found)"
                )
                routeId = package["planningDetails"]["originalRouteId"]

            routeName = package["planningDetails"]["plannerRouteName"]

            print(f"Package ID: {packageID}")
            print(f"HUB Name: {hubName}")
            print(f"Route Name: {routeName}")
            print(f"Route ID: {routeId}")

    files.stop_logging()
    files.close_logs_file(logFile)

    print(f"Script finished. Check for {get_file_name()}")


valid_key_types = [
    "pi (Package Id)",
    "tn (Tracking Number)",
    "ci (Container Id)",
    "bc (Shipment Barcode)",
    "oi (Order Id)",
    "ori (Order Reference Id)",
    "ji (Job Id)",
]
# get command line argument
if len(sys.argv) < 3:
    print(
        "\nNO ARGS PROVIDED!\n"
        + "Please, check the correct script usage bellow:\n\n"
        + "SCRIPT USAGE:\n"
        + "--> python getPackageRoute.py <FILE> <KEY_TYPE>\n\n"
        + "-> Accepted KEY_TYPEs:\n"
        + "\n".join(map(str, valid_key_types))
        + "\n\nSCRIPT EXAMPLE:\n"
        + "--> python getPackageRoute.py 'barcodes' bc\n"
        + "> This will load all the barcodes on barcodes.txt and print out their routeIds\n\n"
        + "NOTES:\n"
        + "> Check comments on code to update relevant data such as KEY_TYPE (bc, ori, etc)\n"
    )
    sys.exit(1)

# The file name must be to the requester's hub name (e.g. 8506)
FILENAME = sys.argv[1].replace(".txt", "").replace(".\\", "")
KEY_TYPE = sys.argv[2].lower()
main(FILENAME, KEY_TYPE)
