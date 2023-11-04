from utils import files, utils, associates, hubs


def get_hub_id(env, orgId):
    print("TYPE THE HUB NAME (numbers only)")
    hubName = input("> ").strip()

    hub = hubs.search_hub_by_name(env=env, orgId=orgId, hubName=hubName)[0]
    print(f"{hubName}'s id is {hub['id']}")

    return hub


def main():
    env = utils.select_env()
    orgId = utils.select_org(env)

    hub = get_hub_id(env, orgId)

    associatesArray = associates.search_associate(
        env=env,
        org_id=orgId,
        key_type_index=14,
        search_key=hub["id"]
    )

    associates_count = len(associatesArray)
    print(f"Found {associates_count} associates")

    if associates is not None:
        files.save_txt_file(
            filePrefix=f"ASSOCIATES_FROM_{hub['name']}", 
            data=[associate['associateId'] for associate in associatesArray ]#if associate["associateType"] not in ["DRIVER", "SORTER"]]
        )


main()
