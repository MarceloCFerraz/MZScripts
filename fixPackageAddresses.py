import concurrent.futures
import datetime
import pandas
import json
import requests

switchboard_get_url_template = "http://switchboard.{0}.milezero.com/switchboard-war/api/package?keyType={1}&keyValue={2}&orgId={3}"

lockbox_get_url_template = "https://lockbox.{0}.milezero.com/lockbox-war/api/location/{1}"
geocoder_get_url_template = "http://geocoder.{0}.milezero.com/gc/api/address?street={1}&city={2}&state={3}&zip={4}&cc=US{5}"
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
    response = requests.get(
        url=alamo_get_url,
        headers={'Accept': 'application/json'}
    )
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


def get_address(domain, street, city, state, zip, provider=None):
    if provider:
        provider = "&provider={}".format(provider)
    else:
        provider = "&provider=GOOGLE".format(provider)

    geocoder_get_url = geocoder_get_url_template.format(domain, street, city, state, zip, provider)
    
    response = requests.get(
        url=geocoder_get_url,
        headers={'Accept': 'application/json'}
    )

    address = response.json()

    # print(json.dumps(address))

    return address


def get_location(domain, location_id, package_id, hub):
    lockbox_get_url = lockbox_get_url_template.format(domain, location_id)
    
    response = requests.get(
        url=lockbox_get_url,
        headers={'Accept': 'application/json'}
    )

    location = response.json()

    try:
        precision = location.get('precision').get('precision')
        
        if precision != 'EXACT' or precision != 'HIGH':
            typed_address = location.get('typedAddress')
            address1 = typed_address.get('address1')
            address2 = typed_address.get('address2')
            city = typed_address.get('city')
            state = typed_address.get('state')
            zip = typed_address.get('postalCode')

            updated_address = get_address(domain, address1, city, state, zip)

            if updated_address.get('geocodeQuality') == 'LOW':
                updated_address = get_address(domain, address2, city, state, zip)

                address1 = typed_address.get('address2')
                address2 = typed_address.get('address1')

                if updated_address.get('geocodeQuality') == 'LOW':
                    address1 = typed_address.get('address1')
                    address2 = typed_address.get('address2')

                    updated_address = get_address(domain, address1, city, state, zip, "SMARTY")

                    if updated_address.get('geocodeQuality') == 'LOW':
                        updated_address = get_address(domain, address2, city, state, zip, "SMARTY")

                        address1 = typed_address.get('address2')
                        address2 = typed_address.get('address1')

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
                    "address2": address2,
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
            payload["hub"] = hub

            print("      Updating " + location_id + "  (" + package_id + ")")
            print("      {} - {}, {}: {}".format(location_id, response.status_code, response.reason, response.text))

            if response.status_code < 400:
                CORRECTED_ADDRESSES.append(payload)
        # else:
            # print("      Skipping {}".format(location_id))

    except AttributeError as e:
        print("***** " + e + " - loc - " + location_id)


def main(env, org_id, package_id, hub):
    print("==== New thread created for {}".format(package_id))
    
    location_id = get_switchboard_package_location(env, 'pi', package_id, org_id)

    get_location(env, location_id, package_id, hub)

    print("==== Finished {}".format(package_id))


if __name__ == '__main__':
    env = select_env()
    org_id = select_org(env)

    starting_time = str(
        datetime.datetime.now().time().replace(microsecond=0)
    ).replace(':', '_')

    pending_hubs = [
        3453,
        8500,
        8488,
        8792,
        8764,
        3926,
        3034,
        8202,
        3845,
        3808,
        8285,
        8194,
        8883,
        8613,
        3882,
        3880,
        8773,
        3716,
        8743,
        8506,
        8220,
        3964,
        8457,
        8228,
        8606,
        8103,
        3933,
        3738,
        3094,
        8027,
        3886,
        3895,
        8409,
        3998,
        8037,
        8102,
        8740,
        8406,
        8845,
        8203,
        98471,
        3322,
        3012,
        8221,
        8605,
        3920,
        8033,
        3946,
        3099,
        8006,
        8247,
        8069,
        8351,
        8232,
        8204,
        3905,
        3921,
        8087,
        8971,
        8428,
        8246,
        3748,
        8391,
        925,
        8081,
        8463,
        8423,
        8826,
        8073,
        3007,
        8190,
        8653,
        8209,
        3090,
        8253,
        3772,
        3471,
        3375,
        8053,
        3881,
        8673,
        3741,
        8050,
        8436,
        3480,
        8101,
        8627,
        8974,
        8281,
        8600,
        8028,
        98078,
        8175,
        8847,
        3941,
        8801,
        8077,
        7585,
        8005,
        8492,
        8211,
        3909,
        8885,
        8377,
        8034,
        8286,
        8109,
        3903,
        8471,
        8026,
        3913,
        8155,
        8571,
        8568,
        8857,
        8744
    ]

    package_date = datetime.datetime.strptime(
        input("Input the date (yyyy-mm-dd): "), 
        "%Y-%m-%d"
    )
    next_day = package_date + datetime.timedelta(1)

    package_date = package_date.strftime("%Y-%m-%d")
    next_day = next_day.strftime("%Y-%m-%d")

    # print("Searching packages from {} to {}".format(package_date, next_day))

    with concurrent.futures.ThreadPoolExecutor() as pool:
        for hub in pending_hubs:
            hub_location_id = search_hub_by_name(env, org_id, hub)[0]['location']['locationId']
            print("Checking for packages in {}".format(hub))

            package_ids = get_alamo_packages(
                env, 
                org_id, 
                hub_location_id,
                '{}T08:00:00.000Z'.format(package_date), 
                '{}T08:00:00.000Z'.format(next_day)
            )

            print("Found {} packages for hub {}".format(len(package_ids), hub))

            for p in package_ids:
                pool.submit(main, env, org_id, p, hub)

            print("==== Finished {} ====".format(hub))

    pool.shutdown(wait=True)

    print("Finished checking all hubs")
    print("Updated {} addresses!".format(len(CORRECTED_ADDRESSES)))
    print()
    print("Savind Updated Addresses to report file")

    df = pandas.DataFrame()
    df["HUB"] = []
    df["Name"] = []
    df["Location ID"] = []
    df["Address"] = []
    df["City"] = []
    df["State"] = []
    df["Zip Code"] = []
    df["Geo Codes"] = []
    df["Provider"] = []
    df["Precision"] = []

    for addr in CORRECTED_ADDRESSES:
        df.loc[len(df)] = {
            "HUB": addr.get("hub"),
            "Name": addr.get("name"),
            "Location ID": addr.get("id"),
            "Address": "'{}, {}'".format(addr.get("typedAddress").get("address1"), addr.get("typedAddress").get("address2")),
            "City": addr.get("typedAddress").get("city"),
            "State": addr.get("typedAddress").get("state"),
            "Zip Code": addr.get("typedAddress").get("postalCode"),
            "Geo Codes": "'{}, {}'".format(addr.get("geo").get("latitude"), addr.get("geo").get("longitude")),
            "Provider": addr.get("precision").get("source"),
            "Precision": addr.get("precision").get("precision")
        }

    df.to_csv("Locations {}.csv".format(starting_time), index=False)
