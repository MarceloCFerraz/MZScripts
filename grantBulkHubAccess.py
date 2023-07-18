from utils import utils, associates, hubs, fleets, files
import sys


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


def get_hubs_from_fleet(associate, allOrgFleets, allOrgHubs):
    idsList = []
    fleetId = ""

    if associate_has_fleet(associate):
        fleet = associate["fleetId"]
        print(f">> Associate has a fleet {fleetId}")

        fleetHubIds = [f['hubIds'] for f in allOrgFleets if f['fleetId'] == fleetId][0]
        fleetHubs = [h for h in allOrgHubs if h['id'] in fleetHubIds]
        fleetHubNames = [h['name'] for h in fleetHubs]

        print(f">> Hubs in {fleetId}: {fleetHubNames}")
        
        idsList = fleetHubIds
    else:
        idsList.append(associate["hubId"])

    return idsList


def fill_hubs_list(hubIdsList, allOrgHubs):
    return [hub for hub in allOrgHubs if hub['id'] in hubIdsList]


def search_fleet_with_hubs(allOrgFleets, hubIdsArray):
    print(f">> Searching for a fleet that contains {hubIdsArray}")
    hubIdsArray.sort()
    
    for fleet in allOrgFleets:
        try:
            fleetHubs = fleet["hubIds"].sort()
            if fleetHubs == hubIdsArray:
                return [fleet]
        except Exception:
            pass
    
    return []


def create_fleet(env, orgId, hubsList):
    fleetId = fleets.create_fleet(env=env, orgId=orgId, hubsArray=hubsList)
    print(f">> Created {fleetId} with {[h['name'] for h in hubsList]}")

    fleet = fleets.search_fleet(env, orgId, fleetId)[0]

    return fleet


def main():
    userName = input("What is your name?\n> ")
    env = utils.select_env()
    orgId = utils.select_org(env)
    newHub = get_new_hub_id(env, orgId)
    answer = keep_previous_hubs()
    
    allOrgAssociates = list(associates.search_associate(env, orgId, 0, orgId))
    allOrgFleets = list(fleets.search_fleet(env, orgId))
    allOrgHubs = list(hubs.search_hubs(env, orgId))

    associateIds = files.get_data_from_file("associates")

    print("Script is running...")
    
    logFile = files.create_logs_file(prefix=f"{newHub['name']}")
    files.start_logging(logFile)
    
    print(f"New Hub: {newHub['name']}")

    for associateId in associateIds:
        associate = [a for a in allOrgAssociates if a["associateId"] == associateId][0]

        if associate is not None:
            print(f"\nUpdating {associate['associateId']}")
            print()
            accountType = associate["associateType"]
            hubIdsList = get_hubs_from_fleet(associate, allOrgFleets, allOrgHubs)

            if accountType not in ["DRIVER", "SORTER"]:
                if answer == "Y":
                    if newHub["id"] not in hubIdsList:
                        hubIdsList.append(newHub["id"])
                        hubsList = fill_hubs_list(hubIdsList, allOrgHubs)

                        if associate_has_fleet(associate):  # if associate already have a fleetId
                            fleet = search_fleet_with_hubs(allOrgFleets, hubIdsList)

                            if len(fleet) > 0:  # if a fleet with the correct hubs already exists
                                print(f">> Fleet found! Updating associate's fleetId with {fleet[0]['fleetId']}")
                                associate["fleetId"] = fleet[0]['fleetId']
                            else:
                                print(">> No fleets found.")
                                fleet = associate["fleetId"]
                                print(f">> Checking if {fleet} is present in other associates' data")

                                associatesWithSameFleet = []

                                for a in allOrgAssociates:
                                    if associate_has_fleet(a):
                                        if a['fleetId'] == fleet:
                                            associatesWithSameFleet.append(a)
                                            
                                                                
                                if len(associatesWithSameFleet) == 1:
                                    # if only this associate has this fleet id
                                    # means we can just update his fleet instead of creating another one
                                    print(">> No other associate use this fleetId")
                                    response = fleets.update_fleet_hubs(env, orgId, fleet, hubsList)
                                    print(f">> Result: {response}\n{response.text if response.status_code > 400 else ''}")
                                else:
                                    # In this case we need to create a new fleet
                                    print(">> Someone else uses this fleetId as well")
                                    
                                    fleet = create_fleet(env, orgId, hubsList)
                                    associate["fleetId"] = fleet['fleetId']
                                    
                                    allOrgFleets.append(fleet)
                                    
                        else:
                            print(">> Associate doesn't have a fleet")
                            
                            fleet = search_fleet_with_hubs(allOrgFleets, hubIdsList)

                            if len(fleet) == 0:
                                print(f">> There are no fleets with those hubs")
                                fleet = create_fleet(env, orgId, hubsList)
                                fleetId = fleet['fleetId']
                                
                                allOrgFleets.append(fleet)
                            else:
                                print(f">> Fleet found! Updating associate's fleetId with {fleet[0]['fleetId']}")
                                associate["fleetId"] = fleet[0]['fleetId']

                            associate["fleetId"] = fleetId
                    else:
                        print("New hub already in associate's fleet")
                else:
                    print(f">> Answer was {answer}. Updating associate Hub ID")
                    associate["hubId"] = newHub['id']
                
                response = associates.update_associate_data(env=env, associateData=associate, userName=userName)
                print(f">> Result: {response}\n{response.text if response.status_code > 400 else ''}")
            else:
                print(f"Sorry, this associate is a {accountType} and we can't him access to other hubs through fleets!")
                print("Finishing script...")
    
    files.stop_logging()
    files.close_logs_file(logFile)
    print("Script Finished. Check for ./logs to see the full result!")


main()
