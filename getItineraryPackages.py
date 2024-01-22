import json
from utils import utils, itineraries, files

if __name__ == "__main__":
    env = utils.select_env()
    org_id = utils.select_org(env)

    itinerary = input("Type the itinerary: ")

    response = {"itineraries": [], "uniquePackages": set()}

    print(f"\n>> Checking itinerary '{itinerary}'")

    if str(itinerary).strip() != "":
        pkgs_and_stops = itineraries.get_itinerary_packages_and_stops(
            env, org_id, itinerary
        )
        response["itineraries"].append(pkgs_and_stops)

        print(
            f">> {itinerary} have {len(pkgs_and_stops['loadedPackages'])} packages "
            # TODO: fetch switchboard to check package status
            # + f"({len(pkgs_and_stops['deliveredPackages'])} delivered) and "
            + f"{len(pkgs_and_stops['deliveryStops'])} stops"
        )

        for pkg in pkgs_and_stops["loadedPackages"]:
            response["uniquePackages"].add(pkg)

        response["uniquePackages"] = list(response["uniquePackages"])
        print(
            f"\n>> Total unique packages accross valid itineraries: {len(response['uniquePackages'])}"
        )

        if len(response["uniquePackages"]) > 20:
            print("Check the full response in the file below")
            files.save_json_to_file(json.dumps(response, indent=2), "ITINERARY")
        else:
            for itinerary in response["itineraries"]:
                print(json.dumps(response, indent=2))
