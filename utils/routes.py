import requests


def get_all_routes_from_hub(env, orgId, hubName, cpt):
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
    url = f"http://sortationservices.{env}.milezero.com/SortationServices-war/api/route/list/routes/{orgId}/{hubName}/{str(cpt).replace(':', '%3A')}"

    print(f">> Gathering all routes from {hubName}")

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
    allRoutes = get_all_routes_from_hub(env, orgId, hubName, cpt)
    
    return [r for r in allRoutes if routeName in r['routeName'] or routeName in r['routeId']]
