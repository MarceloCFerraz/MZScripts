import sys
from datetime import datetime
from utils import utils, packages, files, routes


def main():
    """
    The main function that retrieves package IDs from a file, prompts for user input, searches for a route, and moves the packages to the specified route.

    Returns:
    None
    """
    SUCCESSES = []
    ERRORS = []

    fileName = "pids" 
    packageIdsList = files.get_data_from_file(fileName)

    # supportMember = input("What is your name?\n> ").strip()

    env = utils.select_env()
    orgId = utils.select_org(env)
    
    hubName = input("Type in the route's hub name\n> ")
    newRoute = input("Type in the new route name\n> ").strip().upper()
    cpt = datetime.strptime(
        input("Type in the route date (yyyy-mm-dd)\n> ").strip(),
        "%Y-%m-%d"
    )
    cpt = cpt.strftime("%Y-%m-%d") + "T16:00:00Z"

    allRoutes = routes.get_all_routes_from_hub(env, orgId, hubName, cpt)
    
    route = [r for r in allRoutes if newRoute in r['routeName'] or newRoute in r['routeId']]

    if len(route) == 0:
        print("No Route Found")
    else:
        routeId = route[0]['routeId']
        print(f"Route Found: {routeId}")

        packages.move_packages_to_route(env, orgId, routeId, packageIdsList)


main()
