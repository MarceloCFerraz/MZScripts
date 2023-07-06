from utils import utils, associates, hubs, fleets


def main():
    env = utils.select_env()
    orgId = utils.select_org(env)

    print(f"TYPE THE ASSOCIATE ID")
    associateId = str(input("> ")).strip()

    associate = associates.get_associate_data(env=env, orgId=orgId, associateId=associateId)

    if associate is not None:
        print("Associate Found!")
        print()

        hubIdsArray = []
        hubNamesArray = []
        hubToBeRemoved = ""

        try:
            fleetId = associate["fleetId"]
            hubIdsArray = fleets.get_hubs_from_fleet(env=env, orgId=orgId, fleetId=fleetId)
        except Exception:
            fleetId = ""

        if fleetId == "":
            print(f"Associate only has access to {associate['hubId']}. Finishing script")
        else:
            hubsArray = []
            for hubId in hubIdsArray:
                hub = hubs.search_hub_by_id(env, orgId, hubId)[0]
                hubsArray.append(hub)
                hubNamesArray.append(hub["name"])

            print(f"Associate has access to hubs: {' '.join(hubNamesArray)}")

            while hubToBeRemoved not in hubNamesArray:
                print("WHICH HUB NEEDS TO BE REMOVED?")
                hubToBeRemoved = str(input("> ")).strip()
            
            hubsArray.remove([h for h in hubsArray if h["name"] == hubToBeRemoved][0])

            print(f"Result: {fleets.update_fleet_hubs(env, orgId, fleetId, hubsArray)}")
    print(f"Result: {associates.update_associate_data(env=env, associateData=associate)}")


main()
