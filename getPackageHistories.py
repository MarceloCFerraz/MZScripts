import sys


from utils import files, packages, utils


def main(KEY, KEY_TYPE):
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
    env = utils.select_env()
    orgId = utils.select_org(env)

    histories = packages.get_package_histories(env, orgId, KEY_TYPE, KEY)["histories"]

    if histories != []:
        for history in histories:
            packages.print_package_histories(history)

    response = files.format_json(histories)
    files.save_json_to_file(response, "PKG_HISTORY")


# get command line argument
if len(sys.argv) < 3:
    print(
        "\nNO ARGS PROVIDED!\n"
        + "Please, check the correct script usage bellow:\n\n"
        + "SCRIPT USAGE:\n"
        + "--> python getPackageHistories.py <KEY> <KEY_TYPE>\n\n"
        + "-> Accepted keyTypes:\n"
        + "\n".join(map(str, packages.VALID_KEY_TYPES))
        + "\n\nSCRIPT EXAMPLE:\n"
        + "--> python getBulkPackageHistories.py 8506 bc\n"
        + "> This will load all the barcodes on 8506.txt and print the "
        + "HTTP response for each of them on a json file\n\n"
        + "NOTES:\n"
        + "> Check comments on code to update relevant data such as KEY_TYPE (bc, ori, etc), nextDeliveryDate (if dispatcher wants a specific date that is not the next day) accordingly to your needs\n"
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
