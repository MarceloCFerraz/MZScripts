import json
from datetime import datetime
from utils import routes, utils, itineraries, files


def fetch_itineraries(events):
    itineraries = []
    
    notes = [e["notes"] for e in events if "done. itinerary ids" in str(e["notes"]).lower()]

    if len(notes) > 0:
        for note in notes:
            start = str(note).find("[")
            end = str(note).find("]")

            itineraries.append(
                str(note)[start + 1:end].strip()
            )

    return itineraries


def print_packages_from_itinerary(packages):
    print(json.dumps(packages, 2))


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
                input("Type in the date (yyyy-mm-dd)\n> ").strip(),
                "%Y-%m-%d"
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
        itineraryIds = fetch_itineraries(events)
        packages = {
            "itineraries": [],
            "uniquePackages": set()
        }

        print(f">> Found {len(itineraryIds)} itineraries: {' '.join([f'[{i}]' for i in itineraryIds])}")

        for itinerary in itineraryIds:
            pkgs = itineraries.get_itinerary_packages(env, orgId, itinerary)
            packages["itineraries"].append({itinerary: pkgs})

            print(f">> {itinerary} have {len(pkgs)} unique packages")

            for pkg in pkgs:
                packages["uniquePackages"].add(pkg)
        
        packages["uniquePackages"] = list(packages["uniquePackages"])
        print(f"> Total Unique Packages: {len(packages['uniquePackages'])}")

        if len(packages["itineraries"]) >= 2:
            print("Check the full response in the file below")
            files.save_json_to_file(json.dumps(packages, indent=2), "ITINERARY")
        else:
            print_packages_from_itinerary(packages)