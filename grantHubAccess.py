import sys
from utils import utils, associates, hubs, fleets


def get_new_hub(env, orgId, retry=False):
    if not retry:
        print("TYPE THE NEW HUB NAME")
    hubName = input("> ").strip()

    try:
        hub = hubs.search_hub_by_name(env=env, orgId=orgId, hubName=hubName)[0]
        print(f"Hub found ({hubName} -> {hub['id']})\n")
    except Exception as e:
        print("Hub not found, please try again:")
        hub = get_new_hub(env, orgId, True)

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
        # print(f">> Hubs in {fleet}: {fleetHubs}")
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

def search_fleet_with_hubs(allFleets, hubIdsArray):
    hubIdsArray.sort()

    for fleet in allFleets:
        try:
            fleetHubs = fleet["hubIds"].sort()
            if len(fleetHubs) == len(hubIdsArray):
                found = True

                for hubid in hubIdsArray:
                    if hubid not in fleetHubs:
                        found = False

                if found:
                    return fleet["fleetId"]
        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    print("Fleet not found!")

    return None


def create_new_fleet(env, orgId, hubsList):
    print(f">> Creating new fleet",)
    fleetId = fleets.create_fleet(env=env, orgId=orgId, hubsArray=hubsList)
    print(f">> {fleetId}")

    return fleetId


def update_associate(env, associate, userName):
    response = associates.update_associate_data(env, associate, userName)
    print(f">> Updating associate data: {response}\n{response.text if response.status_code >= 400 else ''}")
    

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

        newHub = get_new_hub(env, orgId)
        answer = keep_previous_hubs()

        if answer == "Y":
            if accountType not in ["DRIVER", "SORTER"]:

                allFleets = fleets.search_fleet(env, orgId)

                hubIdsList = get_associate_hubs_from_fleet(env, orgId, associate)

                if newHub["id"] not in hubIdsList:
                    hubIdsList.append(newHub["id"])

                    hubsList = fill_hubs_list(env, orgId, hubIdsList)

                    print(f">> Searching for a fleet with {' '.join([hub['name'] for hub in hubsList])}")
                    fleet = search_fleet_with_hubs(  # searching for a fleet with same hubs
                        allFleets=allFleets,
                        hubIdsArray=hubIdsList
                    )
                    
                    if fleet is not None:  # if a fleet with the correct hubs already exists
                        print(f">> Fleet found! Updating associate data with {fleet}")
                        associate["fleetId"] = fleet
                        
                        update_associate(env, associate, userName)
                    else:
                        if associate_has_fleet(associate):  # if associate already have a fleetId
                            fleet = associate["fleetId"]
                            
                            print(f">> Checking if other associates use the same fleet")
                            associatesWithSameFleet = associates.search_associate(
                                env=env,
                                org_id=orgId,
                                key_type_index=11,  # fleetId (11)
                                search_key=fleet
                            )
                            
                            if len(associatesWithSameFleet) == 1 and associatesWithSameFleet is not None:
                                # if only this associate has this fleet id
                                # means we can just update his fleet instead of creating another one
                                print(">> No other associate use this fleetId")

                                print(f">> Updating Fleet: {fleets.update_fleet_hubs(env, orgId, fleet, hubsList)}")
                            else:
                                # In this case we need to create a new fleet
                                print(">> Someone else uses this fleetId as well")
                                fleetId = create_new_fleet(env, orgId, hubsList)

                                associate["fleetId"] = fleetId

                                update_associate(env, associate, userName)
                        else:
                            fleetId = create_new_fleet(env, orgId, hubsList)

                            associate["fleetId"] = fleetId

                            update_associate(env, associate, userName)
                else:
                    print("New hub already in associate's fleet")
                    sys.exit()
                    # quits the program if the hub is already on associate's fleet
            else:
                print("Sorry, this associate is a driver and we can't give drivers access to other hubs!")
                print("Finishing script...")
        else:
            print(f">> Answer was {answer}. Moving associate to Hub {newHub['name']}")
            associate["hubId"] = newHub['id']
            associate["location"]["locationId"] = newHub["location"]["locationId"]

            newAssociateData = {}

            for header in associate.keys():
                if header not in ['fleetId', 'preferredVehicle', 'preferredRoute']:
                    newAssociateData[header] = associate[header]

            update_associate(env, newAssociateData, userName)


main()
