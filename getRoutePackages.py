import json
from datetime import datetime

from utils import files, itineraries, routes, utils


def fetch_itineraries(events):
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


def no_itinerary_generated(itinerary_ids):
    return len([i for i in itinerary_ids if str(i).strip() != ""]) == 0


def print_data_from_itinerary(data):
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    env = utils.select_env()
    orgId = utils.select_org(env)

    answer = utils.select_answer("> Do you have a routeId? ")

    routeId = None

    if answer == "Y":
        routeId = input("> Input the route ID: ")
    else:
        while routeId == None:
            hubName = input("Type the hub (only numbers)\n> ").strip()
            cpt = datetime.strptime(
                input("Type in the date (yyyy-mm-dd)\n> ").strip(), "%Y-%m-%d"
            )
            cpt = cpt.strftime("%Y-%m-%d")
            routeName = input("Type the route name\n> ").strip()

            route = routes.find_route(env, orgId, routeName, hubName, cpt)

            if route == None:
                print("Route not Found, please try again\n")
                print("--------------------------------")
            else:
                routeId = route["routeId"]

    events = routes.get_route_events(env, routeId)

    if events != None:
        itinerary_ids = fetch_itineraries(events)

        if no_itinerary_generated(itinerary_ids):
            print(
                f">> Found {len(itinerary_ids)} 'done' events found, but OEGR have generated 0 itineraries"
                + f"\n>> {' '.join([f'[{iti}]' for iti in itinerary_ids])}"
            )
        else:
            response = {"routeId": routeId, "itineraries": [], "uniquePackages": set()}

            print(
                f">> Found {len(itinerary_ids)} itineraries: {' '.join([f'[{iti}]' for iti in itinerary_ids])}"
            )

            for itinerary in itinerary_ids:
                print(f"\n>> Checking itinerary '{itinerary}'")

                if str(itinerary).strip() != "":
                    pkgs_and_stops = itineraries.get_itinerary_packages_and_stops(
                        env, orgId, itinerary
                    )
                    response["itineraries"].append(pkgs_and_stops)

                    print(
                        f">> {itinerary} have {len(pkgs_and_stops['loadedPackages'])} packages "
                        + f"({len(pkgs_and_stops['deliveredPackages'])} delivered) and "
                        + f"{len(pkgs_and_stops['deliveryStops'])} stops"
                    )

                    for pkg in pkgs_and_stops["loadedPackages"]:
                        response["uniquePackages"].add(pkg)

            response["uniquePackages"] = list(response["uniquePackages"])
            print(
                f"\n>> Total unique packages accross valid itineraries: {len(response['uniquePackages'])}"
            )

            if len(response["itineraries"]) >= 2:
                print("Check the full response in the file below")
                files.save_json_to_file(json.dumps(response, indent=2), "ITINERARY")
            else:
                print_data_from_itinerary(response["itineraries"][0])
