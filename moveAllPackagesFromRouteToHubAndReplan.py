from datetime import datetime
from utils import utils, packages, routes


def main():
    userName = input("What is your name?\n> ").strip()
    dispatcher = input("Who requested this change?\n> ").strip()

    env = utils.select_env()
    orgId = utils.select_org(env)

    oldHub = input("Type the CURRENT hub name (only numbers)\n> ").strip()
    routeName = input("Type the desired route name\n> ").strip().upper()

    cpt = datetime.strptime(
        input("Type date to look for the route (yyyy-mm-dd)\n> ").strip(),
        "%Y-%m-%d"
    )
    cpt = cpt.strftime("%Y-%m-%d") + "T16:00:00Z"
    
    
    route = routes.find_route(env, orgId, routeName, oldHub, cpt)
    pids = []

    if len(route) == 0:
        print("Route Not Found!")
    else:
        pkgs = packages.get_all_packages_on_route(env, orgId, route[0]['routeId'])

        if len(pkgs) > 0:
            newHub = input("Type the NEW hub name (only numbers)\n> ").strip()

            print("Moving Packages...")
            for package in pkgs:
                packages.move_package_to_hub(env, orgId, newHub, package['packageID'], dispatcher, userName)

            newDate = datetime.strptime(
                input("Type date for replan (yyyy-mm-dd)\n> ").strip(),
                "%Y-%m-%d"
            )
            newDate = newDate.strftime("%Y-%m-%d")

            SUCCESSES = []
            ERRORS = []

            print("Replanning packages...")
            for package in pkgs:
                package = packages.get_packages_details(env, orgId, "pi", package['packageID'])['packageRecords'][0]

                hub = package['packageDetails']['sourceLocation']['name']

                if hub == newHub:
                    status = package["packageStatuses"]["status"]

                    if status == "CANCELLED":
                        packages.revive_package(env, package)

                    if status == "DELIVERED" or status == "REJECTED":
                        packages.mark_package_as_delivery_failed(env, package)

                    response = packages.resubmit_package(
                        env,
                        orgId,
                        package['packageId'],
                        newDate
                    )

                    for s in response["SUCCESSES"]:
                        SUCCESSES.append(s)
                    for e in response["ERRORS"]:
                        ERRORS.append(e)
                else:
                    print(f"{package['packageId']} not in {newHub} ({hub})")
                    ERRORS.append(package['packageId'])
            
            print("Successful Resubmits ({}/{}): ".format(len(SUCCESSES), len(SUCCESSES) + len(ERRORS)))
            for success in SUCCESSES:
                print("> {}".format(success))

            print("Unsuccessful Resubmits ({}/{}): ".format(len(ERRORS), len(SUCCESSES) + len(ERRORS)))
            for error in ERRORS:
                print("> {}".format(error))


main()
