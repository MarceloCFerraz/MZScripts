import requests

from utils import utils


def rollback_routes(env, routes):
    """ """
    url = f"http://alamo.{utils.convert_env(env)}.milezero.com/alamo-war/api/plannedroutes/rollback"
    body = {
        "routeIds": routes,
        "requestor": {
            "associateId": "MZSupportScript",
            "associateName": "MZSupportScript",
            "associateType": "MZSupportScript",
        },
    }
    response = requests.post(url=url, json=body, timeout=15)

    print("> OK" if response.status_code < 400 else f"> FAIL\n{response.text}")

    return response


def execute_route(env, org_id, routeId):
    """ """
    url = f"http://alamo.{utils.convert_env(env)}.milezero.com/alamo-war/api/plannedroutes/{org_id}/execute"
    body = {
        "routeId": routeId,
        "externalRouteName": "string",
        "requestor": {
            "associateId": "MZSupportScript",
            "associateName": "MZSupportScript",
            "associateType": "MZSupportScript",
        },
    }
    response = requests.post(url=url, json=body, timeout=15)

    print("> OK" if response.status_code < 400 else f"> FAIL\n{response.text}")

    return response


def get_all_routes_from_hub_sortation(env, orgId, hubName, cpt):
    """
    Retrieves all routes from a specific hub.

    Args:
        env (str): The environment.
        orgId (str): The organization ID.
        hubName (str): The hub name.
        cpt (str): Date and time in the format 'YYYY-MM-DDTHH:MM:SSZ'.

    Returns:
        list: The list of routes from the hub.
    """
    url = f"http://sortationservices.{utils.convert_env(env)}.milezero.com/SortationServices-war/api/route/list/routes/{orgId}/{hubName}/{str(cpt).replace(':', '%3A')}"

    print(f">> Gathering all routes from {hubName} ({cpt}) using Sortation Services")

    return requests.get(url=url, timeout=15).json()


def get_all_routes_from_hub_alamo(env, orgId, hubName, cpt):
    """
    Retrieves all routes from a specific hub.

    Args:
        env (str): The environment.
        orgId (str): The organization ID.
        hubName (str): The hub name.
        cpt (str): Date and time in the format 'YYYY-MM-DDTHH:MM:SSZ'.

    Returns:
        list: The list of routes from the hub.
    """
    url = f"http://alamo.{utils.convert_env(env)}.milezero.com/alamo-war/api/routes/search/orgId/{orgId}?key={hubName}&keyType=HUB_NAME&localDate={cpt}"

    print(f">> Gathering all routes from {hubName} ({cpt}) using Alamo")

    return requests.get(url=url, timeout=15).json()


def find_route(env, orgId, routeName, hubName, cpt):
    """
    Finds a specific route by name or ID from a hub.

    Args:
        env (str): The environment.
        orgId (str): The organization ID.
        routeName (str): The name or ID of the route to find.
        hubName (str): The hub name.
        cpt (str): Date and time in the format 'YYYY-MM-DDTHH:MM:SSZ'.

    Returns:
        list: The list of routes matching the name or ID.
    """
    allRoutes = get_all_routes_from_hub_alamo(env, orgId, hubName, cpt)
    allRoutes = allRoutes.get("routes")

    if allRoutes is not None:
        allRoutes = [r for r in allRoutes if route_found(routeName, r["metadata"])]
    else:
        print(">> Routes not found. Please review the inputs:")
        print(f">> Org ID: {orgId}")
        print(f">> HUB: {hubName}")
        print(f">> Route Name: {routeName}")
        print(f">> Date: {cpt}")
        allRoutes = []

    print(f">> {len(allRoutes)} matching routes")

    return allRoutes[0]["metadata"] if len(allRoutes) > 0 else None


def route_found(searched_route_name, route):
    """
    Compares the route names (1st param) with the route id and route name.

    Parameters:
        searched_route_name (str): the route name from the user input
        route (dict): the route metadata from alamo's GET /routes/search/orgId/{orgId}
    Returns:
        True: if searched_route_name is present either in the route's name or id
        False: otherwise
    """
    searched_route_name = str(searched_route_name).strip().lower()
    route_name = str(route["routeName"]).strip().lower()
    # route_id = str(route["routeId"]).strip().lower()

    if searched_route_name == route_name:
        return True
    # if searched_route_name in route_id:
    #     return True

    return False


def get_route_events(env, routeId):
    url = f"http://alamo.{utils.convert_env(env)}.milezero.com/alamo-war/api/plannedroutes/{routeId}/events"

    return requests.get(url=url, timeout=15).json().get("events")


def get_stop_details(env, route_id):
    url = f"http://alamo.{utils.convert_env(env)}.milezero.com/alamo-war/api/plannedroutes/stopdetails/{route_id}"

    return requests.get(url=url).json()
