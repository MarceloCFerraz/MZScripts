from utils import utils, associates, hubs, fleets, files
import concurrent.futures


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

        print(f">> Hubs in {fleetId}: {' '.join([h['name'] for h in fleetHubs])}")
        
        idsList = fleetHubIds
    else:
        idsList.append(associate["hubId"])

    return idsList


def fill_hubs_list(hubIdsList, allOrgHubs):
    return [hub for hub in allOrgHubs if hub['id'] in hubIdsList]


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
        except Exception:
            pass

    print("Fleet not found!")

    return None


def get_associates_with_same_fleet(allOrgAssociates, fleet):
    result = []
    for a in allOrgAssociates:
        if associate_has_fleet(a):
            if a['fleetId'] == fleet:
                result.append(a)
    
    return result



def create_fleet(env, orgId, hubsList):
    fleetId = fleets.create_fleet(env=env, orgId=orgId, hubsArray=hubsList)
    print(f">> Created {fleetId} with {[h['name'] for h in hubsList]}")

    fleet = fleets.search_fleet(env, orgId, fleetId)

    return fleet


def main(env, orgId, answer, associate, allOrgFleets, allOrgHubs, allOrgAssociates):
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
                        print(f">> Searching for a fleet with {' '.join([hub['name'] for hub in hubsList])}")
                        fleet = search_fleet_with_hubs(allOrgFleets, hubIdsList)

                        if fleet is not None:  # if a fleet with the correct hubs already exists
                            print(f">> Fleet found! Updating associate's fleetId with {fleet}")
                            associate["fleetId"] = fleet

                            response = associates.update_associate_data(env=env, associateData=associate, userName=userName)
                            print(f">> Result: {response}\n{response.text if response.status_code >= 400 else ''}")
                        else:
                            fleet = associate["fleetId"]
                            print(f">> Checking if {fleet} is used by other associates")

                            associatesWithSameFleet = get_associates_with_same_fleet(allOrgAssociates, fleet)

                            if len(associatesWithSameFleet) == 1:
                                # if only this associate has this fleet id
                                # means we can just update his fleet instead of creating another one
                                print(">> No other associate use this fleetId")
                                response = fleets.update_fleet_hubs(env, orgId, fleet, hubsList)
                                print(f">> Result: {response}\n{response.text if response.status_code >= 400 else ''}")
                            else:
                                # In this case we need to create a new fleet
                                print(">> Someone else uses this fleetId as well")

                                fleet = create_fleet(env, orgId, hubsList)
                                allOrgFleets.append(fleet)

                                associate["fleetId"] = fleet

                                response = associates.update_associate_data(env=env, associateData=associate, userName=userName)
                                print(f">> Result: {response}\n{response.text if response.status_code >= 400 else ''}")
                    else:
                        print(">> Associate doesn't have a fleet")

                        fleet = search_fleet_with_hubs(allOrgFleets, hubIdsList)

                        if fleet is not None:
                            print(f">> Fleet found! Updating associate's fleetId with {fleet}")
                            associate["fleetId"] = fleet
                        else:
                            fleet = create_fleet(env, orgId, hubsList)
                            associate["fleetId"] = fleet

                            allOrgFleets.append(fleet)

                        response = associates.update_associate_data(env=env, associateData=associate, userName=userName)
                        print(f">> Result: {response}\n{response.text if response.status_code >= 400 else ''}")
                else:
                    print("New hub already in associate's fleet")
            else:
                print(f">> Answer was {answer}. Moving associate to Hub {newHub['name']}")
                associate["hubId"] = newHub['id']
                associate["location"]["locationId"] = newHub["location"]["locationId"]

                newAssociateData = {}

                for header in associate.keys():
                    if header not in ['fleetId', 'preferredVehicle', 'preferredRoute']:
                        newAssociateData[header] = associate[header]
                response = associates.update_associate_data(env, newAssociateData, userName)
                print(f">> Result: {response}\n{response.text if response.status_code >= 400 else ''}")
        else:
            print(f"Sorry, this associate is a {accountType}. He can't be granted access to other hubs through fleets!")
            print("Finishing script...")


userName = input("What is your name?\n> ")
env = utils.select_env()
orgId = utils.select_org(env)
newHub = get_new_hub_id(env, orgId)
answer = keep_previous_hubs()

associateIds = files.get_data_from_file("associates")

allOrgFleets = list(fleets.search_fleet(env, orgId))
allOrgHubs = list(hubs.search_hubs(env, orgId))
allOrgAssociates = list(associates.search_associate(env, orgId, 0, orgId))

print("Script is running...")

logFile = files.create_logs_file(prefix=f"{newHub['name']}")
files.start_logging(logFile)

print(f"New Hub: {newHub['name']}")

for associateId in associateIds:
    associate = [a for a in allOrgAssociates if a["associateId"] == associateId][0]

    main(
        env,
        orgId,
        answer,
        associate,
        allOrgFleets,
        allOrgHubs,
        allOrgAssociates
    )

files.stop_logging()
files.close_logs_file(logFile)
print("Script Finished. Check for ./logs to see the full result!")
