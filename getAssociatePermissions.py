import requests
from utils import utils, associates


def get_associate_auth_perms(env, orgId, associateAuthPermsArray):
    url = f"http://lmx.{env}.milezero.com/lmx-war/api/auth/{orgId}/roles"
    orgAuthPermsArray = requests.get(url=url, timeout=5).json()["permissions"]

    response = []

    for associatePerm in associateAuthPermsArray:
        for perms in orgAuthPermsArray:
            permName = perms["name"]
            if associatePerm == permName:
                permLabel = perms["label"]
                response.append(permLabel)

    return response


def main():
    env = utils.select_env()
    orgId = utils.select_org(env)

    print("TYPE THE ASSOCIATE ID")
    associateId = input("> ")

    associate = associates.get_associate_data(env=env, orgId=orgId, associateId=associateId)

    if associate is not None:
        permissions = get_associate_auth_perms(env, orgId, associate["authPerms"])
        p = "Access MileVision, "
        for permission in permissions:
            p += permission.replace("Access MileVision ", "") + ", "
        print(f"{associateId} permissions are:")
        print(p)


main()
