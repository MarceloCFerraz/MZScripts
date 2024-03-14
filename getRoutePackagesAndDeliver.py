import json
from concurrent.futures import ThreadPoolExecutor

from getRoutePackages import main
from utils import files, packages, utils

if __name__ == "__main__":
    env = utils.select_env()
    orgId = utils.select_org(env)

    response = main(env, orgId)

    print("Marking all packages delivered")
    with ThreadPoolExecutor() as pool:
        for pid in response["uniquePackages"]:
            pool.submit(packages.mark_package_as_delivered, env, orgId, pid)

    print("results saved in the file below")
    files.save_json_to_file(
        json.dumps(
            {
                "routeId": response["routeId"],
                "packages": response["uniquePackages"],
            },
            indent=2,
        ),
        f"ROUTE_DELIVERED_{response['routeId']}",
    )
