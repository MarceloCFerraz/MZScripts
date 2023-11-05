from utils import utils, associates, hubs, fleets


def get_associate(env, orgId):
    answer = select_answer(question=">> Do you have an associate ID?")
    if answer == "Y":
        print(f">> Insert the Associate ID")
        associateId = input("> ")
        associate = associates.get_associate_data(env, orgId, associateId)
    else:
        search_key = input(">> Type the associate's e-mail or username\n> ")
        search_key_index = 3 if "@" in search_key else 4
        # 👆 based on key_types list in associates.search_associate()
        associates.search_associate(env, orgId, search_key_index, search_key)


    return associate


def get_new_hub(env, orgId, hubName=None, hubsNames=None):
    if hubName == None:
        hubName = input("> ").strip()

    if hubsNames != None:
        while hubName in hubsNames:
            print(f">> Associate already have access to {hubName}")
            hubName = input(">> Try again or hit 'CTRL' + 'C' to quit the program\n> ")

    try:
        hub = hubs.search_hub_by_name(env=env, orgId=orgId, hubName=hubName)[0]
        print(f">> {hubName} (OK -> {hub['id']})")
    except Exception as e:
        print(">> Hub not found, please try again!")
        hub = get_new_hub(env, orgId, None, hubsNames)

    print()
    return hub


def select_answer(question=None, answers=None):
    if answers == None:
        answers = ["Y", "N"]

    if question == None:
        question = f">> Does the associate need to maintain access to all previous hubs? ({'/'.join(answers)})"

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
        print(f">> Associate has fleet {fleet}")

        fleetHubs = fleets.get_hubs_from_fleet(env=env, orgId=orgId, fleetId=fleet)
        # print(f">> Hubs in {fleet}: {fleetHubs}")
        for hubId in fleetHubs:
            idsList.append(hubId)

        if associate.get('hubId') not in idsList:
            idsList.append(associate.get('hubId'))

    return idsList


def fill_hubs_list(env, orgId, hubIdsList):
    hubsList = []

    for hubId in hubIdsList:
        hubsList.append(hubs.search_hub_by_id(env, orgId, hubId)[0])

    return hubsList


def search_fleet_with_hubs(allFleets, hubIdsList):
    hubIdsList.sort()

    for fleet in allFleets:
        try:
            fleetHubs = fleet.get('hubIds')

            if len(fleetHubs) == len(hubIdsList):
                found = True

                fleetHubs.sort()

                for hubid in hubIdsList:
                    if hubid not in fleetHubs:
                        found = False
                if found:
                    return fleet["fleetId"]

        except Exception as e:
            print(f"** No hubIds in {fleet.get('fleetId')}")

    print(">>>> Fleet not found!")

    return None


def create_new_fleet(env, orgId, hubsList):
    fleetId = fleets.create_fleet(env=env, orgId=orgId, hubsList=hubsList)
    print(f">> {fleetId}")

    return fleetId


def update_associate(env, associate, userName):
    response = associates.update_associate_data(env, associate, userName)

    print(f">> Update Status: {'OK' if response.status_code < 400 else 'FAILED'}")
    print(f"{response.text if response.status_code >= 400 else ''}")


def apply_changes(env, orgId, hubsList, allFleets, associate, userName):
    """
    This function manages the assignment and updating of associate access to hubs within fleets based on the availability of fleets and hubs. It performs necessary updates and creations, and communicates the results to the user.

    Parameters:
    - env: The environment where the fleet organization operates.
    - orgId: The organization ID within the chosen environment.
    - hubsList: A list of hubs to which the associate should have access.
    - allFleets: A list of all fleets within the selected environment and organization.
    - associate: The associate whose access is being managed.
    - userName: The name of the user making the changes.

    This function performs the following logical steps:

    1. Retrieve the names and IDs of hubs from the provided hubsList.
    2. Search for a fleet that has the same hubs as the associate's access.
    3. If a fleet with the correct hubs already exists, update the associate's data with that fleet.
    4. If the associate already has a fleet, check if other associates use the same fleet.
        - If no other associate uses the same fleet, update the existing fleet with the new hubs.
        - If other associates use the same fleet, create a new fleet with the provided hubs.
    5. If the associate doesn't have a fleet, create a new fleet with the provided hubs and associate it with the associate.

    """
    hubsNames = [h.get('name') for h in hubsList]
    hubsIds = [h.get('id') for h in hubsList]

    print(f">> Searching for a fleet with {' '.join(hubsNames)}")
    fleet = search_fleet_with_hubs(  # searching for a fleet with same hubs
        allFleets=allFleets,
        hubIdsList=hubsIds
    )
    
    if fleet is not None:  # if a fleet with the correct hubs already exists
        print(f">>>> Fleet found: {fleet}")
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
            print(f">> Creating new fleet with {' '.join(hubsNames)}")
            fleetId = create_new_fleet(env, orgId, hubsList)

            associate["fleetId"] = fleetId

            update_associate(env, associate, userName)


def move_to_new_hub(env, orgId, associate, userName, newHub=None):
    print(">> Moving associate, removing fleet, vehicle and pref. route")

    if newHub == None:
        print("\n>> Type the new HUB's name")
        newHub = get_new_hub(env, orgId)

    associate["hubId"] = newHub['id']
    associate["location"]["locationId"] = newHub["location"]["locationId"]

    newAssociateData = {}

    for header in associate.keys():
        if header not in ['fleetId', 'preferredVehicle', 'preferredRoute']:
            newAssociateData[header] = associate[header]

    update_associate(env, newAssociateData, userName)


def main():
    userName = input("What is your name?\n> ")
    env = utils.select_env()
    orgId = utils.select_org(env)

    associate = get_associate(env, orgId)

    if associate is not None:
        name = associate.get('contact').get('name')
        print("Associate Found")
        print()

        if associate["associateType"] not in ["DRIVER", "SORTER"]:
            allFleets = fleets.search_fleet(env, orgId)
            # print(f">> Loaded {len(allFleets)} fleets")

            hubIdsList = get_associate_hubs_from_fleet(env, orgId, associate)
            hubsList = fill_hubs_list(env, orgId, hubIdsList)

            hubsNames = [hub['name'] for hub in hubsList]
            print(f">> HUBs: {' '.join(hubsNames)}")
        
            newHubName = input(
                "\n>> Type the new HUB name\n"
                "> "
            )
            newHub = get_new_hub(env, orgId, newHubName, hubsNames)
            answer = select_answer()

            if answer == "Y":                
                hubsList.append(newHub)

                apply_changes(env, orgId, hubsList, allFleets, associate, userName)
            else:
                print(f">> Answer was '{answer}'...")
                move_to_new_hub(
                    env,
                    orgId,
                    associate,
                    userName,
                    newHub
                )
        else:
            print(f">> {name} is a driver/sorter. We can't give drivers access to other hubs!")
            answer = select_answer(question="Do you want to move this associate to a new HUB?")

            if answer == "Y":
                move_to_new_hub(
                    env,
                    orgId,
                    associate,
                    userName
                    )


main()
