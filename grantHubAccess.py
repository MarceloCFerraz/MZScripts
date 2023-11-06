from utils import utils, associates, hubs, fleets


def get_associate(env, orgId):
    """
    Retrieves associate data based on the associate's ID or search key.

    This function prompts the user to enter the associate's ID or search key (email or username) and retrieves the associate's data using the provided information.

    Parameters:
    - env (str): The environment in which the associate data is stored.
    - orgId (str): The organization ID associated with the associate.

    Returns:
    - associate (dict): The associate's data.
    """
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
    """
    Obtains information about a new hub.

    This function prompts the user to enter the name of the new hub and validates its existence. If the hub already exists, the user is prompted to try again.

    Parameters:
    - env (str): The environment in which the hub data is stored.
    - orgId (str): The organization ID associated with the hub.
    - hubName (str, optional): The name of the new hub. If not provided, the user will be prompted to enter it.
    - hubsNames (list, optional): A list of existing hub names to check for duplicates.

    Returns:
    - hub (dict): The information of the new hub.
    """
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
    """
    Presents a question to the user and expects a specific answer.

    This function presents a question to the user and expects a specific answer. It ensures that the user's input matches the available answer options.

    Parameters:
    - question (str, optional): The question to be presented. If not provided, a default question will be used.
    - answers (list, optional): The available answer options. If not provided, "Y" or "N" will be used.

    Returns:
    - answer (str): The user's selected answer.
    """
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
    """
    Checks whether an associate has a fleet.

    This function checks whether an associate has a fleet by examining the associate's data.

    Parameters:
    - associate (dict): The associate's data.

    Returns:
    - has_fleet (bool): True if the associate has a fleet, False otherwise.
    """
    fleetId = ""

    try:
        fleetId = associate["fleetId"]
    except Exception:
        pass
    
    return fleetId != ""


def get_associate_hubs_from_fleet(env, orgId, associate):
    """
    Retrieves the hub IDs associated with an associate's fleet.

    This function retrieves the hub IDs associated with an associate's fleet. It collects the hub IDs from the fleet and includes the associate's current hub ID if applicable.

    Parameters:
    - env (str): The environment in which the fleet data is stored.
    - orgId (str): The organization ID associated with the fleet.
    - associate (dict): The associate's data.

    Returns:
    - idsList (list): The list of hub IDs associated with the associate's fleet.
    """
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
    """
    Fills a list of hubs by searching for each hub's information.

    This function fills a list of hubs by searching for each hub's information based on the provided hub IDs.

    Parameters:
    - env (str): The environment in which the hub data is stored.
    - orgId (str): The organization ID associated with the hubs.
    - hubIdsList (list): The list of hub IDs to search for.

    Returns:
    - hubsList (list): The list of hub information corresponding to the provided hub IDs.
    """
    hubsList = []

    for hubId in hubIdsList:
        hubsList.append(hubs.search_hub_by_id(env, orgId, hubId)[0])

    return hubsList


def search_fleet_with_hubs(allFleets, hubIdsList):
    """
    Searches for a fleet that contains the exact set of hub IDs.

    This function searches for a fleet that contains the exact set of hub IDs provided. It checks if any fleet matches the hub IDs and returns the fleet ID if found.

    Parameters:
    - allFleets (list): The list of all fleets to search within.
    - hubIdsList (list): The list of hub IDs to match.

    Returns:
    - fleetId (str): The ID of the fleet that matches the provided hub IDs, or None if no match is found.
    """
    hubIdsSet = set(hubIdsList)  # Convert hubIdsList to a set for efficient comparison

    for fleet in allFleets:
        try:
            fleetHubIdsSet = set(fleet['hubIds'])

            if fleetHubIdsSet == hubIdsSet:
                return fleet['fleetId']
        except Exception:
            pass

    print(">>>> Fleet not found!")
    return None


def create_new_fleet(env, orgId, hubsList, fleetName=None, fleetLogo=None):
    """
    Creates a new fleet using the provided information.

    This function creates a new fleet using the provided hub list, fleet name, and fleet logo. It returns the newly created fleet ID.

    Parameters:
    - env (str): The environment in which the fleet will be created.
    - orgId (str): The organization ID associated with the fleet.
    - hubsList (list): The list of hubs to be included in the fleet.
    - fleetName (str, optional): The name of the new fleet. If not provided, the org name will be used.
    - fleetLogo (str, optional): The logo for the new fleet. If not provided, the org logo will be used.

    Returns:
    - fleetId (str): The ID of the newly created fleet.
    """
    fleetId = fleets.create_fleet(env, orgId, hubsList, fleetName, fleetLogo)
    print(f">> {fleetId}")

    return fleetId


def update_associate(env, associate, userName):
    """
    Updates the associate's data.

    This function updates the associate's data using the provided environment, associate information, and the name of the user making the changes. It prints the update status and any relevant error messages.

    Parameters:
    - env (str): The environment in which the associate data is stored.
    - associate (dict): The associate's data to be updated.
    - userName (str): The name of the user making the changes.

    Returns:
    None
    """
    response = associates.update_associate_data(env, associate, userName)

    print(f">> Update Status: {'OK' if response.status_code < 400 else 'FAILED'}")
    print(f"{response.text if response.status_code >= 400 else ''}")


def get_company_name(name):
    """
    Extracts the company name from a given string.

    This function extracts the company name from a given string by removing any spaces after the first word.

    Parameters:
    - name (str): The input string containing the company name.

    Returns:
    - companyName (str): The extracted company name.
    """
    companyName = ""

    for char in name:
        if char != " ":
            companyName += char
        else:
            return companyName
    
    return companyName


def apply_changes(env, orgId, hubsList, allFleets, associate, userName):
    """
    Applies changes to the associate's fleet based on the provided information.

    Parameters:
    - env (str): The environment in which the changes are being applied. Valid values are 'stage', or 'prod'.
    - orgId (int): The ID of the organization to which the associate belongs.
    - hubsList (list): A list of dictionaries containing information about the hubs.
    - allFleets (list): A list of all existing fleets.
    - associate (dict): A dictionary containing LMX information of the associate.
    - userName (str): The name of the user making the changes.

    Returns:
    None
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
            fleetId = associate["fleetId"]
            
            print(f">> Checking if other associates use the same fleet")
            associatesWithSameFleet = associates.search_associate(
                env=env,
                org_id=orgId,
                key_type_index=11,  # fleetId (11)
                search_key=fleetId
            )
            
            if len(associatesWithSameFleet) == 1 and associatesWithSameFleet is not None:
                # if only this associate has this fleet id
                # means we can just update his fleet instead of creating another one
                print(">> No other associate use this fleetId")

                print(f">> Updating Fleet: {fleets.update_fleet_hubs(env, orgId, fleetId, hubsList)}")
            else:
                # In this case we need to create a new fleet
                print(">> Someone else uses this fleetId as well")
                fleet = fleets.search_fleet(env, orgId, fleetId)
                companyName = get_company_name(associate.get('companyId'))
                fleetId = create_new_fleet(env, orgId, hubsList, companyName, fleet.get('logoUrl'))

                associate["fleetId"] = fleetId

                update_associate(env, associate, userName)
        else:
            print(">> Associate doesn't have a fleet")
            print(f">> Creating new fleet with {' '.join(hubsNames)}")
            fleetId = create_new_fleet(env, orgId, hubsList, associate.get('companyId'))

            associate["fleetId"] = fleetId

            update_associate(env, associate, userName)


def move_to_new_hub(env, orgId, associate, userName, newHub=None):
    """
    Moves the associate to a new hub and updates their information accordingly.

    Parameters:
    - env (str): The environment in which the changes are being applied.
    - orgId (int): The ID of the organization to which the associate belongs.
    - associate (dict): A dictionary containing information about the associate.
    - userName (str): The name of the user making the changes.
    - newHub (dict, optional): A dictionary containing information about the new hub. If not provided, the user will be prompted to enter the new hub's name.

    Returns:
    None
    """
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
    """
    The main function that interacts with the user, retrieves associate information, and performs necessary actions based on the associate's type and input.

    This function prompts the user to enter the associate's ID, name, fleet information, and the desired action to be performed. It then validates the input, retrieves additional information if needed, and executes the corresponding function based on the associate's type and action.

    Parameters:
    None

    Returns:
    None
    """
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
