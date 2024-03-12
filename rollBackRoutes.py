import requests

from utils import files, utils


def rollback_route(env, routeIds, userName):
    url = f"http://alamo.{utils.convert_env(env)}.milezero.com/alamo-war/api/plannedroutes/rollback"

    payload = {
        "routeIds": routeIds,
        "requestor": {
            "associateId": userName,
            "associateName": userName,
            "associateType": "Support",
        },
    }

    response = requests.post(url=url, json=payload, timeout=15)

    return response


def main():
    env = utils.select_env()
    userName = input("Type your name:\n> ")
    routeIds = files.get_data_from_file("routes")

    response = rollback_route(env, routeIds, userName)

    print("OK" if response.status_code < 400 else "FAILED")
    print(response.text)


main()
