import sys

from utils import associates, fleets, hubs, utils


def get_associate(env, orgId, acceptBlank, allHubs: list):
    """
    Retrieves associate data based on the associate's ID or search key.

    Parameters:
    - env (str): The environment in which the associate data is stored.
    - orgId (str): The organization ID associated with the associate.
    - acceptBlank (bool): Whether to accept blank input from the user.

    Returns:
    - associate (dict): an associate LMX data.
    - None: if an associate wasn't found or if blank input is allowed
    """
    answer = select_answer(question=">> Do you have an associate ID? ")

    if answer == "Y":
        associate = get_associate_by_id(env, orgId, acceptBlank)
    else:
        associate = get_associate_by_name_or_email(env, orgId, acceptBlank, allHubs)

    return associate


def get_associate_by_id(env, orgId, acceptBlank):
    """
    Retrieves associate data based on the associate's ID.

    Parameters:
    - env (str): The environment in which the associate data is stored.
    - orgId (str): The organization ID associated with the associate.
    - acceptBlank (bool): Whether to accept blank input from the user.

    Returns:
    - associate (dict): an associate LMX data.
    - None: if an associate wasn't found or if blank input is allowed
    """
    while True:
        print(
            ">> Insert the Associate ID ",
            (
                "(leave blank and hit enter if done)"
                if acceptBlank
                else "(or hit Ctrl + C to quit program)"
            ),
        )
        associateId = input("> ")

        if associateId == "":
            if acceptBlank:
                return None
            else:
                print(
                    ">> Can't accept blank. Try again (or hit Ctrl + C to quit program)"
                )
        else:
            return associates.get_associate_data(env, orgId, associateId)


def get_associate_by_name_or_email(env, orgId, acceptBlank, allHubs: list):
    """
    Retrieves associate data based on the associate's name or email.

    Parameters:
    - env (str): The environment in which the associate data is stored.
    - orgId (str): The organization ID associated with the associate.
    - acceptBlank (bool): Whether to accept blank input from the user.

    Returns:
    - associate (dict): an associate LMX data.
    - None: if an associate wasn't found or if blank input is allowed
    """
    # TODO: list associates found and ask user to select one
    while True:
        print(
            ">> Type the associate's e-mail or name ",
            (
                "(leave blank and hit enter if done)"
                if acceptBlank
                else "(or hit Ctrl + C to quit program)"
            ),
        )
        search_key = input("> ")
        print()

        if search_key == "" and acceptBlank:
            return None

        search_key_index = 3 if "@" in search_key else 2
        # based on key_types list in associates.search_associate()

        associate = associates.search_associate(
            env, orgId, search_key_index, search_key
        )

        if not associate:
            msg = ">> Associate not found"
            blankMsg = " and blank is not allowed"
            end = ". Try again or hit CTRL + C to quit"

            if not acceptBlank:
                print(msg + blankMsg + end)
            else:
                print(msg + " but we'll continue anyway")
                return None

            continue

        if len(associate) > 1:
            associate = choose_associate(associate, allHubs)
        else:
            associate = associate[0]

        # choose_associate can return None
        if associate:
            return associate


def get_new_hubs(hubsNames: list[str], allHubs: list[dict]):
    """
    Retrieves new hubs and adds them to the newHubs list.

    This function prompts the user to enter the names of new hubs. It continues to prompt until the user leaves the input blank. For each new hub name entered, it calls the `get_new_hub` function from the `grantHubAccess` module to retrieve the hub data. The retrieved hub data is then added to the `newHubs` list, and the hub name is appended to the `hubsNames` list. The function stops prompting for new hub names if the user leaves the input blank or if the `updated` flag is set to True.

    Parameters:
    - env (str): The environment.
    - orgId (str): The organization ID.
    - hubsNames (list): The list of existing hub names.

    Returns:
    - newHubs (list): The list of new hub data.
    """
    hubName = "init"
    newHubs = []
    old_hub_names = hubsNames.copy()
    updated = False

    while hubName != "" and not updated:
        print(
            f">> HUBs: {print_old_hub_names(old_hub_names)}"
            + f" {print_new_hub_names(newHubs)}"
        )

        print(">> Type the new HUB's name (leave blank and hit enter if done)")

        newHub = get_new_hub(allHubs, hubsNames, True, None)

        if newHub is None:  # means the user entered a blank line
            break

        hubsNames.append(newHub.get("name"))
        newHubs.append(newHub)

    return newHubs


def print_old_hub_names(old_hub_names: list[str]):
    if not old_hub_names:
        return ""

    hubs_names = [h for h in old_hub_names]
    hubs_names.sort()

    return " ".join(hubs_names)


def print_new_hub_names(new_hubs: list[dict]):
    if not new_hubs:
        return ""

    hubs_names = [h["name"] for h in new_hubs]
    hubs_names.sort()

    hubs_names_with_parenthesis = [f"({h})" for h in hubs_names]

    return " ".join(hubs_names_with_parenthesis)


def get_new_hub(allHubs, hubsNames, acceptBlank, hubName=None):
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
    if hubName is None:
        hubName = input("> ").strip().upper()

        if hubName == "" and acceptBlank:
            return None

    newHub = list(filter(lambda h: h["name"] == hubName, allHubs))

    if newHub != []:  # if hubName is valid and exists
        newHub = newHub[0]

        if (
            hubsNames is not None and newHub["name"] not in hubsNames
        ):  # and if it is not on the associate's hub list already
            return newHub
        else:
            print(f"\n>> Associate already have access to {hubName}")
    else:
        print(f"\n>> {hubName} does not exist.")

    print(
        ">> Try again", " (leave blank and hit enter if done)" if acceptBlank else ""
    )  # this can't be prompted always
    return get_new_hub(allHubs, hubsNames, acceptBlank, None)


def select_answer(question=None, answers=None):
    """
    Presents a question to the user and expects a specific answer.

    This function presents a question to the user and expects a specific answer. It ensures that the user's input matches the available answer options.

    Parameters:
    - answers (list, optional): The available answer options. If not provided, "Y" or "N" will be used.
    - question (str, optional): The question to be presented. If not provided, a default question will be used:
        - `Does the associate need to maintain access to all previous hubs? `

    Returns:
    - answer (str): The user's selected answer.
    """
    if answers is None:
        answers = ["Y", "N"]

    if question is None:
        question = (
            "\n>> Does the associate need to maintain access to all previous hubs? "
        )

    question = question + f"({'/'.join(answers)})"

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


def get_hubs_from_associate_fleet(associate, allFleets, allHubs):
    """
    Retrieves the hub IDs associated with an associate's fleet.

    This function retrieves the hub IDs associated with an associate's fleet. It collects the hub IDs from the fleet and includes the associate's current hub ID if applicable.

    Parameters:
    - associate (dict): The associate's data.
    - allFleets (list[dict]): A list with every hub on the organization
    - allHubs (list[dict]): A list with every hub on the organization

    Returns:
    - hubsList (list[dict]): The list of hubs associated with the associate's fleet.
    """
    idsList = []
    fleet = ""

    if associate_has_fleet(associate):
        fleet = associate["fleetId"]
        print(f">> Associate has fleet {fleet}")

        fleetHubs = [f["hubIds"] for f in allFleets if f["fleetId"] == fleet]
        if fleetHubs != []:
            fleetHubs = fleetHubs[0]

            for hubId in fleetHubs:
                idsList.append(hubId)

    if associate.get("hubId") not in idsList:
        idsList.append(associate.get("hubId"))

    hubsList = fill_hubs_list(idsList, allHubs)

    return hubsList


def fill_hubs_list(idsList, allHubs):
    """
    Fills a list of hubs by searching for each hub's information.

    This function fills a list of hubs by searching for each hub's information based on the provided hub IDs.

    Parameters:
    - idsList (list): A list with the hubIds from the associate's fleet
    - allHubs (list[dict]): A list with every hub on the associate's organization

    Returns:
    - hubsList (list[dict]): The list of hub information corresponding to the provided hub IDs.
    """
    hubsList = []

    for hubId in idsList:
        h = list(
            filter(lambda h: h["id"] == hubId, allHubs)
        )  # a list with every match of the hubID

        if h != []:  # if hubName is valid and exists
            h = h[0]
            hubsList.append(h)  # Add found hub to the hubsList

    return hubsList


def search_fleet_with_hubs(allHubs, allFleets, hubIdsList: list):
    """
    Searches for a fleet that contains the exact set of hub IDs.

    This function searches for a fleet that contains the exact set of hub IDs provided. It checks if any fleet matches the hub IDs and returns the fleet ID if found.

    Parameters:
    - allFleets (list): The list of all fleets to search within.
    - hubIdsList (list): The list of hub IDs to match.

    Returns:
    - fleetId (str): The ID of the fleet that matches the provided hub IDs, or None if no match is found.
    """
    MAX_FLEET_DIFFERENCE = 20
    print(
        f"* We'll consider compatible fleets any fleet with the requested hubs plus up to {MAX_FLEET_DIFFERENCE} more hubs, never less"
    )

    fleetCandidates = []
    for fleet in allFleets:
        try:
            valid = True
            index = 0

            while index in range(0, len(hubIdsList)) and valid:
                hubId = hubIdsList[index]

                if hubId not in fleet["hubIds"]:
                    valid = False

                index += 1

            if valid:
                difference = len(fleet["hubIds"]) - len(hubIdsList)

                perfectMatch = difference == 0
                belowMax = difference <= MAX_FLEET_DIFFERENCE

                if perfectMatch:
                    print(f">> {fleet['fleetId']} is a perfect match!")
                    return fleet["fleetId"]

                if belowMax:
                    print(f">> {fleet['fleetId']} is valid ({difference} extra hubs)")
                    fleetCandidates.append(fleet)

        except Exception:
            pass

    if len(fleetCandidates) == 0:
        # No viable option found
        return None

    return choose_fleet_candidate(fleetCandidates, hubIdsList, allHubs)


def choose_associate(associatesList: list, allHubs: list) -> dict | None:
    """
    Iterates through each associate in associates list and gives the user the option to select a associate that offers a better fit or select none.

    The section below prints something like this:
        ```text
        >> 0 - NAME 1 - E-MAIL 1 - ID 1
        >> 1 - NAME 2 - E-MAIL 2 - ID 2
        >> 2 - NAME 3 - E-MAIL 3 - ID 3
        ```

    Returns:
        associate (dict): the associate data if the user selected a associate from the options array
    """
    print(f">> We found {len(associatesList)} compatible associates:")
    index = 0

    for index in range(0, len(associatesList)):
        id = associatesList[index]["associateId"]
        name = associatesList[index]["contact"]["name"]
        email = associatesList[index]["contact"]["email"]
        accountType = associatesList[index]["associateType"]
        state = associatesList[index]["state"]
        hubId = associatesList[index]["hubId"]
        hub = [h["name"] for h in allHubs if h["id"] == hubId]
        if hub:
            hub = hub[0]
        else:
            hub = "NA"

        print(f"{index}: {name} ({state}) - {email} - {hub} - {accountType} - {id}")

    selection = -1
    quit = -7

    print(f"\n>> Please type the number of the associate or '{quit}' to quit")
    while selection not in range(0, len(associatesList)):
        try:
            selection = int(input("> ").strip())

            if selection == quit:
                return None

        except ValueError:
            print(
                "\n>> Please type only the number of the desired associate. For example:"
            )
            print(">> 0 << - NAME 1 - E-MAIL 1 - ID 1")
            print(">> 1 << - NAME 2 - E-MAIL 2 - ID 2")

    return associatesList[selection]


def choose_fleet_candidate(fleetCandidates, hubIdsList, hubsList):
    """
    Iterates through each fleet in fleet candidates list and gives the user the option to select a fleet that offers a better fit or select none.

    The section below prints something like this:
        ```text
        >> 0 - HUB1     HUB2     HUB3     HUB4     HUB5     HUB6(+)
        >> 1 - HUB1     HUB2     HUB3     HUB4     HUB5     HUB7(+)
        >> 2 - HUB1     HUB2     HUB3     HUB4     HUB5     HUB6(+)     HUB7(+)
        ```

    Returns:
        fleetId (str): the fleet id if the user selected a fleet from the options array
    """
    print(f">> We found {len(fleetCandidates)} compatible fleets:")
    print(">> '(+)' is a hub that was not in the original search list")

    desiredHubs = [h["name"] for h in hubsList if h["id"] in hubIdsList]
    index = 0

    for index in range(0, len(fleetCandidates)):
        fleetHubIds = fleetCandidates[index]["hubIds"]
        fleetId = fleetCandidates[index]["fleetId"]

        fleetHubs = [h["name"] for h in hubsList if h["id"] in fleetHubIds]

        printString = [
            f"{'' if hub in desiredHubs else '(+)'}{hub}" for hub in fleetHubs
        ]
        printString.sort(reverse=True)

        printString = [f"{string:<9}" for string in printString]

        print(f">> {index:<2} ({fleetId})")
        print(f"\n{''.join(printString)}\n")

    selection = -1
    quit = -7

    print(f"\n>> Please type the number of the fleet or '{quit}' to quit")
    while selection not in range(0, len(fleetCandidates)):
        try:
            selection = int(input("> ").strip())

            if selection == quit:
                return None

        except ValueError:
            print("\n>> Please type only the number of the desired fleet. For example:")
            print(">> 0 << - HUB1  HUB2  HUB3  HUB4")
            print(">> 1 << - HUB1  HUB2  HUB3  HUB4\n")

    return fleetCandidates[selection]["fleetId"]


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
    print(">> Creating fleet")
    fleetId = fleets.create_fleet(env, orgId, hubsList, fleetName, fleetLogo)
    print(f">>>> {fleetId}")

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
    print(f">> Updating associate {associate['associateId']}")
    response = associates.update_associate_data(env, associate, userName)

    print(f">> Update Status: {'OK' if response.status_code < 400 else 'FAILED'}")
    print(">>" + response.text if response.status_code >= 400 else "")


def update_fleet(env, orgId, fleetId, hubsList):
    print(f">> Updating Fleet {fleetId}")
    response = fleets.update_fleet_hubs(env, orgId, fleetId, hubsList)

    print(f">> Update Status: {'OK' if response.status_code < 400 else 'FAILED'}")
    print(">> " + response.text if response.status_code >= 400 else "")


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


def apply_changes(env, orgId, allHubs, hubsList, allFleets, associate, userName):
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
    hubsNames = [h.get("name") for h in hubsList]
    hubsIds = [h.get("id") for h in hubsList]

    print(f"\n>> Searching for a fleet with {' '.join(hubsNames)}")
    fleetId = search_fleet_with_hubs(  # searching for a fleet with same hubs
        allHubs=allHubs, allFleets=allFleets, hubIdsList=hubsIds
    )

    if fleetId is not None:  # if a fleet with the correct hubs already exists
        print(f">>>> Updating associate with: {fleetId}")
        associate["fleetId"] = fleetId

        update_associate(env, associate, userName)
    else:
        print(">> Fleet not found")

        if associate_has_fleet(associate):  # if associate already have a fleetId
            fleetId = associate["fleetId"]

            print(">> Checking if other associates use the same fleet")
            associatesWithSameFleet = associates.search_associate(
                env=env,
                org_id=orgId,
                key_type_index=11,  # fleetId (11)
                search_key=fleetId,
            )

            if (
                associatesWithSameFleet is not None
                and len(associatesWithSameFleet) == 1
            ):
                # if only this associate has this fleet id
                # means we can just update his fleet instead of creating another one
                print(">> No other associate use this fleetId")

                if (
                    select_answer(question=">> Do you want to update the fleet? ")
                    == "N"
                ):
                    sys.exit(1)
                update_fleet(env, orgId, fleetId, hubsList)
            else:
                # In this case we need to create a new fleet
                print(">> Someone else share the same fleetId")

                if (
                    select_answer(question=">> Do you want to create a new fleet? ")
                    == "N"
                ):
                    sys.exit(1)
                print(f">> Creating new fleet with {' '.join(hubsNames)}")

                fleet = [f for f in allFleets if f["fleetId"] == associate["fleetId"]][
                    0
                ]
                companyName = get_company_name(associate.get("companyId"))
                fleetId = create_new_fleet(
                    env, orgId, hubsList, companyName, fleet.get("logoUrl")
                )

                associate["fleetId"] = fleetId

                update_associate(env, associate, userName)
        else:
            print(">> Associate doesn't have a fleet")
            print(f">> Creating new fleet with {' '.join(hubsNames)}")
            fleetId = create_new_fleet(env, orgId, hubsList, associate.get("companyId"))

            associate["fleetId"] = fleetId

            update_associate(env, associate, userName)


def move_to_new_hub(env, associate, userName, newHub):
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
    print(
        f">> Changing hub ID and location ID to {newHub['id']} and {newHub['location']['locationId']}"
    )

    associate["hubId"] = newHub["id"]
    associate["location"]["locationId"] = newHub["location"]["locationId"]

    newAssociateData = {}

    print(">> Removing fleet, vehicle and route")
    for header in associate.keys():
        if header not in ["fleetId", "preferredVehicle", "preferredRoute"]:
            newAssociateData[header] = associate[header]

    update_associate(env, newAssociateData, userName)


def process_associate(env, orgId, associate, userName, allHubs, allFleets):
    """
    The function that performs necessary actions based on the associate's type and input.

    Executes the corresponding function based on the associate's type and action.

    Parameters:
        env (str): prod or stage
        orgId (str): the ID of the associate's org
        associate (dict): the associate data
        userName (str): who is operating the script
        allHubs (list[dict]): all hubs from org to avoid multiple API calls
        allFleets (list[dict]): all fleets from org to avoid multiple API calls

    Returns:
    None
    """
    name = associate.get("contact").get("name")
    associate_id = associate.get("associateId")

    print(f"{f' PROCESSING {str(name).upper()} ':#^50}")
    print(f"Associate ID: {associate_id}")
    print()

    if associate["associateType"] not in ["DRIVER", "SORTER"]:
        hubsList = get_hubs_from_associate_fleet(associate, allFleets, allHubs)
        hubsNames = [h.get("name") for h in hubsList]

        newHubs = get_new_hubs(hubsNames, allHubs)
        answer = select_answer()
        print()

        if answer == "Y":
            # associate needs to maintain his previous hubs + the new one(s)
            for newHub in newHubs:
                hubsList.append(newHub)

            print(">> Adding access to new hubs...")
            apply_changes(env, orgId, allHubs, hubsList, allFleets, associate, userName)
        else:
            # associate doesn't need the previous hubs,
            if len(newHubs) > 1:
                # only the new ones
                print(">> Granting access to new hubs only...")
                apply_changes(
                    env, orgId, allHubs, newHubs, allFleets, associate, userName
                )
            else:
                # only the new one, so move him to the new hub
                print(">> Moving associate to new hub...")
                move_to_new_hub(env, associate, userName, newHubs[0])
    else:
        print(
            f"\n>> {name} is a driver/sorter. We can't give drivers access to other hubs!"
        )
        answer = select_answer(
            question="Do you want to move this associate to a new HUB? "
        )

        if answer == "Y":
            hub = [h["name"] for h in allHubs if h["id"] == associate["hubId"]]
            print(f">> The associate currently have access to: {' '.join(hub)}")
            print(">> What should be the new hub?")

            newHub = get_new_hub(allHubs, hub, False, None)
            move_to_new_hub(env, associate, userName, newHub)

    print(f"{f' FINISHED {str(name).upper()} ':#^50}")


def main():
    """
    The initialization function that interacts with the user, retrieves associate information, and calls process_associate logic. performs necessary actions based on the associate's type and input.

    This function prompts the user to enter the associate's ID, name, fleet information, and the desired action to be performed. It then validates the input, retrieves additional information if needed, and executes the corresponding function based on the associate's type and action.

    Parameters:
    None

    Returns:
    None
    """
    userName = input("What is your name?\n> ")
    env = utils.select_env()
    orgId = utils.select_org(env)

    allFleets = fleets.search_fleet(env, orgId)
    allHubs = hubs.get_all_hubs(env, orgId)

    associate = get_associate(env, orgId, False, allHubs)

    process_associate(env, orgId, associate, userName, allHubs, allFleets)


if __name__ == "__main__":
    main()
