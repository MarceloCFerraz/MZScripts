from utils import files, utils, associates


def main():
    env = utils.select_env()
    orgId = utils.select_org(env)
    key_type_index = utils.get_associate_key_type_index()

    if key_type_index > 0:
        print(f"TYPE THE ASSOCIATE'S '{utils.get_associate_key_type(key_type_index)}'")
        search_key = input("> ")
    else:
        search_key = orgId

    associatesArray = associates.search_associate(
        env=env,
        org_id=orgId,
        key_type_index=key_type_index,
        search_key=search_key
    )
    associates_count = len(associatesArray)
    print(f"Found {associates_count} associates")

    if associates is not None:
        if associates_count <= 10:
            for associate in associatesArray:
                print(f"Associate State: {associate['state']}")
                print(f"Account Type: {associate['associateType']}")
                print(f"Associate ID: {associate['associateId']}")
                print(f"   User Name: {associate['contact']['userName']}")
                print(f"        Name: {associate['contact']['name']}")
                print(f"      E-Mail: {associate['contact']['email']}")
                print(f"       Phone: {associate['contact']['phone']}")
                print(f"Location ID: {associate['location']['locationId']}")
                print(f"HUB ID: {associate['hubId']}")
                try:
                    print(f"Fleet ID: {associate['fleetId']}")
                except Exception:
                    pass
                print(f"WorldView ID: {associate['worldViewId']}\n")
        else:
            print("Too many associates, check 'RESULTS' folder to see the full response!")
            files.save_json_to_file(filePrefix="ASSOCIATES", jsonData=files.format_json(associatesArray))


main()
