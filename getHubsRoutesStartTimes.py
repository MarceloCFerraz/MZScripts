import csv
import datetime
import time
import requests
from utils import hubs, utils
import concurrent.futures


FULL_RESPONSE = []


def main(env, orgId, hubId):
    """
    Fills data for a specific hub.

    This function retrieves the hub configuration using the provided environment, organization ID, and hub ID. It then iterates over the route start times of the hub and creates a payload containing the hub name, route name, and start time. The payloads are appended to the FULL_RESPONSE list.

    Parameters:
    - env (str): The environment in which the hub data is stored.
    - orgId (str): The organization ID associated with the hub.
    - hubId (str): The ID of the hub.

    Returns:
    - None
    """
    hubConfig = hubs.get_hub_config(env, orgId, hubId)

    hubName = f"'{hubConfig.get('hubName')} - {hubConfig.get('hubDescription')}'"
    hubRoutes = hubConfig.get('routeStartTimes')
    print(f"Filling data for {hubName}")

    for route in hubRoutes:
        routeName = route.get('jurisdiction')
        startTime = str(route.get('routeStartTime'))#.replace(":", "_")
        

        payload = {
            "HUB": hubName,
            "ROUTE": routeName,
            "START_TIME": startTime
        }

        FULL_RESPONSE.append(payload)
    
    print(f"{hubName} Done")


def save_csv_file(fileName, data):
    """
    Saves data to a CSV file.

    This function saves the provided data to a CSV file with the given file name. If the data is empty, a message stating that there is nothing to save is printed. Otherwise, the data is written row by row to the CSV file. If the file name contains the word "Fail", an additional column with the error information is included in each row.

    Parameters:
    - fileName (str): The name of the CSV file to be saved.
    - data (list): The data to be saved in the CSV file.

    Returns:
    - None
    """
    start = time.time_ns()

    if len(data) < 1:
        print(f"Nothing to save on '{fileName}'")
    else:
        with open(fileName, 'w', newline='') as file:
            writer = csv.writer(file)
            headers = data[0].keys()
            writer.writerow(headers)
            
            for payload in data:
                row = []

                for header in headers:
                    row.append(payload.get(header))

                if "Fail" in fileName:
                    row.append(payload.get("ERROR"))
                writer.writerow(row)
                
        finish = time.time_ns()
        elapsed_time = utils.calculate_elapsed_time(start, finish)
        
        print("File '{}' saved successfully".format(fileName))
        print(f"Took {elapsed_time.get('hours')}h, {elapsed_time.get('minutes')}m and {elapsed_time.get('seconds')}s to complete")
        

if __name__ == "__main__":
    hubIds = [
        "eb655219-1b63-4d2b-9512-8c657a1a15bb",
        "12ddf9e7-714b-49a8-b5ae-f87fd3dc95f1",
        "7cc40d78-fa10-40ce-a3dc-1eaf65571a8c",
        "ac94edd8-596f-491d-a9c3-cf1c4d2798aa",
        "21fb134f-6be9-4d88-b663-0a24c632c8a5",
        "b70f145a-db3b-41de-ac5e-f928c8409a81",
        "de6877be-0eb5-4aa3-8347-7b215c50c2a9",
        "eb655219-1b63-4d2b-9512-8c657a1a15bb",
        "e8fe91b4-c1f9-4226-ba1f-06d391412b5e",
        "1d8ea5bb-c24e-4975-b1b3-02af3eed9bd0",
        "e7eb1066-775d-42db-85dc-ee4bfb6850cb",
        "21170ef3-7411-4b16-8f03-0928c81e9bcc",
        "1dad11fc-9a04-4a72-9a3d-00c9da3687d6",
        "570c99cb-c2db-4b9c-a16c-82dba379dd87",
        "b151a449-df0c-43ea-a21a-0fd94ae06eff",
        "c2d6c0c0-1d11-4ed9-9602-7685f210f130",
        "7a4a33fb-4cd8-43d2-b1fd-e350fd682cab",
        "5f4ffbd3-07bb-44e3-a38a-9aa59617c5f3",
        "6bb367c1-6d7e-44d2-bd65-156fd1a4422c",
        "dc120fa7-9b50-4a83-a858-b304f22c18ff",
        "bb64ea6b-3586-42f7-8a88-3ac98af1f7d3",
        "4232232c-7b19-4986-a416-d7cbc2fba5a3",
        "d3842ba8-52b3-4e92-8f62-4ef577444b51",
        "8e0c8e35-2e2b-4952-9bf3-479d317b02d6",
        "2b2606ad-b577-4808-a4a8-483615cfef01",
        "5fc1ec62-3a36-4c83-9847-03e10702cc06",
        "bf4527db-5b94-4459-a70d-1051cc74f616",
        "d4d486c8-58f4-4c3f-bc7e-dca419e7d6e2",
        "c1d45b5d-0e28-4ee6-80d1-8dee81fc9ff7",
        "112fa614-74d2-4c78-b99a-bc7dc7a72d40",
        "38b9ff36-d989-4a68-af39-f2cabb403009",
        "a82ae2f5-6e25-4087-93f1-bbd2b1f9af27",
        "ecdaacab-e20f-4fc2-a883-bff5ce60ecf6",
        "7304176b-a1fb-4ee0-a225-ce210882cb61",
        "80eadfe0-c96b-4720-98f3-7cd05f14a958",
        "271c01db-285b-412f-8147-71312c810d88",
        "1280d1c6-48a1-4cc4-836e-4dcf896b353b",
        "fd8f68fc-bebc-4e63-a8db-5607ecb415b8",
        "ee6eece7-cfa4-43b0-ac0e-a6f0ae554a10",
        "01cac4c0-22b6-4e3f-8ded-ec447fff0c1c",
        "4677fe3a-ce03-4c44-a709-2ee11a185150",
        "fec4b21b-779d-4735-9e25-9f41e25fac77",
        "8560d13d-75b0-48c8-8648-af6b5fc49b46",
        "be38a704-4a40-49d7-9076-78781a3f38b8",
        "1d3824e4-a032-4b6c-961c-369c223458ba",
        "dfce909e-ae67-4674-8007-7763cf4ab318",
        "84582d35-bd68-411d-8196-cef055c7000d",
        "47d68c80-e797-49bf-b898-b0d3f9cb3027",
        "03f2101e-d51a-40a7-8139-c4b60122f192",
        "a516dcd4-e769-4df6-9de8-53ec65d22f78",
        "80c0b005-f17a-4cca-a94f-55631f36de91",
        "8768365a-d3bc-41d8-a94d-30027ae574cc",
        "9f380bce-ee3b-4f6f-9f6b-b27431369a78",
        "a7386ed5-0537-45a1-8ef2-2b25277ea734",
        "0658bb49-055e-48a4-bd84-2355d26d35c5",
        "1aed9c35-c364-42f1-aa2d-fad7ea603189",
        "b39040fa-262f-42e9-8894-9b20b37481be",
        "8e263186-f9c6-491f-b517-c4c998c665d8",
        "029d9e7b-c150-435d-b7ba-8e3d279b9621",
        "bbda7f09-0d20-4c14-9a02-f1e1b89c2a52",
        "7748a4c5-0704-420f-ad9a-7c225a0451cc",
        "f09cb270-758f-470c-8b2a-2995484cbc0b"
    ]
    
    env = utils.select_env()
    orgId = utils.select_org(env)

    with concurrent.futures.ThreadPoolExecutor() as pool:
        for hubId in hubIds:
            pool.submit(main, env, orgId, hubId)

    pool.shutdown(wait=True)

    now = str(
        datetime.datetime.now().replace(microsecond=0)
    ).replace(':', '_').replace('/', '-')

    save_csv_file(f"Hubs Start Times {now}.csv", FULL_RESPONSE)
