import requests

def get_itinerary_data(env, orgId, itineraryId):
    url = f"http://hei.{env}.milezero.com/hei-war/api/v2/itinerary/{orgId}/{itineraryId}?includeExecuted=true&mode=EXECUTION"

    return requests.get(url=url, timeout=15).json()


def get_itinerary_packages(env, orgId, itinerary):

    itinerary = get_itinerary_data(env, orgId, itinerary)
    packageIds = set()

    for task in itinerary["tasks"]:
        for subtask in task["subTasks"]:
            for payload in subtask["payload"]:
                packageIds.add(payload["packageId"])
    
    return list(packageIds)


