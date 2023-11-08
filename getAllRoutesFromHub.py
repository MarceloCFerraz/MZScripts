from datetime import datetime
from utils import utils, packages, routes, files
import replanPackages


def main():
    """
    The main function that prompts the user for their name, dispatcher's name, and other necessary information. It then performs various operations, such as searching for a route, moving packages to a new hub, and performing package replanning.

    Parameters:
    - None

    Returns:
    None
    """
    env = utils.select_env()
    orgId = utils.select_org(env)

    hub = input("Type the CURRENT hub name\n> ").strip()
    cpt = datetime.strptime(
        input("Type date to look for the route (yyyy-mm-dd)\n> ").strip(),
        "%Y-%m-%d"
    )
    cpt = cpt.strftime("%Y-%m-%d") + "T16:00:00Z"
    
    
    rts = routes.get_all_routes_from_hub(env, orgId, hub, cpt)

    if len(rts) == 0:
        print("Routes Not Found!")
    else:
        for route in rts:
            print(f"{route.get('routeName')} - {route.get('routeId')}")


main()
