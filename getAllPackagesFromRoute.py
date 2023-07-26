import requests
from utils import files, utils, packages, routes
from datetime import datetime


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

    allRoutes = routes.get_all_routes_from_hub(env, orgId, hubName, cpt)
    
    route = [r for r in allRoutes if routeName in r['routeName'] or routeName in r['routeId']]
    pids = []

    if len(route) == 0:
        print("No Route Found")
    else:
        pkgs = packages.get_all_packages_on_route(env, orgId, route[0]['routeId'])
        
        for package in pkgs:
            pids.append(package['packageID'])

        print(f"Saving packageIDs to file 'pids.txt'")
        
        files.save_package_ids_to_file(pids, "pids.txt")


main()