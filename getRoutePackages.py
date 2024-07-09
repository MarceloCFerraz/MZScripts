import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from utils import files, itineraries, packages, routes, utils

ITINERARIES = {}


def get_itinerary_packages_and_stops(env, orgId, itinerary, timestamp):
    pkgs_and_stops = itineraries.get_itinerary_packages_and_stops(env, orgId, itinerary)

    ITINERARIES[itinerary] = {"pkgsAndStops": pkgs_and_stops, "uniquePackages": set()}

    # TODO: check why the fuck this is not printing every time.
    print(
        f">> {itinerary} have {len(pkgs_and_stops['loadedPackages'])} packages "
        # TODO: fetch switchboard to check package status
        # + f"{len(pkgs_and_stops['deliveryStops'])} stops "
        + f"({timestamp})"
    )

    for pkg in pkgs_and_stops["loadedPackages"]:
        ITINERARIES[itinerary]["uniquePackages"].add(pkg)


def fetch_itineraries(events):
    print(">> Fetching itineraries in Route Events")
    itineraries = []

    done = [
        e["notes"] for e in events if "done. itinerary ids" in str(e["notes"]).lower()
    ]
    publishing_stamps = [
        e["timestamp"]
        for e in events
        if "publishing to oegr" in str(e["notes"]).lower()
    ]

    if len(done) > 0:
        for i in range(len(done)):
            note = done[i]
            start = str(note).find("[")
            end = str(note).find("]")

            # Gets [ >> fac1ab60-fd7a-4ff9-8798-e9167060295c << ] or "" it there is no itinerary id
            iti = str(note)[start + 1 : end].strip()

            itineraries.append(iti)

    return itineraries, publishing_stamps


def no_itinerary_generated(itinerary_ids):
    return len([i for i in itinerary_ids if str(i).strip() != ""]) == 0


def get_routes(env, orgId):
    routeId = "init"
    rts = set()
    updated = False

    while True:
        print(f"\n>> Routes Selected So Far: {' '.join(rts)}")

        if utils.select_answer(">> Do you want to provide another route?") == "Y":
            print(">> Type the new HUB's name (leave blank and hit enter if done)")

            routeId = get_route_from_user(env, orgId)
            rts.add(routeId)
            updated = True
        elif len(rts) > 0 and updated:  # means the user entered a blank line
            break

    return list(rts)


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
                print(f">> Route found: {routeId}\n")

    return routeId


def print_itineraries(itinerary_ids):
    print(f">> Found {len(itinerary_ids)} itineraries:")
    print(f">> {' '.join([f'[ {iti} ]' for iti in itinerary_ids])}")


def sync_itineraries_and_response(response, itinerary_ids):
    for itinerary in itinerary_ids:
        response["itineraries"].append(ITINERARIES[itinerary].get("pkgsAndStops"))
        for pkg in ITINERARIES[itinerary]["uniquePackages"]:
            response["uniquePackages"].add(pkg)

    # response["uniquePackages"] = list(response["uniquePackages"])

    return response


def process_itineraries(env, orgId, itinerary_ids, timestamps, routeId):
    response = {"routeId": routeId, "itineraries": [], "uniquePackages": set()}

    # get all the data for each of them concurrently / in parallel

    with ThreadPoolExecutor() as pool:
        for i in range(len(itinerary_ids)):
            itinerary = itinerary_ids[i]
            timestamp = timestamps[i]
            # print(f">> Checking itinerary '{itinerary}'")

            if str(itinerary).strip() != "":
                pool.submit(
                    get_itinerary_packages_and_stops, env, orgId, itinerary, timestamp
                )
            else:
                print(f">> [] have 0 packages and 0 stops ({timestamp})")
    pool.shutdown(True)

    response = sync_itineraries_and_response(response, itinerary_ids)

    print(
        f">> {len(response['uniquePackages'])} unique packages found across itineraries"
    )
    return response


def get_pkgs_from_alamo(env, routeId):
    response = routes.get_stop_details(env, routeId)
    print(">> Searching for packages with Alamo's Stop Details")

    if response.get("routeStopDetail") is None:
        print(response.get("message"))
        return set()

    stops = response["routeStopDetail"]["stops"]
    pids = set()

    for stop in stops:
        stopPackages = stop["stopPackages"]

        for pkgs in stopPackages:
            pid = pkgs.get("packageId")

            if pid is not None:
                pids.add(pid)

    print(f">> Found {len(pids)} packages\n")

    return pids


def main(env, orgId, rts=None) -> dict[str, list]:
    if rts is None:
        rts = get_routes(env, orgId)
    else:
        print(">> These routes were provided:")
        print("\n".join(rts))

        if utils.select_answer("Do you wish to continue with them?") == "N":
            rts = get_routes(env, orgId)

    final_response = {}

    for routeId in rts:
        print(f'{"{:=<50}".format("")}')  # prints 50 `=` characters aligned to the left
        print(f">> Route ID: {routeId}")

        pids = set()

        # get packages from sortation (issue is pkgs are not getting to itinerary)
        pkgs_sortation = packages.get_route_packages_sortation(env, orgId, routeId)

        for pkg in pkgs_sortation:
            pids.add(pkg["packageID"])

        # get packages from route stop details
        pkgs_alamo = get_pkgs_from_alamo(env, routeId)

        for pkg in pkgs_alamo:
            pids.add(pkg)

        # get packages from itineraries
        events = routes.get_route_events(env, routeId)

        if events is not None:
            itinerary_ids, timestamps = fetch_itineraries(events)
            print(f">> Found {len(itinerary_ids)} itineraries")

            # print_itineraries(itinerary_ids)
            # if at least one itinerary was generated
            if not no_itinerary_generated(itinerary_ids):
                response = process_itineraries(
                    env, orgId, itinerary_ids, timestamps, routeId
                )

                for pid in response["uniquePackages"]:
                    pids.add(pid)

        # sets are not json compatible, so need to convert to list
        final_response[routeId] = list(pids)

        print(f">> Total of {len(final_response[routeId])} unique packages")

    print()

    return final_response


if __name__ == "__main__":
    env = utils.select_env()
    orgId = utils.select_org(env)
    response = main(env, orgId)

    print(">> Results saved in the file below")
    files.save_json_to_file(
        json.dumps(
            response,
            indent=2,
        ),
        "ROUTE_PKGS",
    )
