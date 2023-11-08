from utils import files, utils, associates, hubs


def main():
    """
    Retrieves and displays associate details based on the selected key type.

    This function prompts the user to select the environment and organization ID. It then prompts the user to select the key type index. If the key type index is greater than 0, the function prompts the user to enter the associate's specific key. Otherwise, it uses the organization ID as the search key. The function retrieves the associate data based on the selected environment, organization ID, key type index, and search key. The function prints the number of associates found and their details, including their state, account type, associate ID, contact information, location ID, hub ID, fleet ID (if available), and WorldView ID. If there are more than 10 associates, a message is displayed indicating that there are too many associates, and the full response is saved in the 'RESULTS' folder.

    Parameters:
    - None

    Returns:
    - None
    """
    env = utils.select_env()
    orgId = utils.select_org(env)
    allHubs = hubs.get_all_hubs(env, orgId)
    
    key_type_index = utils.get_associate_key_type_index()

    if key_type_index > 0:
        print(f"TYPE THE ASSOCIATE'S '{utils.get_associate_key_type(key_type_index)}'")
        search_key = input("> ")
    else:
        search_key = orgId

    if key_type_index == 1:
        associatesArray = [associates.get_associate_data(env, orgId, associateId=search_key)]
    else:
        associatesArray = associates.search_associate(
            env=env,
            org_id=orgId,
            key_type_index=key_type_index - 1,
            search_key=search_key
        )
    associates_count = len(associatesArray)
    print(f"Found {associates_count} associates")

    if associates is not None:
        if associates_count <= 10:
            for associate in associatesArray:
                hub = [hub for hub in allHubs if hub["id"] == associate["hubId"]][0]
                print(f"Associate State: {associate['state']}")
                print(f"   Account Type: {associate['associateType']}")
                print(f"   Associate ID: {associate['associateId']}")
                print(f"      User Name: {associate['contact']['userName']}")
                print(f"           Name: {associate['contact']['name']}")
                print(f"         E-Mail: {associate['contact']['email']}")
                print(f"          Phone: {associate['contact']['phone']}")
                print(f"    Location ID: {associate['location']['locationId']}")
                print(f"   WorldView ID: {associate['worldViewId']}\n")
                try:
                    print(f"       Fleet ID: {associate['fleetId']}")
                except Exception:
                    pass
                print(f"         HUB ID: {associate['hubId']}")
                print(f"       HUB Name: {hub.get('name')}")
        else:
            print("Too many associates, check 'RESULTS' folder to see the full response!")
            files.save_json_to_file(filePrefix="ASSOCIATES", jsonData=files.format_json(associatesArray))


main()
