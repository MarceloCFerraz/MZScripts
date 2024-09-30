from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import replanPackages
import getRoutePackages
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
        return

    response = getRoutePackages.main(env, orgId, [route])

    for routeId in response.keys:
        pkgIds = response[routeId]

        if len(pkgIds) <= 0:
            continue

        newHub = input("Type the NEW hub name\n> ").strip()

        batches = utils.divide_into_batches(pkgIds)
        pkgs = []

        for batch in batches:
            for pkg in (packages.bulk_get_package_details(env, orgId, "pi", batch)["packageRecords"]):
                pkgs.append(pkg)

        print(f"Moving {len(pkgs)} packages from route {routeId} to {newHub}")

        with ThreadPoolExecutor() as pool:
            for pkg in pkgs:
                packages.move_package_to_hub(
                    env, orgId, newHub, pkg["packageId"], dispatcher, userName
                )
        pool.shutdown(wait=True)

        newDate = datetime.strptime(
            input("Type date for replan (yyyy-mm-dd)\n> ").strip(), "%Y-%m-%d"
        )
        newDate = newDate.strftime("%Y-%m-%d")

        print("Replanning packages...")
        replanPackages.process_packages(env, orgId, newDate, newHub, pkgs)



main()
