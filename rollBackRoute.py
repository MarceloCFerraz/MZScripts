from utils import utils
import requests


def rollback_route(env, routeId, userName):
    url = f"http://alamo.{env}.milezero.com/alamo-war/api/plannedroutes/rollback"

    payload = {
        "routeIds": [
            routeId
        ],
        "requestor": {
            "associateId": userName,
            "associateName": userName,
            "associateType": "Support"
        }
    }

    response = requests.post(url=url, json=payload, timeout=15)

    return response


def main():
    env = utils.select_env()
    routeId = input("Type the routeId:\n> ")
    userName = input("Type your name:\n> ")

    response = rollback_route(env, routeId, userName)

    print('OK' if response.status_code < 400 else 'FAILED')
    print(response.text)


main()
