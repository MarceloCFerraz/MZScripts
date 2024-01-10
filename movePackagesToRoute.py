from datetime import datetime

from utils import files, packages, routes, utils


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
    route_name = str(route["routeName"]).strip().lower()
    route_id = str(route["routeId"]).strip().lower()

    return desired_route_name in route_name or desired_route_name in route_id


def main():
    """
    The main function that retrieves package IDs from a file, prompts for user input, searches for a route, and moves the packages to the specified route.

    Returns:
    None
    """

    fileName = "pids"
    packageIdsList = files.get_data_from_file(fileName)

    # supportMember = input("What is your name?\n> ").strip()

    env = utils.select_env()
    orgId = utils.select_org(env)

    hubName = input("Type in the route's hub name\n> ")
    newRoute = input("Type in the new route name\n> ").strip().upper()
    cpt = datetime.strptime(
        input("Type in the route date (yyyy-mm-dd)\n> ").strip(), "%Y-%m-%d"
    )
    cpt = cpt.strftime("%Y-%m-%d")

    route = routes.find_route(env, orgId, newRoute, hubName, cpt)

    if route is None:
        print("No Route Found")
    else:
        routeId = route["routeId"]
        print(f"Route Found: {routeId}")

        packages.move_packages_to_route(env, orgId, routeId, packageIdsList)


main()
