import concurrent.futures
import os
import requests
from datetime import datetime

ORGS = {
    "PROD": {
        "STAPLES": "3c897e84-3957-4958-b54d-d02c01b14f15",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "ca3ffc06-b583-409f-a249-bdd014e21e31",
        "CUB": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "CUBPHARMA": "706660ca-71f6-4c01-a9ff-3a480acebaf4",
        "SHOPRITE": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        "LOWES": "8c381810-baf7-4ebe-a5f2-13c28b1ec7a4",
    },
    "STAGE": {
        "STAPLES": "3e59b207-cea5-4b00-8035-eed1ae26e566",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "4a00ea0a-ebe2-4a77-8631-800e0daa50c5",
        "CUB": "12d035f7-16c7-4c02-9b38-f1212b6f92f3",
        "CUBPHARMA": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "SHOPRITE": "397190aa-18ab-4bef-a8aa-d5875d738911",
        "CLM": "76c23687-43c4-4fe3-b5f0-4cdd386e7895",
        "LOWES": ""
    }
}


def print_array_items(array):
    divisor = 4

    for i in range(0, len(array)):
        item = array[i] + "   "
        if 0 < i < len(array) and (i + 1) % divisor == 0:
            item += "\n"
        print(f"{item}", end="")
    print()


def select_env():
    envs = ["PROD", "STAGE"]
    env = ""
    print("SELECT THE ENV")
    print(f"Options: {'   '.join(envs)}")
    while env not in envs:
        env = str(input("> ")).upper().strip()

    return env


def select_org(env):
    orgs = list(ORGS[env].keys())
    org = ""

    print(f"SELECT THE ORG ({env})")
    print("Options: ")
    print_array_items(orgs)

    while org not in orgs:
        org = str(input("> ")).upper().strip()
    return ORGS[env][org] # returns orgId


def get_unplanned_packages_from_hub(env, orgId, facilityId):
    url = f"http://alamo.{env}.milezero.com/alamo-war/api/constraints?orgId={orgId}&facilityId={facilityId}&state=UNPLANNED"

    response = requests.get(url=url, timeout=3000).json()
    
    print(f"Found {response['size']} packages")

    return response['constraints']


def bulk_cancel_packages(env, orgId, packageIds):
    # newStatus = "CANCELLED"

    API = f"https://switchboard.{env}.milezero.com/switchboard-war/api/package/cancel"
    
    requestData = {
        "orgId": orgId,
        "packageIds": packageIds,
        "associate": {
            "name": "Marcelo",
            "id": "Marcelo",
            "type": "Support"
        },
        "notes": "Requested by dispatcher"
    }
    
    try:
        response = requests.post(url=API, json=requestData, timeout=1000)
        print(
            f"> Result: ({response.status_code})\n"+
            f"{response.text if response.status_code >= 400 else ''}"
        )
    except Exception as e:
        print(f"> {packageIds} couldn't be CANCELLED. See error bellow")
        print(e)


def main():
    env = select_env()
    orgId = select_org(env)

    facility_ids = [ # hub location ids
        "bd816479-23a5-4731-8325-ec37d9a0e87f", # PHL
        "7d6f6042-81ff-46d9-b9d0-c4d61ba9f55e"  # DCA
    ]

    batches = []
    
    for facilityId in facility_ids:
        print(f"Getting UNPLANNED packages for facility {facilityId}")
        pkgs = get_unplanned_packages_from_hub(env, orgId, facilityId)
        
        batch = []

        for i in range(0, len(pkgs)):
            pkg = pkgs[i]

            if len(batch) < 100:
                batch.append(pkg['constraintId'])

                if len(pkgs) == (i + 1):
                    batches.append(batch)
            else:
                batches.append(batch)
                batch = []
        
        with concurrent.futures.ThreadPoolExecutor() as pool:
            for batch in batches:
                pool.submit(bulk_cancel_packages, env, orgId, batch)
        pool.shutdown(wait=True)


main()
