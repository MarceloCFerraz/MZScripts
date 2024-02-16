import concurrent.futures
import datetime
import json

import pandas
import requests

gazetteer_get_url_template = (
    "https://gazetteer.{0}.milezero.com/gazetteer-war/api/location/matching/org/{1}"
)
lockbox_get_url_template = (
    "https://lockbox.{0}.milezero.com/lockbox-war/api/location/{1}"
)
geocoder_get_url_template = "http://geocoder.{0}.milezero.com/gc/api/address?street={1}&city={2}&state={3}&zip_code={4}&cc=US{5}"
lockbox_update_url_template = (
    "https://lockbox.{0}.milezero.com/lockbox-war/api/location/{1}"
)
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
        "DELIVERY SOLUTIONS": "cc2a4805-5b7e-49e1-80a1-a62cf906214d",  # ,
        # "LOWES": "",  # doesn't have a stage org so far
    },
}
CORRECTED_ADDRESSES = []


def print_array_items(array):
    divisor = 4
    items_per_line = divisor

    for i, item in enumerate(array):
        print(f"{item:^{20}}", end="")
        if (i + 1) % items_per_line == 0:
            print()
    print()


def convert_env(env):
    if env == "INTEG":
        env = "PROD"

    return env.lower()


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
    return ORGS[env][org]  # returns orgId


def get_all_hubs(env, orgId):
    endpoint = (
        f"http://cromag.{convert_env(env)}.milezero.com/retail/api/hubs/org/{orgId}"
    )

    return requests.get(url=endpoint, timeout=10).json()["hubs"]


def update_address(env, location_id, payload):
    headers = {"content-type": "application/json"}

    lockbox_update_url = lockbox_update_url_template.format(env, location_id)

    response = requests.put(
        url=lockbox_update_url, data=json.dumps(payload), headers=headers
    )

    return response


def get_address(domain, street, city, state, zip, provider=None):
    if provider:
        provider = "&provider={}".format(provider)
    else:
        provider = "&provider=GOOGLE".format()

    geocoder_get_url = geocoder_get_url_template.format(
        domain, street, city, state, zip, provider
    )

    response = requests.get(
        url=geocoder_get_url, headers={"Accept": "application/json"}
    )

    address = response.json()

    # print(json.dumps(address))

    return address


def get_location(domain, location_id):
    """
    Retrieves and updates location information based on the provided parameters.

    Args:
    - domain (str): The domain.
    - location_id (str): The location ID.
    - package_id (str): The package ID.
    - hub (str): The hub information.

    Returns:
    - None

    This function retrieves the location information for a specific location from Lockbox using the given domain, location ID, and package ID. It then updates the address if necessary by calling the `get_address` function. Finally, it prints the status of the update operation and appends the updated location information to the `CORRECTED_ADDRESSES` list if the update was successful.
    """
    lockbox_get_url = lockbox_get_url_template.format(domain, location_id)

    response = requests.get(url=lockbox_get_url, headers={"Accept": "application/json"})

    location = response.json()

    try:
        precision = location.get("precision").get("precision")

        if precision != "EXACT" or precision != "HIGH":
            typed_address = location.get("typedAddress")
            address1 = typed_address.get("address1")
            address2 = typed_address.get("address2")
            city = typed_address.get("city")
            state = typed_address.get("state")
            zip = typed_address.get("postalCode")

            updated_address = get_address(domain, address1, city, state, zip)

            if updated_address.get("geocodeQuality") == "LOW":
                updated_address = get_address(domain, address2, city, state, zip)

                address1 = typed_address.get("address2")
                address2 = typed_address.get("address1")

                if updated_address.get("geocodeQuality") == "LOW":
                    address1 = typed_address.get("address1")
                    address2 = typed_address.get("address2")

                    updated_address = get_address(
                        domain, address1, city, state, zip, "SMARTY"
                    )

                    if updated_address.get("geocodeQuality") == "LOW":
                        updated_address = get_address(
                            domain, address2, city, state, zip, "SMARTY"
                        )

                        address1 = typed_address.get("address2")
                        address2 = typed_address.get("address1")

            payload = {
                "name": location.get("name"),
                "geo": {
                    "latitude": updated_address.get("lat"),
                    "longitude": updated_address.get("lon"),
                },
                "typedAddress": {
                    "addressType": typed_address.get("addressType"),
                    "countryCode": typed_address.get("countryCode"),
                    "name": typed_address.get("name"),
                    "address1": address1,
                    "address2": address2,
                    "city": city,
                    "state": state,
                    "briefPostalCode": typed_address.get("briefPostalCode"),
                    "postalCode": zip,
                },
                "timezone": updated_address.get("timeZone"),
                "commercialType": location.get("commercialType"),
                "attributes": [],
                "precision": {
                    "precision": updated_address.get("geocodeQuality"),
                    "source": updated_address.get("provider"),
                },
                "executionScannableIds": {},
                "executionProperties": {},
            }

            response = update_address(domain, location_id, payload)

            payload["id"] = location_id
            payload["hub"] = hub

            print("      Updating " + location_id)
            print(
                "      {} - {}, {}: {}".format(
                    location_id, response.status_code, response.reason, response.text
                )
            )

            if response.status_code < 400:
                CORRECTED_ADDRESSES.append(payload)
        # else:
        # print("      Skipping {}".format(location_id))

    except AttributeError:
        print("#### {e} - loc - {location_id}")


def get_gazeteer_location_id(env, org_id, index, hubName):
    """
    Retrieves location IDs from the gazetteer based on the provided parameters.

    Args:
    - env (str): The environment.
    - org_id (str): The organization ID.
    - index (int): The index for pagination.
    - hub_name (str): The hub name.

    Returns:
    - response (object): The response object containing the retrieved location IDs.
    """
    print(hubName, " - index: ", index)

    headers = {"content-type": "application/json"}

    gazetteer_get_url = gazetteer_get_url_template.format(env, org_id)

    payload = {
        "hubName": f"{hubName}",
        "queryMode": "MATCH_ALL_IN_ORDER",
        "pagination": {"from": index, "size": 500},
    }

    response = requests.post(
        url=gazetteer_get_url, data=json.dumps(payload), headers=headers
    )

    with concurrent.futures.ThreadPoolExecutor() as pool:
        for location in response.json().get("locations"):
            pool.submit(get_location, env, location)

    pool.shutdown(wait=True)

    return response


def main(env, orgId, hubName):
    """
    Orchestrates the retrieval and updating of location information.

    Args:
    - env (str): The environment.
    - org_id (str): The organization ID.
    - hub_name (str): The hub name.

    Returns:
    - None
    """

    for index in range(0, 10000, 500):
        print("==== Index: {}".format(index))

        get_gazeteer_location_id(env, orgId, index, hubName)

    print("==== Finished {}".format(hubName))


if __name__ == "__main__":
    env = select_env()
    orgId = select_org(env)

    starting_time = str(datetime.datetime.now().time().replace(microsecond=0)).replace(
        ":", "_"
    )

    # allOrgHubs = get_all_hubs(env, orgId)
    allOrgHubs = [
        8500  # 8506, 3886,8743,3716,8211,8377,3937,3926,8027,3941,3327,3034
    ]

    for hub in allOrgHubs:
        # uncomment this line below if you got all hubs from API
        # hubName = hub['name']

        hubName = hub

        print("==== Starting {}".format(hubName))

        main(env, orgId, hubName)

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
            "Address": "'{}, {}'".format(
                addr.get("typedAddress").get("address1"),
                addr.get("typedAddress").get("address2"),
            ),
            "City": addr.get("typedAddress").get("city"),
            "State": addr.get("typedAddress").get("state"),
            "Zip Code": addr.get("typedAddress").get("postalCode"),
            "Geo Codes": "'{}, {}'".format(
                addr.get("geo").get("latitude"), addr.get("geo").get("longitude")
            ),
            "Provider": addr.get("precision").get("source"),
            "Precision": addr.get("precision").get("precision"),
        }

    df.to_csv("Locations {}.csv".format(starting_time), index=False)
