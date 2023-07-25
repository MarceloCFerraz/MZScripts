import requests


def get_all_routes_from_hub(env, orgId, hubName, cpt):
    url = f"http://sortationservices.{env}.milezero.com/SortationServices-war/api/route/list/routes/{orgId}/{hubName}/{str(cpt).replace(':', '%3A')}"

    print(f">> Gathering all routes from {hubName}")

    return requests.get(url=url, timeout=15).json()
