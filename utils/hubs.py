import requests


def search_hubs(env, orgId):
    url = f"http://cromag.{env}.milezero.com/retail/api/hubs/org/{orgId}?hubType=HUB"

    return requests.get(url=url, timeout=5).json()["hubs"]


def search_hub_by_name(env, orgId, hubName):
    url = f"http://cromag.{env}.milezero.com/retail/api/hubs/org/{orgId}?hubType=HUB&keyType=name&key={hubName}"

    response = requests.get(url=url, timeout=5).json()["hubs"]
    # print(response)

    return response


def search_hub_by_id(env, orgId, hubId):
    url = f"http://cromag.{env}.milezero.com/retail/api/hubs/org/{orgId}?hubType=HUB&keyType=id&key={hubId}"

    return requests.get(url=url, timeout=5).json()["hubs"]


def get_all_hubs(env, orgId):
    endpoint = f"http://cromag.{env}.milezero.com/retail/api/hubs/org/{orgId}"

    return requests.get(url=endpoint, timeout=10).json()["hubs"]
