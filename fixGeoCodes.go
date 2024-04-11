package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"

	models "github.com/MarceloCFerraz/MZScripts/ApiModels"
	"github.com/MarceloCFerraz/MZScripts/utils"
)

type Succeeded struct {
	newAddress models.LBLocation
	oldAddress models.LBLocation
}

type Failed struct {
	address      models.LBLocation
	errorMessage error
}

func main() {
	startTime := time.Now().UTC()
	fmt.Println(startTime)

	util := utils.Initialize()

	var env, orgId, orgName string
	var found bool

	if env, found = os.LookupEnv("ENVIROMENT"); !found {
		env = util.SelectEnv()
	}

	if orgName, found = os.LookupEnv("ORG"); found {
		orgId = util.SelectOrg(env, orgName)
	} else {
		orgId = util.SelectOrg(env)
	}

	fmt.Println("Fetching available Hubs...")
	allHubs, err := getAllHubs(&env, &orgId)

	if err != nil {
		fmt.Println("An error occurred when getting all hubs: ", err)
		os.Exit(1)
	}

	// TODO: Add another option to read from .txt file
	options := []string{"Update All Hubs", "Update specific Hubs (from console)"}
	var hubNames []string
	var option int64

	if opt, found := os.LookupEnv("SEARCH_OPTION"); !found {
		option = utils.SelectOption(&options)
	} else if option, err = strconv.ParseInt(opt, 10, 32); err != nil {
		fmt.Println("Unable to int parse the provided arg option. Check error below", opt)
		panic(err)
	}

	switch option {
	case 0:
		hubNames = getAllHubNames(&allHubs)
	case 1:
		getHubNamesFromUser(&hubNames, &allHubs)
	case 2:
		if hubs, found := os.LookupEnv("HUB_NAMES"); found {
			json.Unmarshal([]byte(hubs), &hubNames)
		}
		fmt.Println("Fixing geo codes provided by env:", hubNames)
	// TODO: Add another option to read from .txt file
	default:
		panic("Please provide a valid option")
	}

	successes := make(chan Succeeded)
	failures := make(chan Failed)

	var successLines [][]string
	var failLines [][]string

	wg := sync.WaitGroup{}

	wg.Add(2)

	go startSuccessReader(&successes, &successLines, &wg)
	go startFailsReader(&failures, &failLines, &wg)

	processHubs(&env, &orgId, &hubNames, &successes, &failures)
	//---------------------------------------
	wg.Wait()
	// wait readers finish converting data into csv lines

	successFile := fmt.Sprintf(
		"UPDATED_ADDRESSES_%s.csv",
		strings.ReplaceAll(startTime.UTC().Format(time.RFC3339), ":", "_"),
	)
	successCsv, err := os.Create(successFile)

	if err != nil {
		fmt.Println("Something went wrong when creating successes file:", err)
		fmt.Printf("We updated %d addresses:\n", len(successLines))
		fmt.Println(successLines)
	}
	successWriter := csv.NewWriter(successCsv)

	saveDataToFile(successFile, &successLines, successWriter)

	successCsv.Close()
	//-------------------------------------

	failFile := fmt.Sprintf(
		"FAILED_ADDRESSES_%s.csv",
		strings.ReplaceAll(startTime.UTC().Format(time.RFC3339), ":", "_"),
	)
	failCsv, err := os.Create(failFile)

	if err != nil {
		fmt.Println("Something went wrong when creating failures file:", err)
		fmt.Printf("%d addresses failed to be updated:\n", len(successLines))
		fmt.Println(successLines)
	}
	failWriter := csv.NewWriter(failCsv)
	saveDataToFile(failFile, &failLines, failWriter)

	failCsv.Close()
	//--------------------------------------

	fmt.Println("Hubs Updated:", len(hubNames))
	fmt.Println("Successful Updates:", len(successLines))
	fmt.Println("Failed Updates:", len(failLines))
	fmt.Println(failLines)
	fmt.Println("Total Processing Time:", time.Now().UTC().Sub(startTime))
	fmt.Println("Exiting program...")
	os.Exit(0)
}

func saveDataToFile(fileName string, csvLines *[][]string, writer *csv.Writer) {
	fmt.Printf("Saving data to file:%s\n", fileName)

	// err := writer.WriteAll(*csvLines) // saves all data with one line

	for i, row := range *csvLines {
		writeErr := writer.Write(row)

		if writeErr != nil {
			fmt.Printf("Error saving row %d:\n", i)
			fmt.Println("Row:", row)
			fmt.Println("Error:", writeErr)
			continue
		}

		writer.Flush() // ensure data is written
		flushError := writer.Error()

		if flushError != nil {
			fmt.Println("Error flushing data")
			fmt.Println("Error:", writeErr)
		}
	}
}

func startSuccessReader(successes *chan Succeeded, csvLines *[][]string, wg *sync.WaitGroup) {
	headers := []string{
		"Hub",
		"ID", "Name",
		"Old Geo Quality", "New Geo Quality",
		"Old Provider", "New Provider",
		"Old Lat", "New Lat",
		"Old Long", "New Long",
		"Old Address 1", "New Address 1",
		"Old Address 2", "New Address 2",
	}

	*csvLines = append(*csvLines, headers)

	for {
		result, open := <-*successes

		if !open {
			wg.Done()
			return
		}

		line := []string{
			result.newAddress.Hub,
			result.newAddress.ID, result.newAddress.Name,
			result.oldAddress.Precision.Precision, result.newAddress.Precision.Precision,
			result.oldAddress.Precision.Source, result.newAddress.Precision.Source,
			fmt.Sprintf("%f", result.oldAddress.Geo.Latitude), fmt.Sprintf("%f", result.oldAddress.Geo.Longitude),
			fmt.Sprintf("%f", result.newAddress.Geo.Latitude), fmt.Sprintf("%f", result.newAddress.Geo.Longitude),
			result.oldAddress.TypedAddress.Address1, result.newAddress.TypedAddress.Address1,
			result.oldAddress.TypedAddress.Address2, result.newAddress.TypedAddress.Address2,
		}

		*csvLines = append(*csvLines, line)
	}
}

func startFailsReader(fails *chan Failed, csvLines *[][]string, wg *sync.WaitGroup) {

	headers := []string{
		"Hub",
		"ID", "Name",
		"Error Message",
		"Geo Quality", "Provider",
		"Latitude", "Longitude",
		"Address Line 1", "Address Line 2",
		"City", "State", "Zip", "Country", "Address Type", "Timezone",
	}

	*csvLines = append(*csvLines, headers)

	for {
		result, open := <-*fails

		if !open {
			wg.Done()
			return
		}

		regex := regexp.MustCompile(`[{},:"\[\]]`)

		line := []string{
			result.address.Hub,
			result.address.ID, result.address.Name,
			strings.ReplaceAll(regex.ReplaceAllString(result.errorMessage.Error(), " "), "\n", ""),
			result.address.Precision.Precision, result.address.Precision.Source,
			fmt.Sprintf("%f", result.address.Geo.Latitude), fmt.Sprintf("%f", result.address.Geo.Longitude),
			result.address.TypedAddress.Address1, result.address.TypedAddress.Address2,
			result.address.TypedAddress.City, result.address.TypedAddress.State,
			result.address.TypedAddress.PostalCode, result.address.TypedAddress.CountryCode,
			result.address.TypedAddress.AddressType, result.address.Timezone,
		}

		*csvLines = append(*csvLines, line)
	}
}

func getAllHubs(env, orgId *string) (models.CromagGetHubs, error) {
	var allHubs models.CromagGetHubs
	temp, err := utils.GetAllHubs(env, orgId)

	if err != nil {
		return models.CromagGetHubs{}, err
	}

	err = json.Unmarshal(temp, &allHubs)

	if err != nil {
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

		if _, err := fmt.Scanf("%s", &hubName); err != nil {
			// if input is new line and hubNames have at least one item
			if err.Error() == "unexpected newline" && len(*hubNames) > 0 {
				fmt.Println("Returning...")
				return
			}
			fmt.Println("Type a valid option! ")
			continue
		}

		if utils.Contains(hubNames, &hubName) {
			fmt.Println("You've already selected this hub. Try a different one")
			continue
		}

		if !utils.Contains(&allNames, &hubName) {
			fmt.Println(hubName, "doesn't exist in this org")
			continue
		}

		*hubNames = append(*hubNames, hubName)

		// fmt.Println("Press Enter to continue")
		// fmt.Scanln()
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

func processHubs(
	env, orgId *string,
	hubNames *[]string,
	successes *chan Succeeded,
	failures *chan Failed,
) {
	defer close(*successes)
	defer close(*failures)

	semaphore := make(chan bool, 100) // limits the max amount of goroutines to 100
	wg := sync.WaitGroup{}

	for _, hub := range *hubNames {
		fmt.Printf("-------------------- Starting hub %s --------------------\n", hub)

		// max is 10k addresses for each hub in gazetteer
		// request 10000 addresses per api call
		// increase another 10k and fetch the next batch of addresses until all were read
		increase := 10_000

		for i := 0; i < 10_000; i = i + increase {
			batch, err := utils.GetAddressFromGazetteer(env, orgId, hub, i, increase)

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
				go processHubLocations(
					env, hub, location.ID,
					&semaphore, &wg, successes, failures,
				)
			}
		}
		wg.Wait() // wait until all goroutines have finished

		fmt.Printf("-------------------- Finishing hub %s --------------------\n", hub)
	}
}

func processHubLocations(
	env *string,
	hubName string,
	locationId string,
	semaphore *chan bool,
	wg *sync.WaitGroup,
	successes *chan Succeeded,
	failures *chan Failed,
) {
	defer wg.Done()
	defer func() { <-*semaphore }() // deferring the removal of whatever is in the semaphore
	// this is basically saying: "hey, this goroutine has finished, some other goroutine can execute now"
	// fmt.Println("Go Routines:", len(*semaphore))

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

	if locationNeedsUpdate(&location) {
		location.Hub = hubName
		updateLocation(env, location, successes, failures)
	}
}

func updateLocation(
	env *string,
	location models.LBLocation,
	successes *chan Succeeded,
	failures *chan Failed,
) {
	success := Succeeded{}
	fail := Failed{}

	success.oldAddress = location
	// fmt.Printf("Original Location: %v\n", location)

	typedAddr := location.TypedAddress

	bestGeoCoderLocation := getBestLoc(env, &typedAddr, &location.ID)

	// fmt.Printf("Best geo location: %v\n", bestGeoCoderLocation)

	location.Geo.Latitude = bestGeoCoderLocation.Lat
	location.Geo.Longitude = bestGeoCoderLocation.Lon
	location.Precision.Precision = bestGeoCoderLocation.GeocodeQuality
	location.Precision.Source = bestGeoCoderLocation.Provider
	location.Timezone = bestGeoCoderLocation.TimeZone
	// location.TypedAddress is already updated in getBestLoc, i'm passing a pointer to it

	success.newAddress = location
	fail.address = location

	err := updateAddress(env, &location)

	if err != nil {
		fmt.Printf("An error occurred when trying to update location '%s' in lockbox\n", location.ID)
		fmt.Println("Error:", err)

		fail.errorMessage = err
		*failures <- fail

		return
	}

	*successes <- success
}

func getBestLoc(env *string, typedAddr *models.TypedAddress, locationId *string) models.GCLocation {
	tests := make([]models.GCLocation, 4)
	addr1 := strings.TrimSpace(typedAddr.Address1)
	addr2 := strings.TrimSpace(typedAddr.Address2)
	smarty := "SMARTY"
	google := "GOOGLE"

	// test 1
	test1, err := getGCAddress(env, &smarty, typedAddr)

	if err != nil {
		// fmt.Printf("Test 1 for location %s failed\n", *locationId)
		// fmt.Println("Error:", err)
	}

	// fmt.Printf("Test 1: %v\n", test1)

	if !newLocationNeedsUpdate(&test1) {
		return test1
	}
	tests = append(tests, test1)

	// test 2
	if addr2 != "" {
		typedAddr.Address1 = addr2
		typedAddr.Address2 = addr1

		test2, err := getGCAddress(env, &smarty, typedAddr)

		if err != nil {
			// fmt.Printf("Test 2 for location %s failed\n", *locationId)
			// fmt.Println("Error:", err)
		}

		// fmt.Printf("Test 2: %v\n", test2)

		if !newLocationNeedsUpdate(&test2) {
			return test2
		}
		tests = append(tests, test2)
	}

	// test 3
	typedAddr.Address1 = addr1
	typedAddr.Address2 = addr2

	test3, err := getGCAddress(env, &google, typedAddr)

	if err != nil {
		// fmt.Printf("Test 3 for location %s failed\n", *locationId)
		// fmt.Println("Error:", err)
	}

	// fmt.Printf("Test 3: %v\n", test3)

	if !newLocationNeedsUpdate(&test3) {
		return test3
	}
	tests = append(tests, test3)

	// test 4
	if addr2 != "" {
		typedAddr.Address1 = addr2
		typedAddr.Address2 = addr1

		test4, err := getGCAddress(env, &google, typedAddr)

		if err != nil {
			// fmt.Printf("Test 4 for location %s failed\n", *locationId)
			// fmt.Println("Error:", err)
		}

		// fmt.Printf("Test 4: %v\n", test4)

		if !newLocationNeedsUpdate(&test4) {
			return test4
		}
		tests = append(tests, test4)
	}

	// none of the above tries were sufficient, so save the best option and let the user know

	fmt.Printf("Location %s have a bad address. We'll use the best option available\n", *locationId)
	var bestLoc *models.GCLocation

	for _, loc := range tests {
		if bestLoc == nil {
			bestLoc = &loc
			continue
		}

		if getLocGeocodeWeight(&loc) > getLocGeocodeWeight(bestLoc) {
			bestLoc = &loc
		}
	}

	return *bestLoc
}

func locationNeedsUpdate(location *models.LBLocation) bool {
	if location.Precision.Precision == "EXACT" || // location is already perfect
		location.Precision.Precision == "HIGH" { // geocode is good enough
		return false
	}

	return true
}

func newLocationNeedsUpdate(location *models.GCLocation) bool {
	if location.GeocodeQuality == "EXACT" || // location is already perfect
		location.GeocodeQuality == "HIGH" { // geocode is good enough
		return false
	}

	return true
}

func getGCAddress(env, provider *string, address *models.TypedAddress) (models.GCLocation, error) {
	var addr models.GCLocation

	response, err := utils.SearchAddressWithGeoCoder(
		*env,
		strings.ReplaceAll(address.Address1, " ", "%20"),
		strings.ReplaceAll(address.City, " ", "%20"),
		strings.ReplaceAll(address.State, " ", "%20"),
		strings.ReplaceAll(address.PostalCode, " ", "%20"),
		*provider,
	)

	if err != nil {
		fmt.Println("Failed to get data from geocoder")
		return models.GCLocation{}, err
	}

	err = json.Unmarshal(response, &addr)

	if err != nil {
		fmt.Println("Failed unmarshal data from geocoder")
		return models.GCLocation{}, err
	}

	return addr, nil
}

func updateAddress(env *string, loc *models.LBLocation) error {
	locationId := loc.ID
	loc.ID = ""
	data, err := json.Marshal(&loc)

	if err != nil {
		fmt.Println("An error occurred when unmarshaling loc", loc.ID)
		fmt.Println("Error:", err)
		return err
	}
	return utils.UpdateAddress(*env, locationId, data)
}

func getLocGeocodeWeight(loc *models.GCLocation) int {
	switch loc.GeocodeQuality {
	case "LOW":
		return 1
	case "MEDIUM":
		return 2
	case "HIGH":
		return 3
	default:
		return 0
	}
}
