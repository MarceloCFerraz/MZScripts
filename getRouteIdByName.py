import requests
from utils import files, utils, packages, routes
from datetime import datetime


def route_found(desired_route_name, route):
    """
    Compares the route names (1st param) with the route id and route name.

    Parameters:
        desired_route_name (str): the route name from the user input
        route (dict): the route metadata from alamo's GET /routes/search/orgId/{orgId}
    Returns:
        True: if desired_route_name is present either in the route's name or id
        False: otherwise
    """
    route_name = str(route)['routeName'].strip().lower()
    route_id = str(route)['routeId'].strip().lower()

    return desired_route_name in route_name or desired_route_name in route_id


def main():
    """
    The main function for route search.

    This function serves as the entry point for searching routes. It prompts the user to select the environment, organization ID, hub name, desired date, and route name. It then calls the necessary functions from the `utils` and `routes` modules to retrieve the routes and search for the desired route based on the provided inputs.

    Parameters:
    None

    Returns:
    None
    """
    env = utils.select_env()
    orgId = utils.select_org(env)
    hubName = input("Type the hub (only numbers)\n> ").strip()
    cpt = datetime.strptime(
        input("Type in the desired date (yyyy-mm-dd)\n> ").strip(),
        "%Y-%m-%d"
    )
    cpt = cpt.strftime("%Y-%m-%d")
    routeName = input("Type the desired route name\n> ").strip()

    route = routes.find_route(env, orgId, routeName, hubName, cpt)
  
    if route == None:
        print("No Route Found")
    else:
        print(f"Route Found: {route['routeId']}")


main()