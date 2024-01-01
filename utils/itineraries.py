import requests

from utils import utils


def get_itinerary_url(env, orgId, itineraryId):
    return f"http://hei.{utils.convert_env(env)}.milezero.com/hei-war/api/v2/itinerary/{orgId}/{itineraryId}?includeExecuted=true&mode=EXECUTION"


def get_itinerary_data(env, orgId, itineraryId):
    url = get_itinerary_url(env, orgId, itineraryId)

    return requests.get(url=url, timeout=15).json()


def get_itinerary_packages_and_stops(env, orgId, itineraryId):
    response = {
        "itineraryId": itineraryId,
        "url": get_itinerary_url(env, orgId, itineraryId),
        "loadedPackages": [],
        "deliveredPackages": set(),
        "deliveryStops": [],
    }

    itinerary = get_itinerary_data(env, orgId, itineraryId)
    package_ids = set()

    for task in itinerary["tasks"]:
        for subtask in task["subTasks"]:
            del_stop = {"taskId": subtask["taskId"], "deliveredPackages": set()}
            add_stop = False

            for payload in subtask["payload"]:
                pid = payload["packageId"]
                package_ids.add(pid)

                if str(subtask["eventName"]).upper() == "DELIVER":
                    response["deliveredPackages"].add(pid)
                    del_stop["deliveredPackages"].add(pid)
                    add_stop = True

            if add_stop:
                # converting all sets to lists because json lib doesn't support sets
                del_stop["deliveredPackages"] = list(del_stop["deliveredPackages"])
                response["deliveryStops"].append(del_stop)

    # converting all sets to lists because json lib doesn't support sets
    response["loadedPackages"] = list(package_ids)
    response["deliveryStops"] = list(response["deliveryStops"])
    response["deliveredPackages"] = list(response["deliveredPackages"])

    return response
