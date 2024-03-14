from datetime import datetime

from utils import files, packages, routes, utils


def main():
    """
    Retrieves package IDs from a specific route and saves them to a file.

    This function prompts the user to select the environment and organization ID. It then prompts the user to input the hub (only numbers), the desired date (in the format "yyyy-mm-dd"), and the desired route name. The function retrieves all routes from the specified hub and date. It filters the routes based on the specified route name. If no routes are found, it prints a "No Route Found" message. Otherwise, it retrieves all packages on the first matching route. It saves the package IDs to a file named "pids.txt". Finally, it prints a success message indicating that the package IDs have been saved.

    Parameters:
    - None

    Returns:
    - None
    """
    env = utils.select_env()
    orgId = utils.select_org(env)
    hubName = input("Type the hub (only numbers)\n> ").strip()
    cpt = datetime.strptime(
        input("Type in the desired date (yyyy-mm-dd)\n> ").strip(), "%Y-%m-%d"
    )
    cpt = cpt.strftime("%Y-%m-%d")
    routeName = input("Type the desired route name\n> ").strip().lower()

    route = routes.find_route(env, orgId, routeName, hubName, cpt)

    if not route:
        print("No Route Found")
    else:
        pids = []
        pkgs = packages.get_route_packages_sortation(env, orgId, route["routeId"])

        for package in pkgs:
            pids.append(package["packageID"])

        print("Saving packageIDs to file 'pids.txt'")

        files.save_package_ids_to_file(pids, "pids.txt")


main()
main()
