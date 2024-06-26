from datetime import datetime

from utils import routes, utils


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
        input("Type in the desired date (yyyy-mm-dd)\n> ").strip(), "%Y-%m-%d"
    )
    cpt = cpt.strftime("%Y-%m-%d")
    routeName = input("Type the desired route name\n> ").strip()

    route = routes.find_route(env, orgId, routeName, hubName, cpt)

    if route is None:
        print("No Route Found")
    else:
        print(f"Route Found: {route['routeId']}")


main()
