import requests
from utils import utils, associates


def get_associate_auth_perms(env, orgId, associateAuthPermsArray):
    """
    Retrieves the permission labels associated with the given associate's authorization permissions.

    This function takes the environment, organization ID, and an array of associate authorization permissions as input. It sends a request to the specified URL to retrieve the organization's authorization permissions. The function then compares each associate permission with the organization permissions and appends the corresponding permission label to the response array.

    Parameters:
    - env (str): The environment.
    - orgId (str): The organization ID.
    - associateAuthPermsArray (list): An array of associate authorization permissions.

    Returns:
    - response (list): An array of permission labels associated with the given associate's authorization permissions.
    """
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
    """
    Retrieves and displays the permissions associated with an associate.

    This function prompts the user to select the environment and organization ID. It then prompts the user to enter the associate ID. The function retrieves the associate data using the provided environment, organization ID, and associate ID. If the associate data is not None, the function calls the `get_associate_auth_perms()` function to retrieve the permission labels associated with the associate's authorization permissions. The function then prints the associate ID followed by the permissions.

    Parameters:
    - None

    Returns:
    - None
    """
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
