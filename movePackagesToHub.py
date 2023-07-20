import requests
from utils import files, utils, packages


def main():
    userName = input("What is your name?\n> ").strip()
    dispatcher = input("Who requested this change?\n> ").strip()
    env = utils.select_env()
    orgId = utils.select_org(env)
    newHub = input("Type in the new hub name\n> ").strip()

    packageIds = files.get_data_from_file("pids")

    for packageId in packageIds:
        packages.move_package(env, orgId, newHub, packageId, dispatcher, userName)


main()