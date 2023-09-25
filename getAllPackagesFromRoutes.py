import requests
from utils import files
from datetime import datetime
import concurrent.futures as thread
import csv


def get_all_packages_on_route(env, routeId):
    url = f"http://sortationservices.{env}.milezero.com/SortationServices-war/api/package/route/{routeId}"

    response = requests.get(url=url, timeout=120).json()

    return response


def save_data_to_file(writer, pkgs, route):
    for pkg in pkgs:
        ori = pkg.get('orderRefNumber')
        bc = pkg.get('shipmentBarcode')
        pid = pkg.get('packageID')
        
        writer.writerow([route, ori, bc, pid])



def main():
    env = "prod"
    routes = files.get_data_from_file("routes")
    resultFileName = f"Packages From Routes {str(datetime.now().time().replace(microsecond=0)).replace(':', '-')}.csv"

    with open (resultFileName, 'w', newline='') as resultFile:
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
