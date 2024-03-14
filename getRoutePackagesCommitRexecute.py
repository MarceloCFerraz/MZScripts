import json

from getRoutePackages import main
from utils import files, packages, routes, utils

if __name__ == "__main__":
    env = utils.select_env()
    orgId = utils.select_org(env)

    response = main(env, orgId)

    print("Committing packages")
    packages.commit_packages(env, orgId, response["uniquePackages"])

    print("Rolling route back")
    routes.rollback_routes(env, [response["routeId"]])

    print("Re-executing route")
    routes.execute_route(env, orgId, response["routeId"])

    print("move packages back to route just in case")
    packages.move_packages_to_route(
        env, orgId, response["routeId"], response["uniquePackages"]
    )

    print("results saved in the file below")
    files.save_json_to_file(
        json.dumps(
            {
                "routeId": response["routeId"],
                "packages": response["uniquePackages"],
            },
            indent=2,
        ),
        f"ROUTE_COMMITTED_{response['routeId']}",
    )
