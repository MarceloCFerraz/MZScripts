import requests
from utils import files
from datetime import datetime
import csv


def get_all_packages_on_route(env, routeId):
    """
    Retrieves all packages on a specific route.

    This function takes the environment and route ID as parameters and constructs the URL to retrieve the packages on the specified route. It sends a GET request to the URL and returns the response as JSON.

    Parameters:
    - env (str): The environment (e.g., "prod").
    - routeId (int): The ID of the route.

    Returns:
    - response (dict): The response containing the packages on the specified route.
    """
    url = f"http://sortationservices.{env}.milezero.com/SortationServices-war/api/package/route/{routeId}"

    response = requests.get(url=url, timeout=120).json()

    return response


def save_data_to_file(writer, pkgs, route):
    """
    Saves package data to a file.

    This function takes a writer object, a list of packages, and the route ID. It iterates over each package, retrieves the necessary data (order reference number, shipment barcode, and package ID), and writes it to the file using the writer object.

    Parameters:
    - writer (csv.writer): The writer object to write the data to the file.
    - pkgs (list): A list of packages.
    - route (int): The ID of the route.

    Returns:
    - None
    """
    for pkg in pkgs:
        ori = pkg.get("orderRefNumber")
        bc = pkg.get("shipmentBarcode")
        pid = pkg.get("packageID")

        writer.writerow([route, ori, bc, pid])


def main():
    """
    Retrieves and saves package data from multiple routes.

    This function sets the environment to "prod" and retrieves the routes from a file using the `get_data_from_file()` function. It generates a result file name based on the current timestamp. It opens the result file in write mode and creates a writer object. It writes the header row to the file. For each route, the function retrieves all packages using the `get_all_packages_on_route()` function and saves the package data to the file using the `save_data_to_file()` function. Finally, it prints a success message indicating that the file has been saved.

    Parameters:
    - None

    Returns:
    - None
    """
    env = "prod"
    routes = files.get_data_from_file("routes")
    resultFileName = f"Packages From Routes {str(datetime.now().time().replace(microsecond=0)).replace(':', '-')}.csv"

    with open(resultFileName, "w", newline="") as resultFile:
        writer = csv.writer(resultFile)
        writer.writerow(["Route ID", "Order ID", "Barcode", "Package ID"])

        for route in routes:
            pkgs = get_all_packages_on_route(env, route)
            save_data_to_file(writer, pkgs, route)
    # with thread.ThreadPoolExecutor() as pool:
    #             pool.submit(save_data_to_file, writer, pkgs, route)
    # pool.shutdown(wait=True)

    print(f"File {resultFileName} saved sucessfully!")


main()
