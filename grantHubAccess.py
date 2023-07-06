from utils import utils, associates, hubs, fleets


def main():
    env = utils.select_env()
    orgId = utils.select_org(env)

    print(f"TYPE THE ASSOCIATE ID")
    associateId = input("> ")

    associate = associates.get_associate_data(env=env, orgId=orgId, associateId=associateId)

    if associate is not None:
        print("Associate Found!")
        print()

        print("TYPE THE NEW HUB NAME (numbers only)")
        hubName = input("> ")
        newHubId = hubs.search_hub_by_name(env=env, orgId=orgId, hubName=hubName)[0]["id"]
        print(f"{hubName}'s id is {newHubId}")

        answers = ["Y", "N"]
        answer = ""
        print("Does the associate need to maintain access to all previous hubs? (Y/N)")
        while answer not in answers:
            answer = str(input("> ")).upper().strip()

        if answer == "Y":
            hubIdsArray = []

            fleet = ""
            try:
                fleet = associate["fleetId"]
                print(f"Associate has fleet {fleet}")
                fleetHubs = fleets.get_hubs_from_fleet(env=env, orgId=orgId, fleetId=fleet)
                print(f"Hubs in {fleet}: {fleetHubs}")
                for hub in fleetHubs:
                    hubIdsArray.append(hub)
            except Exception:
                hubIdsArray.append(associate["hubId"])

            if newHubId not in hubIdsArray:
                hubIdsArray.append(newHubId)
            else:
                print("New hub already in associate's fleet")

            if fleet != "":  # if associate already have a fleetId
                fleet = fleets.search_fleet_with_hubs(  # searching for a fleet with same hubs
                    env=env,
                    orgId=orgId,
                    hubIdsArray=hubIdsArray
                )
                if fleet is not None:  # if a fleet with the correct hubs already exists
                    print(f"Fleet found! Updating associate's fleetId with {fleet}")
                    associate["fleetId"] = fleet
                else:
                    fleet = associate["fleetId"]
                    print(f"Searching if {fleet} is present in other associates' data")
                    associatesWithSameFleet = associates.search_associate(
                        env=env,
                        org_id=orgId,
                        key_type_index=12,  # fleetId (12)
                        search_key=fleet
                    )
                    # if only this associate has this fleet id
                    if len(associatesWithSameFleet) == 1 and associatesWithSameFleet is not None:
                        print("No other associate use this fleetId")
                        hubsArray = []
                        for hubId in hubIdsArray:
                            hubsArray.append(hubs.search_hub_by_id(env, orgId, hubId)[0])
                        print(f"Result: {fleets.update_fleet_hubs(env, orgId, fleet, hubsArray)}")
                    else:
                        print("Someone else uses this fleetId as well")
                        hubsArray = []
                        for hubId in hubIdsArray:
                            hubsArray.append(hubs.search_hub_by_id(env=env, orgId=orgId, hubId=hubId)[0])
                        fleet = fleets.create_fleet(env=env, orgId=orgId, hubsArray=hubsArray)
                        associate["fleetId"] = fleet
            else:
                print("Associate doesn't have a fleet")
                hubsArray = []
                for hubId in hubIdsArray:
                    hubsArray.append(hubs.search_hub_by_id(env=env, orgId=orgId, hubId=hubId)[0])
                fleet = fleets.create_fleet(env=env, orgId=orgId, hubsArray=hubsArray)
                associate["fleetId"] = fleet
        else:
            associate["hubId"] = newHubId
        print(f"Result: {associates.update_associate_data(env=env, associateData=associate)}")


main()
