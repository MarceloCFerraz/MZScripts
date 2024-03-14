from datetime import datetime

import replanPackages
from utils import files, packages, routes, utils


def main():
    """
    The main function that prompts the user for their name, dispatcher's name, and other necessary information. It then performs various operations, such as searching for a route, moving packages to a new hub, and performing package replanning.

    Parameters:
    - None

    Returns:
    None
    """
    userName = input("What is your name?\n> ").strip()
    dispatcher = input("Who requested this change?\n> ").strip()

    env = utils.select_env()
    orgId = utils.select_org(env)

    oldHub = input("Type the CURRENT hub name\n> ").strip()
    routeName = input("Type the desired route name\n> ").strip().upper()

    cpt = datetime.strptime(
        input("Type date to look for the route (yyyy-mm-dd)\n> ").strip(), "%Y-%m-%d"
    )
    cpt = cpt.strftime("%Y-%m-%d") + "T16:00:00Z"

    route = routes.find_route(env, orgId, routeName, oldHub, cpt)

    if route is None:
        print("Route Not Found!")
    else:
        pkgs = packages.get_route_packages_sortation(env, orgId, route["routeId"])

        if len(pkgs) > 0:
            newHub = input("Type the NEW hub name\n> ").strip()

            files.save_txt_file([pkg.get("packageID") for pkg in pkgs], newHub)

            print("Moving Packages...")
            for package in pkgs:
                packages.move_package_to_hub(
                    env, orgId, newHub, package["packageID"], dispatcher, userName
                )

            newDate = datetime.strptime(
                input("Type date for replan (yyyy-mm-dd)\n> ").strip(), "%Y-%m-%d"
            )
            newDate = newDate.strftime("%Y-%m-%d")

            print("Replanning packages...")
            replanPackages.process_packages(env, orgId, newDate, newHub, pkgs)


main()
