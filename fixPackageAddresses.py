import concurrent.futures
import pandas
import json
import requests

switchboard_get_url_template = "http://switchboard.{0}.milezero.com/switchboard-war/api/package?keyType={1}&keyValue={2}&orgId={3}"

lockbox_get_url_template = "https://lockbox.{0}.milezero.com/lockbox-war/api/location/{1}"
geocoder_get_url_template = "http://geocoder.{0}.milezero.com/gc/api/address?street={1}&city={2}&state={3}&zip={4}&cc=US&provider=GOOGLE"
lockbox_update_url_template = "https://lockbox.{0}.milezero.com/lockbox-war/api/location/{1}"

alamo_get_url_template = "http://alamo.{0}.milezero.com/alamo-war/api/plannedroutes?orgId={1}&facilityId={2}&startTime={3}&endTime={4}"

ORGS = {
    "PROD": {
        "CLM": "8a9e84be-9874-4346-baab-26053d35871e",
        "STAPLES": "3c897e84-3957-4958-b54d-d02c01b14f15",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "ca3ffc06-b583-409f-a249-bdd014e21e31",
        "M3": "e9b34629-061d-4e24-93b1-717c00e2f116",
        "CFM": "8a9e84be-9874-4346-baab-26053d35871e",
        # "WALT'S": "ce8766a5-1d0f-4146-8a7c-98c0879cef10",  # Sandbox
        # "CUB": "6591e63e-6065-442d-87c3-20a5cd98cdba",  # not a client anymore
        "CUBPHARMA": "706660ca-71f6-4c01-a9ff-3a480acebaf4",
        "SHOPRITE-MM": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        "SHOPRITE": "3f7539c3-ebbb-4d97-ac9f-bc66862c6ab8",
        # "EMPIRE": "de03ba9f-7baa-4f64-9628-5eb75b970af1",  # Sandbox
        "ESSENDANT": "3d765297-0e0e-4178-843b-0ebdac333c7a",
        # "DELIVERY SOLUTIONS": "1bced832-4e3b-4f21-b803-477869cf02af", # Sandbox
        "LOWES": "8c381810-baf7-4ebe-a5f2-13c28b1ec7a4",
    },
    "STAGE": {
        "STAPLES": "3e59b207-cea5-4b00-8035-eed1ae26e566",
        "HN": "c88987f9-91e8-4561-9f07-df795ef9b8f0",
        "EDG": "4a00ea0a-ebe2-4a77-8631-800e0daa50c5",
        "M3": "28d04fba-012b-46ee-ab9a-d2909672e70e",
        "CFM": "76c23687-43c4-4fe3-b5f0-4cdd386e7895",
        "WALT'S": "f7c63075-2eb4-4056-9fe7-f403278f253b",
        # "CUB": "12d035f7-16c7-4c02-9b38-f1212b6f92f3",  # not a client anymore
        "CUBPHARMA": "6591e63e-6065-442d-87c3-20a5cd98cdba",
        "SHOPRITE-MM": "46474980-b149-4779-b9b5-76ea3d7baa90",
        "SHOPRITE": "397190aa-18ab-4bef-a8aa-d5875d738911",
        "EMPIRE": "09de776e-10cc-437d-9abc-ee5103d3b974",
        "ESSENDANT": "af0db6df-c6fd-4ad3-919c-350501c25bae",
        "DELIVERY SOLUTIONS": "cc2a4805-5b7e-49e1-80a1-a62cf906214d" #,
        # "LOWES": "",  # doesn't have a stage org so far
    }
}
CORRECTED_ADDRESSES = []


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


def search_hub_by_name(env, orgId, hubName):
    url = f"http://cromag.{env}.milezero.com/retail/api/hubs/org/{orgId}?hubType=HUB&keyType=name&key={hubName}"

    response = requests.get(url=url, timeout=5).json()["hubs"]
    # print(response)

    return response


def get_alamo_packages(domain, org_id, location_id, start_date, end_date):
    alamo_get_url = alamo_get_url_template.format(domain, org_id, location_id, start_date, end_date)
    response = requests.get(url=alamo_get_url,
                            headers={'Accept': 'application/json'})
    package_id = []
    for order in response.json():
        for pid in order.get('packageConstraints'):
            if len(pid) != 0:
                package_id.append(pid.get('packageId'))

    return package_id

def get_switchboard_package_location(domain, key_type, key_value, org_id):
    switchboard_get_url = switchboard_get_url_template.format(domain, key_type, key_value, org_id)
    response = requests.get(url=switchboard_get_url,
                            headers={'Accept': 'application/json'})
    location_id = ''
    for package_record in response.json().get('packageRecords'):
        location_id = package_record.get('orderDetails').get('customerLocationId')

    return location_id


def update_address(domain, location_id, payload):
    headers = {'content-type': 'application/json'}
    lockbox_update_url = lockbox_update_url_template.format(domain, location_id)
    response = requests.put(
        url=lockbox_update_url,
        data=json.dumps(payload), 
        headers=headers
    )

    return response


def get_address(domain, street, city, state, zip):
    geocoder_get_url = geocoder_get_url_template.format(domain, street, city, state, zip)
    response = requests.get(url=geocoder_get_url,
                            headers={'Accept': 'application/json'})
    address = response.json()
    return address


def get_location(domain, location_id, package_id):
    lockbox_get_url = lockbox_get_url_template.format(domain, location_id)
    response = requests.get(url=lockbox_get_url,
                            headers={'Accept': 'application/json'})
    location = response.json()
    try:

        precision = location.get('precision').get('precision')
        if precision == 'LOW':

            typed_address = location.get('typedAddress')
            address1 = typed_address.get('address1')
            address2 = typed_address.get('address2')
            city = typed_address.get('city')
            state = typed_address.get('state')
            zip = typed_address.get('postalCode')
            updated_address = get_address(domain, address1, city, state, zip)
            if updated_address.get('geocodeQuality') == 'LOW':
                updated_address = get_address('prod', address2, city, state, zip)
                print("package ID: " + package_id + "location id: " + location_id + " swapped adress line")
                payload = {
                    "name": location.get('name'),
                    "geo": {
                        "latitude": updated_address.get('lat'),
                        "longitude": updated_address.get('lon')
                    },
                    "typedAddress": {
                        "addressType": typed_address.get('addressType'),
                        "countryCode": typed_address.get('countryCode'),
                        "name": typed_address.get('name'),
                        "address1": address2,
                        "address2": address1,
                        "city": city,
                        "state": state,
                        "briefPostalCode": typed_address.get('briefPostalCode'),
                        "postalCode": zip
                    },
                    "timezone": updated_address.get('timeZone'),
                    "commercialType": location.get('commercialType'),
                    "attributes": [
                    ],
                    "precision": {
                        "precision": updated_address.get('geocodeQuality'),
                        "source": updated_address.get('provider'),
                    },
                    "executionScannableIds": {},
                    "executionProperties": {}
                }
            else:
                payload = {
                    "name": location.get('name'),
                    "geo": {
                        "latitude": updated_address.get('lat'),
                        "longitude": updated_address.get('lon')
                    },
                    "typedAddress": {
                        "addressType": typed_address.get('addressType'),
                        "countryCode": typed_address.get('countryCode'),
                        "name": typed_address.get('name'),
                        "address1": address1,
                        "address2": typed_address.get('address2'),
                        "city": city,
                        "state": state,
                        "briefPostalCode": typed_address.get('briefPostalCode'),
                        "postalCode": zip
                    },
                    "timezone": updated_address.get('timeZone'),
                    "commercialType": location.get('commercialType'),
                    "attributes": [
                    ],
                    "precision": {
                        "precision": updated_address.get('geocodeQuality'),
                        "source": updated_address.get('provider'),
                    },
                    "executionScannableIds": {},
                    "executionProperties": {}
                }

            response = update_address(domain, location_id, payload)

            payload["id"] = location_id

            print("Updating " + location_id + "  (" + package_id + ")")
            print("{0} - {1}: {2}".format(response.status_code, response.reason, response.text))
            if response.status_code < 400:
                CORRECTED_ADDRESSES.append(payload)

    except AttributeError as e:
        print(e + " - loc - " + location_id)


def main(env, org_id, hubName):
    hub_location_id = search_hub_by_name(env, org_id, hubName)[0]['location']['locationId']

    print("Checking for packages in {}".format(hubName))

    package_ids = get_alamo_packages(
        env, 
        org_id, 
        hub_location_id,
        '2023-08-30T08:00:00.000Z', 
        '2023-08-31T08:00:00.000Z'
    )

    print("Found {} packages for hub {}".format(len(package_ids), hubName))

    for p in package_ids:
        location_id = get_switchboard_package_location(env, 'pi', p, org_id)
        get_location(env, location_id, p)

    print("==== Finished {} ====".format(hubName))

if __name__ == '__main__':

    pending_hubs = [
        3886,8743,3716,8211,8377,3937,3926,8027,3941,3327,3034
    ]

    env = select_env()
    org_id = select_org(env)

    with concurrent.futures.ThreadPoolExecutor() as pool:
        for hub in pending_hubs:
            pool.submit(main, env, org_id, hub)

    pool.shutdown(wait=True)

    print("Finished checking and updating addresses")
    print("Savind Updated Addresses to .xlsx file")

    df = pandas.DataFrame()
    df["Name"] = []
    df["Location ID"] = []
    df["Address"] = []
    df["City"] = []
    df["State"] = []
    df["Zip Code"] = []
    df["Geo Codes"] = []
    df["Precision"] = []

    for addr in CORRECTED_ADDRESSES:
        df.loc[len(df)] = {
            "Name": addr.get("name"),
            "Location ID": addr.get("id"),
            "Address": "{}, {}".format(addr.get("typedAddress").get("address1"), addr.get("typedAddress").get("address2")),
            "City": addr.get("typedAddress").get("city"),
            "State": addr.get("typedAddress").get("state"),
            "Zip Code": addr.get("typedAddress").get("postalCode"),
            "Geo Codes": "{}, {}".format(addr.get("geo").get("latitude"), addr.get("geo").get("longitude")),
            "Precision": addr.get("precision").get("precision")
        }

    df.to_excel("Locations Updated.xlsx", index=False)
