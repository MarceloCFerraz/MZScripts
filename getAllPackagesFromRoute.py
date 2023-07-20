import requests
from utils import files, utils, packages
from datetime import datetime


def get_all_routes_from_hub(env, orgId, hubName, cpt):
    url = f"http://sortationservices.{env}.milezero.com/SortationServices-war/api/route/list/routes/{orgId}/{hubName}/{str(cpt).replace(':', '%3A')}"

    print(f">> Gathering all routes from {hubName}")

    return requests.get(url=url, timeout=15).json()


def get_all_packages_on_route(env, orgId, routeId):
    url = f"http://sortationservices.{env}.milezero.com/SortationServices-war/api/monitor/packages/{orgId}/{routeId}"

    print(f">> Searching for packages in {routeId}")

    return requests.get(url=url, timeout=15).json()


def save_package_ids_to_file(packageIDs, fileName):
    with open(fileName, "w") as txt:
        for packageID in packageIDs:
            txt.write(packageID + "\n")


def main():
    env = utils.select_env()
    orgId = utils.select_org(env)
    hubName = input("Type the hub (only numbers)\n> ").strip()
    cpt = datetime.strptime(
        input("Type in the desired date (yyyy-mm-dd)\n> ").strip(),
        "%Y-%m-%d"
    )
    cpt = cpt.strftime("%Y-%m-%d") + "T16:00:00Z"
    routeName = input("Type the desired route name\n> ").strip().upper()

    routes = get_all_routes_from_hub(env, orgId, hubName, cpt)
    
    route = [r for r in routes if routeName in r['routeName'] or routeName in r['routeId']]
    pids = []

    if len(route) == 0:
        print("No Route Found")
    else:
        pkgs = get_all_packages_on_route(env, orgId, route[0]['routeId'])
        
        for package in pkgs:
            pids.append(package['packageID'])

        print(f"Saving packageIDs to file 'pids.txt'")
        
        save_package_ids_to_file(pids, "pids.txt")


main()