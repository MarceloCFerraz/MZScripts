from utils import files, utils, packages

def main(env:str, org_id:str, keys:list[str], key_type: str) -> dict:
    response = {
        "successes": [],
        "failures": [],
    }

    batches = utils.divide_into_batches(keys)
    pids = set()

    for batch in batches:
        pkgs = packages.bulk_get_package_details(env, org_id, key_type, keys)

        for pk

    try:
        res = packages.revive_package(env, org_id, )
    except Exception ex:
        

    return response


if __name__ == "__main__":
    env = utils.select_env()
    org_id = utils.select_org(env)
    key_type = packages.select_key_type()
    file_name = input(f"Please provide the file with your {key_type.upper()}s: ").strip()
    keys = files.get_data_from_file(file_name, True)

    results = main(env, org_id, keys, key_type)