package main

import (
	"fmt"
	"os"
	"time"

	"github.com/MarceloCFerraz/MZScripts/utils"
)

func main() {
	// var json fastjson.Parser // or ParserPool
	util := utils.Initialize()

	env := util.SelectEnv()
	orgId := util.SelectOrg(&env)

	startTime := time.Now().UTC()
	fmt.Println(startTime)

	var hubNames []string
	options := []string{"Update All Hubs", "Update specific Hubs"}
	// TODO: Add another option to read from .txt file

	option := utils.SelectOption(&options)
	switch option {
	case 1:
		GetHubNamesFromUser(&env, &orgId, &hubNames)
		break
	default:
		err := utils.GetAllHubNames(&env, &orgId, &hubNames)
		if err != nil {
			fmt.Println("An error occurred when fetching for Hub Names:", err)
			os.Exit(1)
		}
		break
	}

	fmt.Println(hubNames)
	// allOrgHubs = [
	//     8500  # 8506, 3886,8743,3716,8211,8377,3937,3926,8027,3941,3327,3034
	// ]

	// for hub in allOrgHubs:
	//     # uncomment this line below if you got all hubs from API
	//     # hubName = hub['name']

	//     hubName = hub

	//     print("==== Starting {}".format(hubName))

	//     main(env, orgId, hubName)

	// print("Finished checking all hubs")
	// print("Updated {} addresses!".format(len(CORRECTED_ADDRESSES)))
	// print()
	// print("Savind Updated Addresses to report file")

	// df = pandas.DataFrame()
	// df["HUB"] = []
	// df["Name"] = []
	// df["Location ID"] = []
	// df["Address"] = []
	// df["City"] = []
	// df["State"] = []
	// df["Zip Code"] = []
	// df["Geo Codes"] = []
	// df["Provider"] = []
	// df["Precision"] = []

	// for addr in CORRECTED_ADDRESSES:
	//     df.loc[len(df)] = {
	//         "HUB": addr.get("hub"),
	//         "Name": addr.get("name"),
	//         "Location ID": addr.get("id"),
	//         "Address": "'{}, {}'".format(
	//             addr.get("typedAddress").get("address1"),
	//             addr.get("typedAddress").get("address2"),
	//         ),
	//         "City": addr.get("typedAddress").get("city"),
	//         "State": addr.get("typedAddress").get("state"),
	//         "Zip Code": addr.get("typedAddress").get("postalCode"),
	//         "Geo Codes": "'{}, {}'".format(
	//             addr.get("geo").get("latitude"), addr.get("geo").get("longitude")
	//         ),
	//         "Provider": addr.get("precision").get("source"),
	//         "Precision": addr.get("precision").get("precision"),
	//     }

	// df.to_csv("Locations {}.csv".format(starting_time), index=False)

	// gazetteer_get_addresses := "https://gazetteer.{env}.milezero.com/gazetteer-war/api/location/matching/org/{org_id}"
	// lockbox_get_location := "https://lockbox.{env}.milezero.com/lockbox-war/api/location/{location_id}"
	// geocoder_get_geocode := "http://geocoder.{env}.milezero.com/gc/api/address?street={1}&city={2}&state={3}&zip_code={4}&cc=US&provider={5}"
	// lockbox_update_address := "https://lockbox.{env}.milezero.com/lockbox-war/api/location/{location_id}"
	// cromag_get_hub := "http://cromag.{convert_env(env)}.milezero.com/retail/api/hubs/org/{org_id}"

	//	read all hubs
	//	iterate through hubs and read ever address from each of them
	//		correct each address (spam goroutines)
	//			get current address
	//			verify geocode quality
	//			if less than EXACT, correct generate new geo code with google
	//				generate 2 goroutines to verify precision (LOW, MEDIUM, HIGH or EXACT) for:
	//				1. addr 1 (as addr1) + addr 2 (as addr2)
	//				2. addr 2 (as addr1) + addr 1 (as addr2)
	//			highest result should be used
	// save updated addresses into csv file once all done
}

func GetHubNamesFromUser(ent *string, orgId *string, hubNames *[]string) {
	var hubName string
	fmt.Println("Type one Hub Name per line")
	for {
		fmt.Printf("Hub Names Selected So Far: %v\n", *hubNames)
		fmt.Print("> ")
		fmt.Scanln()

		if _, err := fmt.Scanf("%s", &hubName); err != nil {
			if err.Error() == "unexpected newline" && len(*hubNames) > 0 {
				fmt.Println("Returning...")
				return
			}
			fmt.Println("Type a valid option")
		} else if !utils.Contains(hubNames, &hubName) {
			*hubNames = append(*hubNames, hubName)
		}
	}
}

// def print_array_items(array):
//     divisor = 4
//     items_per_line = divisor

//     for i, item in enumerate(array):
//         print(f"{item:^{20}}", end="")
//         if (i + 1) % items_per_line == 0:
//             print()
//     print()

// def convert_env(env):
//     if env == "INTEG":
//         env = "PROD"

//     return env.lower()

// def select_env():
//     envs = ["PROD", "STAGE"]
//     env = ""
//     print("SELECT THE ENV")
//     print(f"Options: {'   '.join(envs)}")
//     while env not in envs:
//         env = str(input("> ")).upper().strip()

//     return env

// def select_org(env):
//     orgs = list(ORGS[env].keys())
//     org = ""

//     print(f"SELECT THE ORG ({env})")
//     print("Options: ")
//     print_array_items(orgs)

//     while org not in orgs:
//         org = str(input("> ")).upper().strip()
//     return ORGS[env][org]  # returns orgId

// def get_all_hubs(env, orgId):
//     endpoint = (
//         f"http://cromag.{convert_env(env)}.milezero.com/retail/api/hubs/org/{orgId}"
//     )

//     return requests.get(url=endpoint, timeout=10).json()["hubs"]

// def update_address(env, location_id, payload):
//     headers = {"content-type": "application/json"}

//     lockbox_update_url = lockbox_update_url_template.format(env, location_id)

//     response = requests.put(
//         url=lockbox_update_url, data=json.dumps(payload), headers=headers
//     )

//     return response

// def get_address(domain, street, city, state, zip, provider=None):
//     if provider:
//         provider = "&provider={}".format(provider)
//     else:
//         provider = "&provider=GOOGLE".format()

//     geocoder_get_url = geocoder_get_url_template.format(
//         domain, street, city, state, zip, provider
//     )

//     response = requests.get(
//         url=geocoder_get_url, headers={"Accept": "application/json"}
//     )

//     address = response.json()

//     # print(json.dumps(address))

//     return address

// def get_location(domain, location_id):
//     """
//     Retrieves and updates location information based on the provided parameters.

//     Args:
//     - domain (str): The domain.
//     - location_id (str): The location ID.
//     - package_id (str): The package ID.
//     - hub (str): The hub information.

//     Returns:
//     - None

//     This function retrieves the location information for a specific location from Lockbox using the given domain, location ID, and package ID. It then updates the address if necessary by calling the `get_address` function. Finally, it prints the status of the update operation and appends the updated location information to the `CORRECTED_ADDRESSES` list if the update was successful.
//     """
//     lockbox_get_url = lockbox_get_url_template.format(domain, location_id)

//     response = requests.get(url=lockbox_get_url, headers={"Accept": "application/json"})

//     location = response.json()

//     try:
//         precision = location.get("precision").get("precision")

//         if precision != "EXACT" or precision != "HIGH":
//             typed_address = location.get("typedAddress")
//             address1 = typed_address.get("address1")
//             address2 = typed_address.get("address2")
//             city = typed_address.get("city")
//             state = typed_address.get("state")
//             zip = typed_address.get("postalCode")

//             updated_address = get_address(domain, address1, city, state, zip)

//             if updated_address.get("geocodeQuality") == "LOW":
//                 updated_address = get_address(domain, address2, city, state, zip)

//                 address1 = typed_address.get("address2")
//                 address2 = typed_address.get("address1")

//                 if updated_address.get("geocodeQuality") == "LOW":
//                     address1 = typed_address.get("address1")
//                     address2 = typed_address.get("address2")

//                     updated_address = get_address(
//                         domain, address1, city, state, zip, "SMARTY"
//                     )

//                     if updated_address.get("geocodeQuality") == "LOW":
//                         updated_address = get_address(
//                             domain, address2, city, state, zip, "SMARTY"
//                         )

//                         address1 = typed_address.get("address2")
//                         address2 = typed_address.get("address1")

//             payload = {
//                 "name": location.get("name"),
//                 "geo": {
//                     "latitude": updated_address.get("lat"),
//                     "longitude": updated_address.get("lon"),
//                 },
//                 "typedAddress": {
//                     "addressType": typed_address.get("addressType"),
//                     "countryCode": typed_address.get("countryCode"),
//                     "name": typed_address.get("name"),
//                     "address1": address1,
//                     "address2": address2,
//                     "city": city,
//                     "state": state,
//                     "briefPostalCode": typed_address.get("briefPostalCode"),
//                     "postalCode": zip,
//                 },
//                 "timezone": updated_address.get("timeZone"),
//                 "commercialType": location.get("commercialType"),
//                 "attributes": [],
//                 "precision": {
//                     "precision": updated_address.get("geocodeQuality"),
//                     "source": updated_address.get("provider"),
//                 },
//                 "executionScannableIds": {},
//                 "executionProperties": {},
//             }

//             response = update_address(domain, location_id, payload)

//             payload["id"] = location_id
//             payload["hub"] = hub

//             print("      Updating " + location_id)
//             print(
//                 "      {} - {}, {}: {}".format(
//                     location_id, response.status_code, response.reason, response.text
//                 )
//             )

//             if response.status_code < 400:
//                 CORRECTED_ADDRESSES.append(payload)
//         # else:
//         # print("      Skipping {}".format(location_id))

//     except AttributeError:
//         print("#### {e} - loc - {location_id}")

// def get_gazeteer_location_id(env, org_id, index, hubName):
//     """
//     Retrieves location IDs from the gazetteer based on the provided parameters.

//     Args:
//     - env (str): The environment.
//     - org_id (str): The organization ID.
//     - index (int): The index for pagination.
//     - hub_name (str): The hub name.

//     Returns:
//     - response (object): The response object containing the retrieved location IDs.
//     """
//     print(hubName, " - index: ", index)

//     headers = {"content-type": "application/json"}

//     gazetteer_get_url = gazetteer_get_url_template.format(env, org_id)

//     payload = {
//         "hubName": f"{hubName}",
//         "queryMode": "MATCH_ALL_IN_ORDER",
//         "pagination": {"from": index, "size": 500},
//     }

//     response = requests.post(
//         url=gazetteer_get_url, data=json.dumps(payload), headers=headers
//     )

//     with concurrent.futures.ThreadPoolExecutor() as pool:
//         for location in response.json().get("locations"):
//             pool.submit(get_location, env, location)

//     pool.shutdown(wait=True)

//     return response

// def main(env, orgId, hubName):
//     """
//     Orchestrates the retrieval and updating of location information.

//     Args:
//     - env (str): The environment.
//     - org_id (str): The organization ID.
//     - hub_name (str): The hub name.

//     Returns:
//     - None
//     """

//     for index in range(0, 10000, 500):
//         print("==== Index: {}".format(index))

//         get_gazeteer_location_id(env, orgId, index, hubName)

//     print("==== Finished {}".format(hubName))
