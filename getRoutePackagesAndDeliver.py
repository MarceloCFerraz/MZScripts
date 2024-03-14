import json
from concurrent.futures import ThreadPoolExecutor

from getRoutePackages import main
from utils import files, packages, utils

if __name__ == "__main__":
    env = utils.select_env()
    orgId = utils.select_org(env)
    # rts = [""] # you can add route ids you already have in here.
    # response = main(env, orgId, rts)

    response = main(env, orgId)
    validRoutes = {}

    # filter empty routes
    for routeId in response.keys():
        pkgs = response[routeId]

        if len(pkgs) > 0:
            print(f"Marking all packages from {routeId} as delivered")

            with ThreadPoolExecutor() as pool:
                for pid in response["uniquePackages"]:
                    pool.submit(packages.mark_package_as_delivered, env, orgId, pid)
            pool.shutdown(True)

            validRoutes[routeId] = response[routeId]

    # lastly, save data on which routes and which packages the script interacted with to a .json file
    print("results saved in the file below")
    files.save_json_to_file(
        json.dumps(
            validRoutes,
            indent=2,
        ),
        "ROUTES_DELIVERED_",
    )
