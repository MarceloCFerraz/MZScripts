package main

import (
	"encoding/json"
	"fmt"
	"os"
	"sync"
	"time"

	models "github.com/MarceloCFerraz/MZScripts/ApiModels"
	"github.com/MarceloCFerraz/MZScripts/utils"
)

// type Result struct {
// 	newAddress models.LBLocation
// 	oldAddress models.LBLocation
// }

func main() {
	util := utils.Initialize()

	env := util.SelectEnv()
	orgId := util.SelectOrg(&env)

	startTime := time.Now().UTC()
	fmt.Println(startTime)

	fmt.Println("Fetching all hubs...")

	allHubs, err := getAllHubs(&env, &orgId)

	if err != nil {
		fmt.Println("An error occurred when getting all hubs: ", err)
		os.Exit(1)
	}

	var hubNames []string
	// TODO: Add another option to read from .txt file
	options := []string{"Update All Hubs", "Update specific Hubs"}

	switch utils.SelectOption(&options) {
	case 1:
		getHubNamesFromUser(&hubNames, &allHubs)
	default:
		// not a pointer because this function is also used in `getHubNamesFromUser`
		hubNames = getAllHubNames(&allHubs)
	}

	// every hub can have up to 10k locations, so the most appropriate way to
	// work on all of them is to concurrently process locations instead of hubs
	// and limit the amount of addresses being checked and updated in parallel
	// limit := 500

	// updatedAddresses := make(chan Result, limit)
	// addresses := make(chan models.LBLocation, limit)
	// done := make(chan bool)

	// var matrix [][]string
	// headers := []string{
	// 	"id", "name", "hub",
	// 	"old geocode quality", "new geocode quality",
	// 	"old address line 1", "new address line 1",
	// 	"old address line 2", "new address line 2",
	// 	"old geocode provider", "new geocode provider",
	// 	"old latitude", "new latitude",
	// 	"old longitude", "new longitude",
	// }
	// var csvWriter csv.Writer

	// // a channel will be used to limit and bridge communication between goroutines
	// wg := sync.WaitGroup{}
	// // a wait group will be used to wait for all goroutines to finish before continuing

	// /* --------- THIS SHOULD BE PLACED BEFORE OR WITHIN EVERY GOROUTING --------- */
	// updatedAddresses <- address // add one item to channel before each goroutine call up to `maxGoRoutines`
	// <-updatedAddresses          // remove one item from this channel after goroutine is finished

	// wg.Add(1)       // add one to the wg before each goroutine call
	// defer wg.Done() // defer wg.Done() for each goroutine
	/* -------------------------------------------------------------------------- */
	processHubs(&env, &orgId, &hubNames)

	// for hub in allOrgHubs:
	//     # uncomment this line below if you got all hubs from API
	//     # hubName = hub['name']

	//     hubName = hub

	//     print("==== Starting {}".format(hubName))

	// for index in range(0, 10000, 500):
	//     print("==== Index: {}".format(index))
	//     get_gazeteer_location_id(env, orgId, index, hubName)
	// print("==== Finished {}".format(hubName))

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

func getAllHubs(env, orgId *string) (models.CromagGetHubs, error) {
	var allHubs models.CromagGetHubs
	temp, err := utils.GetAllHubs(env, orgId)

	if err != nil {
		fmt.Println("An error occurred when getting all hubs: ", err)
		return models.CromagGetHubs{}, err
	}

	err = json.Unmarshal(temp, &allHubs)

	if err != nil {
		fmt.Println("Error unmarshaling: ", err)
		return models.CromagGetHubs{}, err
	}

	// fmt.Println(allHubs)
	fmt.Println("Found", allHubs.Count, "Hubs")
	return allHubs, nil
}

func getHubNamesFromUser(hubNames *[]string, allHubs *models.CromagGetHubs) {
	var hubName string
	allNames := getAllHubNames(allHubs)

	fmt.Println("Type one Hub Name per line")
	for {
		fmt.Printf("Hub Names Selected So Far: %v\n", *hubNames)
		fmt.Print("> ")
		fmt.Scanln()

		if _, err := fmt.Scanf("%s", &hubName); err != nil {
			// if input is new line and hubNames have at least one item
			if err.Error() == "unexpected newline" && len(*hubNames) > 0 {
				fmt.Println("Returning...")
				return
			}
			fmt.Println("Type a valid option")
		} else if !utils.Contains(hubNames, &hubName) {
			if utils.Contains(&allNames, &hubName) {
				*hubNames = append(*hubNames, hubName)
			} else {
				fmt.Println("This option doesn't exist in this org")
			}
		}
	}
}

// Utility function to iterate through the slice of provided hubs and return only the hub names in it
func getAllHubNames(allHubs *models.CromagGetHubs) []string {
	var hubNames []string

	for _, hub := range allHubs.Hubs {
		hubNames = append(hubNames, hub.Name)
	}

	return hubNames
}

func processHubs(env, orgId *string, hubNames *[]string) {
	semaphore := make(chan bool, 500) // limits the max amount of goroutines to 500
	wg := sync.WaitGroup{}

	for _, hub := range *hubNames {
		fmt.Printf("------------------ Starting hub %s ------------------\n", hub)

		// max is 10k addresses for each hub in gazetteer
		for i := 0; i < 10_000; i = i + 500 {
			batch, err := utils.GetAddressFromGazetteer(env, orgId, hub, i)

			if err != nil {
				fmt.Println("Error fetching addresses for", hub)
				fmt.Println("Error:", err)
				break // stops fetching for addresses for this hub and starts with the next hub
			}

			var addresses models.GzMatchingLocation
			err = json.Unmarshal(batch, &addresses)

			if err != nil || addresses.Message != "" {
				fmt.Println("Error unmarshaling data or error with data")
				fmt.Println("Data:", string(batch))
				fmt.Println("Error:", err)
				continue // stops current interaction and searches the next 500 addresses for the same hub
			}

			for _, location := range addresses.Locations {
				semaphore <- true
				wg.Add(1)
				go processHubLocations(env, location.ID, &semaphore, &wg)
			}
			wg.Wait() // wait until all goroutines for this hub have finished
		}

		fmt.Printf("------------------ Finishing hub %s ------------------\n", hub)
	}

	// wg.Wait() // wait for all goroutines to finish

	// save updated addresses struct to csv file
}

func processHubLocations(env *string, locationId string, semaphore *(chan bool), wg *sync.WaitGroup) {
	defer wg.Done()
	defer func() { <-*semaphore }()

	data, err := utils.GetLocationFromLockbox(*env, locationId)

	if err != nil {
		fmt.Println(err)
		return
	}

	var location models.LBLocation

	err = json.Unmarshal(data, &location)

	if err != nil {
		fmt.Print("Error Unmarshaling location", locationId, "error:", err)
		return
	}

	if locationNeedsUpdate(location) {
		updateLocation(env, location)
	}

}

func locationNeedsUpdate(location models.LBLocation) bool {
	if location.Precision.Precision == "" || // location does not have geocode precision registered for some reason
		location.Precision.Precision == "EXACT" { // location is already perfect
		return false
	}

	return true
}

func newAddressNeedsUpdate(location models.GCLocation) bool {
	if location.GeocodeQuality == "" || // location does not have geocode precision registered for some reason
		location.GeocodeQuality == "EXACT" || // location is already perfect
		location.GeocodeQuality == "HIGH" { // geocode is good enough
		return false
	}

	return true
}

func updateLocation(env *string, location models.LBLocation) {
	typedAddr := location.TypedAddress

	// TODO: create another function to isolate repeated code
	response, err := utils.SearchAddressWithGeoCoder(
		*env,
		typedAddr.Address1,
		typedAddr.City,
		typedAddr.State,
		typedAddr.PostalCode,
		"SMARTY",
	)

	if err != nil {
		fmt.Println("An error occurred:", err)
		return
	}

	var addr models.GCLocation

	err = json.Unmarshal(response, &addr)

	if err != nil {
		fmt.Println("An error occurred at unmarshaling:", err)
		return
	}

	if !newAddressNeedsUpdate(addr) {
		// save updated and old address
		return
	}

	// test 1
	response, err = utils.SearchAddressWithGeoCoder(
		*env,
		typedAddr.Address2,
		typedAddr.City,
		typedAddr.State,
		typedAddr.PostalCode,
		"SMARTY",
	)

	if err != nil {
		fmt.Println("An error occurred:", err)
		return
	}

	err = json.Unmarshal(response, &addr)

	if err != nil {
		fmt.Println("An error occurred at unmarshaling:", err)
		return
	}

	if !newAddressNeedsUpdate(addr) {
		// save updated and old address
		return
	}

	// test 2
	response, err = utils.SearchAddressWithGeoCoder(
		*env,
		typedAddr.Address1,
		typedAddr.City,
		typedAddr.State,
		typedAddr.PostalCode,
		"GOOGLE",
	)

	if err != nil {
		fmt.Println("An error occurred:", err)
		return
	}

	err = json.Unmarshal(response, &addr)

	if err != nil {
		fmt.Println("An error occurred at unmarshaling:", err)
		return
	}

	if !newAddressNeedsUpdate(addr) {
		// save updated and old address
		return
	}

	// test 3
	response, err = utils.SearchAddressWithGeoCoder(
		*env,
		typedAddr.Address2,
		typedAddr.City,
		typedAddr.State,
		typedAddr.PostalCode,
		"GOOGLE",
	)

	if err != nil {
		fmt.Println("An error occurred:", err)
		return
	}

	err = json.Unmarshal(response, &addr)

	if err != nil {
		fmt.Println("An error occurred at unmarshaling:", err)
		return
	}

	// save updated and old address

}

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
