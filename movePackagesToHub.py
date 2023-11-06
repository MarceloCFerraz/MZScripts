import requests
from utils import files, utils, packages


def main():
    """
    Prompts for user input, retrieves package IDs from a file, and moves each package to the specified hub.

    Returns:
    None
    """
    userName = input("What is your name?\n> ").strip()
    dispatcher = input("Who requested this change?\n> ").strip()
    env = utils.select_env()
    orgId = utils.select_org(env)
    newHub = input("Type in the new hub name\n> ").strip()

    packageIds = files.get_data_from_file("pids")

    for packageId in packageIds:
        packages.move_package_to_hub(env, orgId, newHub, packageId, dispatcher, userName)


main()