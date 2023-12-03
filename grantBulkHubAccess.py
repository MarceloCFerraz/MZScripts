import concurrent.futures
import grantHubAccess
from utils import utils, associates, fleets, files, hubs


ASSOCIATES = []


def get_associate(env, orgId, associateId):
    """
    Retrieves associate data and adds it to the ASSOCIATES list.

    This function retrieves the associate data for a given `associateId` using the `get_associate_data` function from the `associates` module. If the associate is found, their data is appended to the ASSOCIATES list. If the associate is not found, a message is printed indicating that the associate was not found.

    Parameters:
    - env (str): The environment.
    - orgId (str): The organization ID.
    - associateId (str): The associate ID to retrieve.

    Returns:
    None
    """
    associate = associates.get_associate_data(env, orgId, associateId)

    if associate != None:
        ASSOCIATES.append(associate)
    else:
        print(f">> {associateId} not found")


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

    print(">> Reading 'associates.txt' to get Associate IDs")

    associateIDs = files.get_data_from_file("associates")

    if associateIDs == []:

        print(">> No associates in 'associates.txt'")
        if grantHubAccess.select_answer(question="Do you want to search for the associates?") == "Y":
            associateID = grantHubAccess.get_associate(env, orgId, False)

            while associateIDs == [] and associateID == None:
                associateID = grantHubAccess.get_associate(env, orgId, True)

                if associateID != None:
                    associateIDs.append(associateID)
                elif associateIDs == []:
                    print(">> The associates list is empty. Please enter an associate or hit CTRL + C to quit the program")
                    associateID = grantHubAccess.get_associate(env, orgId, True)
                else:
                    break
    else:
        # Using multithreading to get multiple associates simultaneosly
        with concurrent.futures.ThreadPoolExecutor() as pool:
            for associateId in associateIDs:
                pool.submit(get_associate, env, orgId, associateId)
        pool.shutdown(True)
    
    for associate in ASSOCIATES:
        allFleets = fleets.search_fleet(env, orgId)
        print()
        allHubs = hubs.get_all_hubs(env, orgId)
        print()
        grantHubAccess.main(env, orgId, associate, userName, allHubs, allFleets)


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
