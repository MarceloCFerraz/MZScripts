from utils import utils, associates, hubs, fleets


def main():
    env = utils.select_env()
    orgId = utils.select_org(env)

    print(f"TYPE THE ASSOCIATE ID")
    associateId = str(input("> ")).strip()

    associate = associates.get_associate_data(env=env, orgId=orgId, associateId=associateId)

    if associate is not None:
        print(">> Associate Found!")
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
            print(f">> Associate only has access to {associate['hubId']}. Finishing script")
        else:
            hubsArray = []
            for hubId in hubIdsArray:
                hub = hubs.search_hub_by_id(env, orgId, hubId)[0]
                hubsArray.append(hub)
                hubNamesArray.append(hub["name"])

            print(f">> Associate has access to hubs: {' '.join(hubNamesArray)}")

            while hubToBeRemoved not in hubNamesArray:
                print(">> WHICH HUB NEEDS TO BE REMOVED?")
                hubToBeRemoved = str(input("> ")).strip()
            
            hubsArray.remove([h for h in hubsArray if h["name"] == hubToBeRemoved][0])

            print(f">> Searching for a fleet with {' '.join(hubsArray['name'])}")

            fleet = fleets.search_fleet_with_hubs(  # searching for a fleet with same hubs
                env=env,
                orgId=orgId,
                hubIdsArray=[h['id'] for h in hubsArray]
            )
            if fleet is not None:  # if a fleet with the correct hubs already exists
                print(f">> Fleet found! Updating associate's fleetId with {fleet}")

                associate["fleetId"] = fleet
            else:
                print(f">> Searching if {fleet} is present in other associates' data")

                fleet = associate["fleetId"]
                associatesWithSameFleet = associates.search_associate(
                    env=env,
                    org_id=orgId,
                    key_type_index=12,  # fleetId (12)
                    search_key=fleet
                )
                
                if len(associatesWithSameFleet) == 1 and associatesWithSameFleet is not None:
                    # if only this associate has this fleet id
                    # means we can just update his fleet instead of creating another one
                    print(">> No other associate use this fleetId")
                    print(f">> Updating fleet with {' '.join(hubsArray['name'])}")

                    print(f">> Result: {fleets.update_fleet_hubs(env, orgId, fleet, hubsArray)}")
                else:
                    # In this case we need to create a new fleet
                    print(">> Someone else uses this fleetId as well")
                    print(">> Creating a new fleet")

                    fleet = fleets.create_fleet(env=env, orgId=orgId, hubsArray=hubsArray)
                    associate["fleetId"] = fleet

                    print(f">> New Fleet: {fleet}")
    print(">> Updating Associate Data")
    print(f">> Result: {associates.update_associate_data(env=env, associateData=associate)}")


main()
