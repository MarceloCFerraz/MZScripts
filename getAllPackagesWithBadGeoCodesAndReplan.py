from datetime import datetime

import pandas

from utils import hubs, locations, packages, utils

SUCCESSES = []
ERRORS = []


def get_valid_hubs(hubs):
    """
    Filters out the valid hubs from the given list of hubs.

    This function takes a list of hubs and checks if the name of each hub is numeric. If it is, the hub is considered valid and added to the list of valid hubs.

    Parameters:
    - hubs (list): A list of hubs.

    Returns:
    - validHubs (list): A list of valid hubs.
    """
    validHubs = []

    for hub in hubs:
        if str(hub["name"]).isnumeric():
            validHubs.append(hub)

    return validHubs


def main():
    """
    Retrieves and processes packages with bad geo codes.

    This function prompts the user to select the environment and organization ID. It then prompts the user to input the original date. The function retrieves all hubs for the selected environment and organization ID. It filters out the valid hubs using the `get_valid_hubs()` function. The function prints the number of hubs found and the number of valid hubs. It then searches for packages in each valid hub that have bad geo codes. For each package found, the function retrieves the package details and the corresponding location details. It checks if the location precision is not "EXACT" and adds the package information to a DataFrame. The function saves the DataFrame as an .xlsx file. It then resubmits each package with the new date. The function prints the number of succeeded and failed resubmits, along with the details of each.

    Parameters:
    - None

    Returns:
    - None
    """
    newDate = datetime.min

    env = utils.select_env()
    orgId = utils.select_org(env)

    oldDate = datetime.strptime(
        input("Input the Original Date (yyyy-mm-dd): ").strip(), "%Y-%m-%d"
    )
    oldDate = oldDate.strftime("%Y-%m-%d")
    oldDate = str(oldDate + "T16:00:00Z")
    oldDate = oldDate.replace(":", "%3A")

    hbs = hubs.get_all_hubs(env, orgId)

    validHubs = get_valid_hubs(hbs)
    hubsCount = len(hbs)

    print(f"{hubsCount} hubs found ({len(validHubs)} valid)")
    print("Searching for packages...")

    pkgs = []

    for hub in validHubs:
        hubName = hub["name"]
        print(f"> {hubName}")

        hubPackages = packages.get_all_packages_for_hub(env, orgId, hubName, oldDate)

        # this needs to be done in order to add all packages from all hubs to the array
        for packageID in hubPackages:
            pkgs.append(packageID)

    print(f"{len(pkgs)} packages found!\n")

    if len(pkgs) > 0:
        newDate = oldDate

        dt = []
        hb = []
        bc = []
        pi = []
        li = []
        cstm = []
        addr = []
        geo = []
        prc = []

        print("Searching for badly geo coded packages...")
        for packageID in pkgs:
            pkg = packages.get_package_details(env, orgId, "pi", packageID)[
                "packageRecords"
            ][0]

            try:
                hubName = pkg["packageDetails"]["sourceLocation"]["name"]
            except Exception:
                try:
                    hubName = pkg["packageDetails"]["clientHub"]
                except Exception:
                    try:
                        hubName = pkg["packageDetails"]["destination"]["name"]
                    except Exception:
                        hubName = "not found"

            locId = pkg["orderDetails"]["customerLocationId"]

            location = locations.get_location(env, locId)

            try:
                if location["precision"]["precision"] != "EXACT":
                    dt.append(oldDate)
                    hb.append(hubName)
                    bc.append(pkg["packageDetails"]["shipmentBarcode"])
                    pi.append(pkg["packageId"])
                    li.append(li)
                    cstm.append({location["name"]})
                    addr.append(
                        f"{location['typedAddress']['address1']}, {location['typedAddress']['address2']}, {location['typedAddress']['city']}, {location['typedAddress']['state']}, {location['typedAddress']['postalCode']}"
                    )
                    geo.append(
                        f"{location['geo']['latitude']}, {location['geo']['longitude']}"
                    )
                    prc.append(location["precision"]["precision"])
            except Exception as e:
                print("Found an error with this location:")
                print(e)

        print(f"Found {len(pi)} packages.")

        df = pandas.DataFrame()
        df["Date"] = dt
        df["Hub"] = hb
        df["Barcode"] = bc
        df["Package ID"] = pi
        df["Customer"] = cstm
        df["Address"] = addr
        df["Location ID"] = li
        df["Geo Code"] = geo
        df["Precision"] = prc

        print("Saving data into .xlsx file")

        df.to_excel("Packages With Bad Geo Codes.xlsx", index=False)

        for packageID in pi:
            response = packages.resubmit_package(env, orgId, packageID, newDate)

            for s in response["SUCCESSES"]:
                SUCCESSES.append(s)
            for e in response["ERRORS"]:
                ERRORS.append(e)

        succeededResubmits = len(SUCCESSES)
        failedResubmits = len(ERRORS)
        totalResubmits = succeededResubmits + failedResubmits

        print(f"({succeededResubmits}/{totalResubmits}) succeeded:")
        for s in SUCCESSES:
            print(s)
        print(f"({failedResubmits}/{totalResubmits}) failed:")
        for e in ERRORS:
            print(e)

    else:
        print("0 Packages found. Finishing script")


main()
