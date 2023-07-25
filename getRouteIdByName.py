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

    routes = routes.get_all_routes_from_hub(env, orgId, hubName, cpt)
    
    route = [r for r in routes if routeName in r['routeName'] or routeName in r['routeId']]

    if len(route) == 0:
        print("No Route Found")
    else:
        print(f"Route Found: {route[0]['routeId']}")


main()