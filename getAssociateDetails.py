from utils import associates, files, hubs, utils


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
    key_type_index = utils.get_associate_key_type_index()

    allHubs = hubs.get_all_hubs(env, orgId)

    # TODO: allow user to search for more than one field
    associatesArray = []
    if key_type_index > 0:
        print(f"TYPE THE ASSOCIATE'S '{utils.get_associate_key_type(key_type_index)}'")
        search_key = str(input("> ")).strip()
    else:
        search_key = orgId

    if key_type_index == 1:
        associatesArray = [
            associates.get_associate_data(env, orgId, associateId=search_key)
        ]
    else:
        associatesArray = associates.search_associate(
            env=env,
            org_id=orgId,
            key_type_index=key_type_index - 1,
            search_key=search_key,
        )

    if associatesArray is not None:
        associates_count = len(associatesArray)
        print(f"Found {associates_count} associates")

        if associates_count <= 10:
            for associate in associatesArray:
                if associate is not None:
                    extra_details = associates.get_associate_device_and_app(
                        env, orgId, associate["associateId"]
                    )
                    hub = [h for h in allHubs if h.get("id") == associate["hubId"]][0]
                    spaces = 20

                    print(f"{'Associate State: ': >{spaces}}{associate['state']}")
                    print(f"{'Account Type: ': >{spaces}}{associate['associateType']}")
                    print(f"{'Associate ID: ': >{spaces}}{associate['associateId']}")
                    print(
                        f"{'User Name: ': >{spaces}}{associate['contact']['userName']}"
                    )
                    print(f"{'Name: ': >{spaces}}{associate['contact']['name']}")
                    print(f"{'E-Mail: ': >{spaces}}{associate['contact']['email']}")
                    print(f"{'Phone: ': >{spaces}}{associate['contact']['phone']}")
                    print(
                        f"{'Location ID: ': >{spaces}}{associate['location']['locationId']}"
                    )
                    print(f"{'WorldView ID: ': >{spaces}}{associate['worldViewId']}")
                    try:
                        print(f"{'Fleet ID: ': >{spaces}}{associate['fleetId']}")
                    except Exception:
                        pass
                    print(f"{'HUB ID: ': >{spaces}}{associate['hubId']}")
                    print(f"{'HUB Name: ': >{spaces}}{hub.get('name')}")
                    print(
                        f"{'Preferred Vehicle: ': >{spaces}}{associate.get('preferredVehicle')}"
                    )
                    print(
                        f"{'Preferred Route: ': >{spaces}}{associate.get('preferredRoute')}"
                    )

                    if (
                        extra_details is not None
                        and extra_details.get("extraProperties") is not None
                    ):
                        try:
                            extra_details = extra_details["extraProperties"]
                            print(
                                f"{'Phone: ': >{spaces}}{str(extra_details['deviceName']).capitalize() + ' ' + str(extra_details['deviceModel'])}"
                            )
                            print(
                                f"{'OS Version: ': >{spaces}}{str(extra_details['type']).capitalize() + ' ' + str(extra_details['osVersion'])}"
                            )
                            print(
                                f"{'App Version: ': >{spaces}}{extra_details['appVersion']}"
                            )
                        except Exception:
                            pass
                    print("========================================")
        else:
            print(
                "Too many associates, check 'RESULTS' folder to see the full response!"
            )
            files.save_json_to_file(
                filePrefix="ASSOCIATES", jsonData=files.format_json(associatesArray)
            )


if __name__ == "__main__":
    main()
