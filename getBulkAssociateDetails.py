from utils import files, utils, associates


def main():
    env = utils.select_env()
    orgId = utils.select_org(env)

    key_type_index = utils.get_associate_key_type_index()

    search_keys = files.get_data_from_file("associates")
    associatesArray = []
    
    allOrgAssociates = list(associates.search_associate(env, orgId, 0, orgId))

    for search_key in search_keys:
        if key_type_index == 0:
            search_key = orgId

        search_results = [a for a in allOrgAssociates if a[utils.ASSOCIATE_KEY_TYPES[key_type_index]] == search_key]
        for associate in search_results:
            associatesArray.append(associate)

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
