import json

from getRoutePackages import main
from utils import files, packages, routes, utils

if __name__ == "__main__":
    env = utils.select_env()
    orgId = utils.select_org(env)
    # rts = [
    #     "0a1f2711-0dac-4442-9815-d3129d4944d7",
    #     "2024-03-14T08:00-N04:00-52c9f625-c4e6-4a0d-aa83-8baee215a71f-VRZ-WORKFORCE",
    #     "2024-03-14T08:00-N04:00-5d6e35c0-bc5b-4e2b-a5a0-b01bdde51bec-WKM-WORKFORCE",
    #     "2024-03-14T08:00-N04:00-64554310-66f2-4fdd-963d-157935af9240-LEVITTOWN_LEVG5",
    #     "2024-03-14T08:00-N04:00-d5a38a14-4c06-462f-9e3d-ce92a1f89912-UQQ-WORKFORCE",
    #     "2024-03-14T08:00-N04:00-ef33196c-daaa-41c8-94f0-5982bd7261d1-ZLW-WORKFORCE",
    #     "2e081269-4036-4943-b271-df6ad19c5b00",
    #     "40391e4c-e920-4011-bf34-b04c32db7f48",
    #     "6b1ea4a5-67ab-40db-bc31-2f53c153c14e",
    #     "7dad83d5-df78-4383-abd8-ba6df30bb633",
    #     "81957b8b-816f-42e9-91d4-4e5dba200ad9",
    #     "dept-ROLLOVER-2024-03-14-44432212-8b45-46a0-8d62-9c04b2403610",
    #     "ed4f192c-5807-411e-b1d3-f2b40974b37e",
    #     "f1721753-7a69-40bd-a79a-2e17c434ca0a",
    #     "ffff3fd2-debe-4f36-b614-0bef0e14c2f4",
    #     "fischer-ROLLOVER-2024-03-14-d2e98867-3b36-4421-98ec-11217dbc8668",
    #     "glas-ROLLOVER-2024-03-14-514348fb-a828-4da7-80c1-e19972f890d6",
    #     "lgrngvl-ROLLOVER-2024-03-14-5ce89811-2c8d-4b3b-89fe-2672a06753a7",
    #     "spots-ROLLOVER-2024-03-14-d342110b-5abf-423f-982f-95eb2375e4cd",
    #     "vlsgate-ROLLOVER-2024-03-14-8353a65c-361b-4d80-8189-b909c9dce7ae",
    #     "warwick-ROLLOVER-2024-03-14-b584996b-feef-441d-abb9-797001c4e2fd",
    # ]
    # response = main(env, orgId, rts)

    response = main(env, orgId)
    validRoutes = {}

    # filter empty routes
    for routeId in response.keys():
        pkgs = response[routeId]

        if len(pkgs) > 0:
            validRoutes[routeId] = response[routeId]

    for routeId in validRoutes.keys():
        pkgs = validRoutes[routeId]

        print(f"Committing packages from {routeId}")
        packages.commit_packages(env, orgId, pkgs)

    # then rollback them
    print("Rolling routes back")
    routes.rollback_routes(env, list(validRoutes.keys()))

    # then re-execute them one by one and make sure all packages are already on them
    for routeId in validRoutes.keys():
        pkgs = validRoutes[routeId]

        print(f"Re-executing route {routeId}")
        routes.execute_route(env, orgId, routeId)

        print(f"Moving packages back to {routeId} just in case")
        packages.move_packages_to_route(env, orgId, routeId, validRoutes[routeId])

    # lastly, save data on which routes and which packages the script interacted with to a .json file
    print("results saved in the file below")
    files.save_json_to_file(
        json.dumps(
            validRoutes,
            indent=2,
        ),
        "ROUTES_COMMITTED",
    )
