from utils import utils, associates, hubs, fleets


def get_new_hub_id(env, orgId):
    print("TYPE THE NEW HUB NAME (numbers only)")
    hubName = input("> ").strip()

    hub = hubs.search_hub_by_name(env=env, orgId=orgId, hubName=hubName)[0]
    print(f"{hubName}'s id is {hub['id']}")

    return hub


def keep_previous_hubs():
    answers = ["Y", "N"]
    answer = ""
    print("Does the associate need to maintain access to all previous hubs? (Y/N)")
    while answer not in answers:
        answer = str(input("> ")).upper().strip()

    return answer


def associate_has_fleet(associate):
    fleetId = ""

    try:
        fleetId = associate["fleetId"]
    except Exception:
        pass
    
    return fleetId != ""

def get_associate_hubs_from_fleet(env, orgId, associate):
    idsList = []
    fleet = ""

    if associate_has_fleet(associate):
        fleet = associate["fleetId"]
        print(f">> Associate has fleet {fleet}")

        fleetHubs = fleets.get_hubs_from_fleet(env=env, orgId=orgId, fleetId=fleet)
        print(f">> Hubs in {fleet}: {fleetHubs}")
        for hubId in fleetHubs:
            idsList.append(hubId)
    else:
        idsList.append(associate["hubId"])

    return idsList


def fill_hubs_list(env, orgId, hubIdsList):
    hubsList = []

    for hubId in hubIdsList:
        hubsList.append(hubs.search_hub_by_id(env, orgId, hubId)[0])

    return hubsList


def main():
    userName = input("What is your name?\n> ")
    env = utils.select_env()
    orgId = utils.select_org(env)

    print(f"TYPE THE ASSOCIATE ID")
    associateId = input("> ")

    associate = associates.get_associate_data(env=env, orgId=orgId, associateId=associateId)

    if associate is not None:
        print("Associate Found!")
        print()
        accountType = associate["associateType"]

        if accountType != "DRIVER":
            newHub = get_new_hub_id(env, orgId)

            answer = keep_previous_hubs()

            if answer == "Y":
                hubIdsList = get_associate_hubs_from_fleet(env, orgId, associate)

                if newHub["id"] not in hubIdsList:
                    hubIdsList.append(newHub["id"])
                else:
                    print("New hub already in associate's fleet")
                
                hubsList = fill_hubs_list(env, orgId, hubIdsList)

                if associate_has_fleet(associate):  # if associate already have a fleetId
                    print(f">> Searching for a fleet with {' '.join(
                        [hub['name'] for hub in hubsList]
                    )}")
                    fleet = fleets.search_fleet_with_hubs(  # searching for a fleet with same hubs
                        env=env,
                        orgId=orgId,
                        hubIdsArray=hubIdsList
                    )
                    if fleet is not None:  # if a fleet with the correct hubs already exists
                        print(f">> Fleet found! Updating associate's fleetId with {fleet}")
                        associate["fleetId"] = fleet
                    else:
                        fleet = associate["fleetId"]
                        print(f">> Searching if {fleet} is present in other associates' data")
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


                            print(f">> Result: {fleets.update_fleet_hubs(env, orgId, fleet, hubsList)}")
                        else:
                            # In this case we need to create a new fleet
                            print(">> Someone else uses this fleetId as well")

                            fleet = fleets.create_fleet(env=env, orgId=orgId, hubsArray=hubsList)
                            associate["fleetId"] = fleet
                else:
                    print(">> Associate doesn't have a fleet")
                    print(f">> Searching for a fleet containing {newHub['name']}")
                    
                    fleetId = fleets.search_fleet_with_hubs(env, orgId, [hub["id"] for hub in hubsList])

                    if fleetId == None:
                        print(f">> There are no fleets with only {' '.join(
                            [hub['name'] for hub in hubsList]
                        )}")
                        print(f">> Creating new fleet with")
                        
                        fleetId = fleets.create_fleet(env=env, orgId=orgId, hubsArray=hubsList)

                    associate["fleetId"] = fleetId
            else:
                associate["hubId"] = newHub['id']
            print(f">> Result: {associates.update_associate_data(env=env, associateData=associate, userName=userName)}")
        else:
            print("Sorry, this associate is a driver and we can't give drivers access to other hubs!")
            print("Finishing script...")


main()
