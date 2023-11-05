import concurrent.futures
import grantHubAccess
from utils import utils, associates, fleets, files


ASSOCIATES = []


def get_associate(env, orgId, associateId):
    associate = associates.get_associate_data(env, orgId, associateId)

    if associate != None:
        ASSOCIATES.append(associate)
    else:
        print(f">> {associateId} not found")


def get_new_hubs(env, orgId, hubsNames):
    hubName = "init"
    newHubs = []
    updated = False

    while hubName != "" and not updated:
        hubName = input(
            ">> Type the new HUB's name "
            "(leave blank if done)\n"
            "> "
        ).strip().upper()

        if hubName != "":
            newHub = grantHubAccess.get_new_hub(env, orgId, hubName, hubsNames)
            hubsNames.append(newHub.get('name'))

            newHubs.append(newHub)
            updated = True
    
    return newHubs


def main():
    """
    The main function of the script for managing associate access to hubs within fleets and handling driver/sorter associates differently. The script allows users to make decisions regarding access and updates based on prompts and user input.

    This function performs the following logical steps:

    1. Prompt the user for their name.
    2. Select an environment (env) using a utility function.
    3. Select an organization (orgId) within the chosen environment.
    4. Read 'associates.txt' to retrieve Associate IDs.
    5. Launch a thread pool for parallel processing of associate data.
    6. For each Associate ID, fetch associate details in parallel threads.
    7. Search for all fleets within the selected environment and organization.
    8. Iterate through each associate and manage their access to hubs or perform actions based on their role.

    Ensure that the necessary utility functions, input/output mechanisms, and dependencies are properly configured for the script to execute successfully.
    """
    userName = input("What is your name?\n> ")
    env = utils.select_env()
    orgId = utils.select_org(env)

    print("Reading 'associates.txt' to get Associate IDs")
    associateIDs = files.get_data_from_file("associates")

    # Using multithreading to get multiple associates simultaneosly
    with concurrent.futures.ThreadPoolExecutor() as pool:
        for associateId in associateIDs:
            pool.submit(get_associate, env, orgId, associateId)
        pool.shutdown(True)

    allFleets = fleets.search_fleet(env, orgId)
    # print(f">> Loaded {len(allFleets)} fleets")

    for associate in ASSOCIATES:
        name = associate.get('contact').get('name')
        print(f"============ STARTING {str(name).upper} ============")

        if associate["associateType"] not in ["DRIVER", "SORTER"]:
            hubsIds = grantHubAccess.get_associate_hubs_from_fleet(env, orgId, associate)
            hubsList = grantHubAccess.fill_hubs_list(env, orgId, hubsIds)
            hubsNames = [h.get('name') for h in hubsList]
            
            print(f">> HUBs: {' '.join(hubsNames)}\n")

            newHubs = get_new_hubs(env, orgId, hubsNames)
            answer = grantHubAccess.select_answer()

            if answer == "Y":
                for newHub in newHubs:
                    hubsList.append(newHub)

                grantHubAccess.apply_changes(env, orgId, hubsList, allFleets, associate, userName)
            else:
                if len(hubsList) > 1:
                    grantHubAccess.apply_changes(env, orgId, hubsList, allFleets, associate, userName)
                else:
                    print(f">> Answer was '{answer}' and only 1 HUB was informed...")
                    grantHubAccess.move_to_new_hub(
                        env,
                        orgId,
                        associate,
                        userName,
                        hubsList[0]
                    )
        else:
            print(f">> {name} is a driver/sorter. We can't give drivers access to other hubs!")
            answer = grantHubAccess.select_answer(question="Do you want to move this associate to a new HUB?")

            if answer == "Y":
                grantHubAccess.move_to_new_hub(
                    env,
                    orgId,
                    associate,
                    userName
                )

        print(f"============ FINISHED {str(name).upper} ============\n\n")


main()
# How the script works:
# - Get associate IDs from 'associates.txt,' with each new line representing a new associate ID. No need for special formatting.
# - Use multithreading to search for associate IDs and save them in the ASSOCIATES List when found.
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
