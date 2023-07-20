from utils import packages, files, utils

env = utils.select_env()
orgId = utils.select_org(env)

# fileName = input("Type in file name containing the package ids?\n> ").strip()

packageIds = files.getDataLines("pids")
packages.bulk_cancel_packages(env, orgId, packageIds)
