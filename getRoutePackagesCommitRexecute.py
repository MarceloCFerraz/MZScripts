from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from utils import itineraries, packages, routes, utils

ITINERARIES = {}


def get_itinerary_packages_and_stops(env, orgId, itinerary):
    pkgs_and_stops = itineraries.get_itinerary_packages_and_stops(env, orgId, itinerary)

    ITINERARIES[itinerary] = {"pkgsAndStops": pkgs_and_stops, "uniquePackages": set()}

    print(
        f">> {itinerary} have {len(pkgs_and_stops['loadedPackages'])} packages "
        # TODO: fetch switchboard to check package status
        # + f"({len(pkgs_and_stops['deliveredPackages'])} delivered) and "
        + f"{len(pkgs_and_stops['deliveryStops'])} stops"
    )

    for pkg in pkgs_and_stops["loadedPackages"]:
        ITINERARIES[itinerary]["uniquePackages"].add(pkg)


def fetch_itineraries(events):
    print(">> Fetching itineraries in Route Events")
    itineraries = []

    notes = [
        e["notes"] for e in events if "done. itinerary ids" in str(e["notes"]).lower()
    ]

    if len(notes) > 0:
        for note in notes:
            start = str(note).find("[")
            end = str(note).find("]")

            itineraries.append(
                str(note)[
                    start + 1 : end
                ].strip()  # Gets [ >> fac1ab60-fd7a-4ff9-8798-e9167060295c << ] or "" it there is no itinerary id
            )

    return itineraries


def get_route_from_user(env, orgId):
    answer = utils.select_answer("> Do you have a routeId? ")
    routeId = None

    if answer == "Y":
        routeId = input("> Input the route ID: ")
    else:
        while routeId is None:
            hubName = input("Type the hub (only numbers)\n> ").strip()
            cpt = datetime.strptime(
                input("Type in the date (yyyy-mm-dd)\n> ").strip(), "%Y-%m-%d"
            )
            cpt = cpt.strftime("%Y-%m-%d")
            routeName = input("Type the route name\n> ").strip()

            route = routes.find_route(env, orgId, routeName, hubName, cpt)

            if route is None:
                print(">> Route not Found, please try again\n")
                print("--------------------------------")
            else:
                routeId = route["routeId"]
                print(f">> Route found: {routeId}")

    return routeId


def no_itinerary_generated(itinerary_ids):
    return len([i for i in itinerary_ids if str(i).strip() != ""]) == 0


def print_itineraries(itinerary_ids):
    if no_itinerary_generated(itinerary_ids):
        print(
            f">> Found {len(itinerary_ids)} itineraries: {' '.join([f'[{iti}]' for iti in itinerary_ids])}"
        )
    else:
        print(
            f">> Found {len(itinerary_ids)} 'done' events, but OEGR have generated 0 itineraries"
            + f"\n>> {' '.join([f'[{iti}]' for iti in itinerary_ids])}"
        )


def sync_itineraries_and_response(response, itinerary_ids):
    for itinerary in itinerary_ids:
        response["itineraries"].append(ITINERARIES[itinerary].get("pkgsAndStops"))
        for pkg in ITINERARIES[itinerary]["uniquePackages"]:
            response["uniquePackages"].add(pkg)

    response["uniquePackages"] = list(response["uniquePackages"])
    print(
        f"\n>> Total unique packages accross valid itineraries: {len(response['uniquePackages'])}"
    )

    return response


def process_itineraries(env, orgId, itinerary_ids):
    response = {"routeId": routeId, "itineraries": [], "uniquePackages": set()}

    # get all the data for each of them concurrently / in parallel

    print("Fetching itinerary data with Thread Pool")
    with ThreadPoolExecutor() as pool:
        for itinerary in itinerary_ids:
            print(f"\n>> Checking itinerary '{itinerary}'")

            if str(itinerary).strip() != "":
                pool.submit(
                    get_itinerary_packages_and_stops,
                    env,
                    orgId,
                    itinerary,
                )
    pool.shutdown(True)

    response = sync_itineraries_and_response(response, itinerary_ids)

    return response


if __name__ == "__main__":
    env = utils.select_env()
    orgId = utils.select_org(env)

    routeId = get_route_from_user(env, orgId)
    events = routes.get_route_events(env, routeId)

    if events is not None:
        itinerary_ids = fetch_itineraries(events)

        print_itineraries(itinerary_ids)
        if not no_itinerary_generated(
            itinerary_ids
        ):  # if at least one itinerary was generated
            response = process_itineraries(env, orgId, itinerary_ids)

            print("Committing packages")
            packages.commit_packages(env, orgId, response["uniquePackages"])

            print("Rolling route back")
            routes.rollback_routes(env, [routeId])

            print("Re-executing route")
            routes.execute_route(env, orgId, routeId)

            print("move packages back to route just in case")
            packages.move_packages_to_route(
                env, orgId, routeId, response["uniquePackages"]
            )
