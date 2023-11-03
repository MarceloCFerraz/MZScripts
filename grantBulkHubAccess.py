import sys
import concurrent.futures
from utils import utils, associates, hubs, fleets, files


ASSOCIATES = []


def get_associate(env, orgId, associateId):
    associate = associates.get_associate_data(env, orgId, associateId)

    if associate != None:
        ASSOCIATES.append(associate)
    else:
        print(f">> {associateId} not found")


def get_new_hub(env, orgId, hubName=None, retry=False):
    if retry:
        hubName = input("> ").strip().upper()

    try:
        hub = hubs.search_hub_by_name(env=env, orgId=orgId, hubName=hubName)[0]
        print(f"{hubName} (OK -> {hub['id']})")
    except Exception as e:
        print("Hub not found, please try again!")
        hub = get_new_hub(env, orgId, None, True)

    print()
    return hub


def select_answer(question=None, answers=None):
    if not answers:
        answers = ["Y", "N"]
    if not question:
        question = f"Does the associate need to maintain access to all previous hubs? ({'/'.join(answers)})"

    answer = ""
    print(question)
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
        # print(f">> Associate has fleet {fleet}")

        fleetHubs = fleets.get_hubs_from_fleet(env=env, orgId=orgId, fleetId=fleet)
        # print(f">> Hubs in {fleet}: {fleetHubs}")
        for hubId in fleetHubs:
            idsList.append(hubId)

        if associate.get('hubId') not in idsList:
            idsList.append(associate.get('hubId'))

    return idsList


def fill_hubs_list(env, orgId, hubsIds):
    hubsList = []

    for hubId in hubsIds:
        hubsList.append(hubs.search_hub_by_id(env, orgId, hubId)[0])

    return hubsList


def search_fleet_with_hubs(allFleets, hubIdsArray):
    hubIdsArray.sort()

    for fleet in allFleets:
        try:
            fleetHubs = fleet.get('hubIds')

            if len(fleetHubs) == len(hubIdsArray):
                found = True

                fleetHubs.sort()

                for hubid in hubIdsArray:
                    if hubid not in fleetHubs:
                        found = False
                if found:
                    return fleet["fleetId"]

        except Exception as e:
            print(f"** No hubIds in {fleet.get('fleetId')} → {e}")

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


def get_new_hubs(env, orgId, hubsNames, associateName):
    answer = "init"
    newHubs = []
    updated = False

    while answer != "" and not updated:
        answer = input("Type the new HUB name (leave blank if done):\n> ").strip().upper()

        if answer not in hubsNames and answer != "":
            newHub = get_new_hub(env, orgId, answer)
            hubsNames.append(newHub.get('name'))

            newHubs.append(newHub)
            updated = True

        elif answer in hubsNames:
            print(f">> {associateName} already have access to {answer}!\n")
    
    return newHubs


def move_to_new_hub(env, orgId, associate, userName):
    print("Type the new HUB: ")
    newHub = get_new_hub(env, orgId)
    associate["hubId"] = newHub['id']
    associate["location"]["locationId"] = newHub["location"]["locationId"]

    newAssociateData = {}

    print("Moving associate and removing fleet, vehicle and route!")
    for header in associate.keys():
        if header not in ['fleetId', 'preferredVehicle', 'preferredRoute']:
            newAssociateData[header] = associate[header]

    update_associate(env, newAssociateData, userName)


def apply_changes(env, orgId, hubsList, allFleets, associate, userName):
    hubsNames = [h.get('name') for h in hubsList]
    hubsIds = [h.get('id') for h in hubsList]

    print(f">> Searching for a fleet with {hubsNames}")
    fleet = search_fleet_with_hubs(  # searching for a fleet with same hubs
        allFleets=allFleets,
        hubIdsArray=hubsIds
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
            print(">> Associate doesn't have a fleet")
            print(f">> Creating new fleet with {hubsNames}")
            fleetId = create_new_fleet(env, orgId, hubsList)

            associate["fleetId"] = fleetId

            update_associate(env, associate, userName)

# How the script works:
# - Get associate IDs from 'associates.txt,' with each new line representing a new associate ID. No need for special formatting.
# - Use multithreading to search for associate IDs and save them in the ASSOCIATES array when found.
# - Interactively ask each associate about their hub access needs, one hub at a time. Press Enter with a blank input to continue.
# - Check if associates need to keep their current hub access:
#   - If yes:
#     - Add new hubs to the associate's hub list.
#     - Look for a fleet that already contains these hubs.
#       - If a fleet is found, update the associate's data with the fleet ID.
#       - If none exists, check if other associates use the same fleet.
#         - If no one does, update the fleet.
#         - If others do, create a new fleet with old and new hubs.
#   - If no:
#     - Search for a fleet with the new hubs.
#       - If a fleet is found, update the associate's data with the fleet ID.
#       - If none is found, check if other associates use the same fleet.
#         - If no one does, update the fleet.
#         - If others do, create a new fleet with old and new hubs.
#
# Additionally, manage driver and sorter relocations as needed:
# - Determine the new hub.
# - Modify the associate's hubId and locationId.
# - Remove any references to the previous 'fleetId,' 'preferredVehicle,' and 'preferredRoute' before updating the associate's data."
def main():
    userName = input("What is your name?\n> ")
    env = utils.select_env()
    orgId = utils.select_org(env)

    print("Reading 'associates.txt' to get Associate IDs")
    associateIDs = files.get_data_from_file("associates")

    with concurrent.futures.ThreadPoolExecutor() as pool:
        for associateId in associateIDs:
            pool.submit(get_associate, env, orgId, associateId)
        pool.shutdown(True)

        allFleets = fleets.search_fleet(env, orgId)
        # print(f">> Loaded {len(allFleets)} fleets")

        for associate in ASSOCIATES:
            name = associate.get('contact').get('name')
            print(f">> {name}:")

            if associate["associateType"] not in ["DRIVER", "SORTER"]:
                hubsIds = get_associate_hubs_from_fleet(env, orgId, associate)
                hubsList = fill_hubs_list(env, orgId, hubsIds)
                hubsNames = [h.get('name') for h in hubsList]
                
                print(f">> {name} have access to: {hubsNames}\n")

                newHubs = get_new_hubs(env, orgId, hubsNames, name)
                answer = select_answer()

                if answer == "Y":
                    for newHub in newHubs:
                        hubsList.append(newHub)

                    apply_changes(env, orgId, hubsList, allFleets, associate, userName)
                else:
                    apply_changes(env, orgId, hubsList, allFleets, associate, userName)
            else:
                print(f">> {name} is a driver/sorter. We can't give drivers access to other hubs!")
                answer = select_answer("Do you want to move this associate to a new HUB?")

                if answer == "Y":
                    move_to_new_hub(env, orgId, associate, userName)

                print("Finishing script...")
                sys.exit()


main()
