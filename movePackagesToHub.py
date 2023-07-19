import requests
from utils import files

def move_packages(env, orgId, newHub, packageId, dispatcher, userName):
    url = f"https://switchboard.{env}.milezero.com/switchboard-war/api/package/update/{orgId}/{packageId}/hub"
    
    payload = {
        "hubName": newHub,
        "notes": f"Requested by {dispatcher}. Executed by {userName}"
    }
    response = requests.post(url=url, json=payload, timeout=15)
    print(f"{response} {response.text if response.status_code >= 400 else ''}")


def main():
    userName = "Marcelo Ferraz"
    dispatcher = "Kosta Delevski"
    env = "prod"
    orgId = "3c897e84-3957-4958-b54d-d02c01b14f15"
    newHub = "3453"

    packageIds = files.get_data_from_file("pids")

    for packageId in packageIds:
        move_packages(env, orgId, newHub, packageId, dispatcher, userName)


main()