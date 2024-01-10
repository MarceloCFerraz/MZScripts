import requests
import pandas
from datetime import datetime

ORGS = {
    "PROD": {
        "CLM": "8a9e84be-9874-4346-baab-26053d35871e",
        "STAPLES": "3c897e84-3957-4958-b54d-d02c01b14f15",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "ca3ffc06-b583-409f-a249-bdd014e21e31",
        "M3": "e9b34629-061d-4e24-93b1-717c00e2f116",
        "CFM": "8a9e84be-9874-4346-baab-26053d35871e",
        # "WALT'S": "ce8766a5-1d0f-4146-8a7c-98c0879cef10",  # Sandbox
        # "CUB": "6591e63e-6065-442d-87c3-20a5cd98cdba",  # not a client anymore
        "CUBPHARMA": "706660ca-71f6-4c01-a9ff-3a480acebaf4",
        "SHOPRITE-MM": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        "SHOPRITE": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        # "EMPIRE": "de03ba9f-7baa-4f64-9628-5eb75b970af1",  # Sandbox
        "ESSENDANT": "3d765297-0e0e-4178-843b-0ebdac333c7a",
        # "DELIVERY SOLUTIONS": "1bced832-4e3b-4f21-b803-477869cf02af", # Sandbox
        "LOWES": "8c381810-baf7-4ebe-a5f2-13c28b1ec7a4",
    },
    "STAGE": {
        "STAPLES": "3e59b207-cea5-4b00-8035-eed1ae26e566",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "4a00ea0a-ebe2-4a77-8631-800e0daa50c5",
        "M3": "28d04fba-012b-46ee-ab9a-d2909672e70e",
        "CFM": "76c23687-43c4-4fe3-b5f0-4cdd386e7895",
        "WALT'S": "f7c63075-2eb4-4056-9fe7-f403278f253b",
        # "CUB": "12d035f7-16c7-4c02-9b38-f1212b6f92f3",  # not a client anymore
        "CUBPHARMA": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "SHOPRITE-MM": "46474980-b149-4779-b9b5-76ea3d7baa90",
        "SHOPRITE": "397190aa-18ab-4bef-a8aa-d5875d738911",
        "EMPIRE": "09de776e-10cc-437d-9abc-ee5103d3b974",
        "ESSENDANT": "af0db6df-c6fd-4ad3-919c-350501c25bae",
        "DELIVERY SOLUTIONS": "cc2a4805-5b7e-49e1-80a1-a62cf906214d",  # ,
        # "LOWES": "",  # doesn't have a stage org so far
    },
}


def print_array_items(array):
    """
    Prints the items in the array in a formatted manner.

    Parameters:
    - array (list): The array containing the items to be printed.

    Returns:
    None
    """
    divisor = 4

    for i in range(len(array)):
        item = array[i] + "   "
        if 0 < i < len(array) and (i + 1) % divisor == 0:
            item += "\n"
        print(f"{item}", end="")
    print()


def select_env():
    """
    Prompts the user to select an environment.

    Returns:
    str: The selected environment.
    """
    envs = ["PROD", "STAGE"]
    env = ""

    print("SELECT THE ENV")
    print(f"Options: {'   '.join(envs)}")

    while env not in envs:
        env = str(input("> ")).upper().strip()

    return env


def select_org(env):
    """
    Prompts the user to select an organization based on the selected environment.

    Parameters:
    - env (str): The selected environment.

    Returns:
    str: The selected organization ID.
    """
    orgs = list(ORGS[env].keys())
    org = ""

    print(f"SELECT THE ORG ({env})")
    print("Options: ")
    print_array_items(orgs)

    while org not in orgs:
        org = str(input("> ")).upper().strip()

    return ORGS[env][org]  # returns orgId


def load_data_from_file(file_name):
    """
    Loads data from an Excel file.

    Parameters:
    - file_name (str): The name of the Excel file.

    Returns:
    pandas.DataFrame: The loaded data.
    """
    data = pandas.read_excel(file_name)
    return data


def get_packages_details(env, org_id, key_type, key):
    """
    Retrieves package details based on the provided parameters.

    Parameters:
    - env (str): The environment code used to construct the request URL.
    - org_id (str): The organization ID associated with the packages.
    - key_type (str): The type of key used to retrieve the packages.
    - key (str): The key value used to retrieve the packages.

    Returns:
    dict: The package details.
    """
    endpoint = f"http://switchboard.{env}.milezero.com/switchboard-war/api/package?keyType={key_type}&keyValue={key}&orgId={org_id}&includeCancelledPackage=true"

    print(f"Retrieving Packages From {key_type.upper()} {key}")

    return requests.get(endpoint, timeout=15).json()


def get_packages_histories(env, org_id, key_type, key):
    """
    Retrieves package histories based on the provided parameters.

    Parameters:
    - env (str): The environment code used to construct the request URL.
    - org_id (str): The organization ID associated with the packages.
    - key_type (str): The type of key used to retrieve the packages.
    - key (str): The key value used to retrieve the packages.

    Returns:
    dict: The package histories.
    """
    endpoint = f"https://switchboard.{env}.milezero.com/switchboard-war/api/package/histories?keyValue={key}&keyType={key_type}&orgId={org_id}&orderBy=timestamp"

    print(f"Retrieving Histories From {key_type.upper()} {key}")

    return requests.get(endpoint, timeout=15).json()


def get_timestamp_as_string(timestamp):
    """
    Converts a timestamp to a string format.

    Parameters:
    - timestamp (str): The timestamp to be converted.

    Returns:
    str: The converted timestamp as a string.
    """
    try:
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
            "%H:%M:%S"
        )
    except Exception:
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M:%S")


def main():
    """
    Serves as the entry point for processing data from an Excel file. It prompts the user to select an environment and organization, loads the data from the file, and iterates over each row to retrieve package information based on the barcode and post date.

    The function first checks if the post date is valid. If it is, the function retrieves the package details for the given environment, organization, barcode, and post date. If multiple packages are found, it selects the package based on the matching post date in the planning details. If only one package is found, it retrieves the package history and looks for the first "RECEIVED" event, extracting the receive scan timestamp.

    The receive scan timestamps are stored in a list and assigned to the "Receive Scan" column in the data. Finally, the modified DataFrame is saved back to the Excel file.

    Parameters:
    None

    Returns:
    None
    """
    file_name = "packages.xlsx"
    env = select_env()
    org_id = select_org(env)
    data = load_data_from_file(file_name)

    receive_scan_values = []

    for i, row in data.iterrows():
        barcode = row["Barcode"]
        # print(f"{row['Post Date']} {type(row['Post Date'])}")
        post_date = row["Post Date"]
        if pandas.isnull(post_date) or post_date == pandas.NaT:
            print(f"{post_date} not valid (NaT or null)")
            receive_scan = "N/A"
        else:
            post_date = (
                datetime.strptime(str(post_date), "%Y-%m-%d %H:%M:%S")
                .date()
                .strftime("%Y-%m-%d")
            )

            package_data = get_packages_details(env, org_id, "bc", barcode)[
                "packageRecords"
            ]
            print(f"{len(package_data)} packages found")

            if len(package_data) > 1:
                package = [
                    p
                    for p in package_data
                    if post_date in p["planningDetails"]["plannerRouteId"]
                    or post_date in p["planningDetails"]["originalRouteId"]
                ][0]
            elif len(package_data) == 1:
                package = package_data[0]

                package_history = get_packages_histories(
                    env, org_id, "pi", package["packageId"]
                )["histories"][0]

                events = package_history["histories"]

                print(f"{len(events)} history events")

                receive_event = [
                    event for event in events if event["action"] == "RECEIVED"
                ]

                print(f"{len(receive_event)} RECEIVED events found", end=" ")

                if len(receive_event) >= 1:
                    receive_event = receive_event[0]
                    receive_scan = get_timestamp_as_string(receive_event["timestamp"])

                    print(f"({receive_scan} came first)")
                else:
                    print()
                    receive_scan = "N/A"
            else:
                receive_scan = "Package not found!"
                print(receive_scan)

        receive_scan_values.append(receive_scan)
        print()

    # Assign the receive_scan_values list to the "Receive Scan" column
    data["Receive Scan"] = receive_scan_values

    # Save the modified DataFrame back to a new Excel file
    data.to_excel(file_name, index=False)


if __name__ == "__main__":
    main()
