# write a script that reads a file with a list of route ids and prints the events for each route

import requests

from utils import files, utils


def get_route_events(env, routeId: str):
    url = f"http://alamo.{utils.convert_env(env)}.milezero.com/alamo-war/api/plannedroutes/{routeId}/events"
    # print(url)
    response = requests.get(url=url, timeout=15)

    if response.status_code >= 400:
        print(str(response.status_code) + ": " + response.text)
        return {}

    return response.json().get("events")


def get_route_events_sortation(env, routeId):
    url = f"http://sortationservices.{utils.convert_env(env)}.milezero.com/SortationServices-war/api/monitor/getRouteEvents/{orgId}/{routeId}"

    response = requests.get(url=url, timeout=15)

    if response.status_code >= 400:
        print(str(response.status_code) + ": " + response.text)
        return {}

    return response.json().get("events")


def is_valid_event(event):
    return event.get("associate") and (
        event["associate"].get("associateId") or event["associate"].get("associateName")
    )


def associate_name_is(event, associateName):
    return (
        event["associate"].get("associateName")
        and event["associate"]["associateName"] == associateName
    )


def associate_id_is(event, associateId):
    return (
        event["associate"].get("associateId")
        and event["associate"]["associateId"] == associateId
    )


# reading events from sortation services
def main(env, orgId, fileName):
    routeIds = files.get_data_from_file(fileName, False)
    events = []
    for routeId in routeIds:
        # response = get_route_events_sortation(env, routeId)
        response = get_route_events(env, routeId)

        if response:
            events.extend(response)

    for event in events:
        if is_valid_event(event) and (
            associate_name_is(event, "Traviss Williams")
            or associate_id_is(event, "43a28241-3d49-4ee4-ae48-bbe4e779bcae")
        ):
            print(
                event["timestamp"] + " - " + event["eventType"] + " - " + event["notes"]
            )


if __name__ == "__main__":
    env = utils.select_env()
    orgId = utils.select_org(env)
    main(env, orgId, "inspectRoutes")
