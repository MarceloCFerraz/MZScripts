package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"sync"
	"time"

	models "github.com/MarceloCFerraz/MZScripts/ApiModels"
	"github.com/MarceloCFerraz/MZScripts/utils"
)

type Result struct {
	newAddress models.LBLocation
	oldAddress models.LBLocation
}

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

	var csvLines [][]string
	results := make(chan Result)
	done := make(chan bool)

	go startReader(&results, &csvLines, &done)

	processHubs(&env, &orgId, &hubNames, &results)
	<-done
	// wait for reader finish read all updated addresses and convert them into csv lines

	fileName := fmt.Sprintf(
		"UPDATED_ADDRESSES_%s.csv",
		strings.ReplaceAll(startTime.UTC().Format(time.RFC3339), ":", "_"),
	)
	csvFile, err := os.Create(fileName)

	if err != nil {
		fmt.Println("Something went wrong when creating the result file:", err)
		fmt.Printf("We updated %d addresses:\n", len(csvLines))
		fmt.Println(csvLines)
	}
	defer csvFile.Close()

	writer := csv.NewWriter(csvFile)

	saveDataToFile(fileName, &csvLines, writer)

	fmt.Println("Exiting program...")
	os.Exit(0)
}

func saveDataToFile(fileName string, csvLines *[][]string, writer *csv.Writer) {
	fmt.Printf("Saving updated data to file:%s\n", fileName)
	rowCount := 0

	// err := writer.WriteAll(*csvLines) // saves all data with one line

	for i, row := range *csvLines {
		writeErr := writer.Write(row)

		if writeErr != nil {
			fmt.Printf("Error saving row %d:\n", i)
			fmt.Println("Row:", row)
			fmt.Println("Error:", writeErr)
			continue
		}

		rowCount++

		if rowCount%10 == 0 {
			writer.Flush() // ensure data is written
			flushError := writer.Error()
			if flushError != nil {
				fmt.Println("Error flushing data")
				fmt.Println("Error:", writeErr)
			}
			rowCount = 0
		}
	}
}

func startReader(results *chan Result, csvLines *[][]string, done *chan bool) {
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
		result, open := <-*results

		if !open {
			*done <- true
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

func processHubs(env, orgId *string, hubNames *[]string, results *chan Result) {
	defer close(*results)

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
				go processHubLocations(env, hub, location.ID, &semaphore, &wg, results)
			}
		}
		wg.Wait() // wait until all goroutines have finished

		fmt.Printf("------------------ Finishing hub %s ------------------\n", hub)
	}
}

func processHubLocations(env *string, hubName string, locationId string, semaphore *chan bool, wg *sync.WaitGroup, results *chan Result) {
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
		updateLocation(env, location, results)
	}
}

func updateLocation(env *string, location models.LBLocation, results *chan Result) {
	update := Result{}
	update.oldAddress = location
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

	update.newAddress = location

	*results <- update
	err := saveAddress(env, &location)

	if err != nil {
		fmt.Printf("An error occurred when trying to update address %s in locbox\n", location.ID)
		fmt.Println("Error:", err)
	}
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
		fmt.Printf("An error occurred during Test 1 for location %s:\n", *locationId)
		fmt.Println("Error:", err)
	}

	// fmt.Printf("Test 1: %v\n", test1)

	if !newAddressNeedsUpdate(&test1) {
		return test1
	}
	tests = append(tests, test1)

	// test 2
	if addr2 != "" {
		typedAddr.Address1 = addr2
		typedAddr.Address2 = addr1

		test2, err := getGCAddress(env, &smarty, typedAddr)

		if err != nil {
			fmt.Printf("An error occurred during Test 2 for location %s:\n", *locationId)
			fmt.Println("Error:", err)
		}

		// fmt.Printf("Test 2: %v\n", test2)

		if !newAddressNeedsUpdate(&test2) {
			return test2
		}
		tests = append(tests, test2)
	}

	// test 3
	typedAddr.Address1 = addr1
	typedAddr.Address2 = addr2

	test3, err := getGCAddress(env, &google, typedAddr)

	if err != nil {
		fmt.Printf("An error occurred during Test 3 for location %s:\n", *locationId)
		fmt.Println("Error:", err)
	}

	// fmt.Printf("Test 3: %v\n", test3)

	if !newAddressNeedsUpdate(&test3) {
		return test3
	}
	tests = append(tests, test3)

	// test 4
	if addr2 != "" {
		typedAddr.Address1 = addr2
		typedAddr.Address2 = addr1

		test4, err := getGCAddress(env, &google, typedAddr)

		if err != nil {
			fmt.Printf("An error occurred during Test 4 for location %s:\n", *locationId)
			fmt.Println("Error:", err)
		}

		// fmt.Printf("Test 4: %v\n", test4)

		if !newAddressNeedsUpdate(&test4) {
			return test4
		}
		tests = append(tests, test4)
	}

	// none of the above tries were sufficient, so save the best option and let the user know

	fmt.Println("None of our tries were sufficient, we'll update the location with the best option")
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

func newAddressNeedsUpdate(location *models.GCLocation) bool {
	if location.GeocodeQuality == "EXACT" || // location is already perfect
		location.GeocodeQuality == "HIGH" { // geocode is good enough
		return false
	}

	return true
}

func getGCAddress(env, provider *string, address *models.TypedAddress) (models.GCLocation, error) {
	var addr models.GCLocation

	response, err := utils.SearchAddressWithGeoCoder(
		*env, strings.ReplaceAll(address.Address1, " ", "%20"), address.City,
		address.State, address.PostalCode, *provider,
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

func saveAddress(env *string, loc *models.LBLocation) error {
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
