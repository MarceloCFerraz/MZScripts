package utils

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/valyala/fasthttp"
)

// TODO: analyze making env and orgId not pointers depending on how concurrency will be handled
func GetAddressFromGazetteer(env *string, orgId *string, hubName string, index int) ([]byte, error) {
	response := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(response)

	url := fmt.Sprintf(
		"https://gazetteer.%s.milezero.com/gazetteer-war/api/location/matching/org/%s",
		*env,
		*orgId,
	)

	payload := map[string]interface{}{
		"hubName":    hubName,
		"queryMode":  "MATCH_ALL_IN_ORDER",
		"pagination": map[string]interface{}{"from": index, "size": 500},
	}

	body, err := json.Marshal(payload)

	if err != nil {
		fmt.Println("An error occurred when marshaling payload for ", url)
		fmt.Println("ERROR: ", err)

		return nil, err
	}
	method := "POST"

	if err := SendResquet(url, method, body, response); err != nil {
		fmt.Println("An error occurred with request for ", url)
		fmt.Println("ERROR: ", err)

		return nil, err
	}

	return CheckResponse(response)
}

func UpdateAddress(env, orgId string, updatedAddress []byte) error {
	response := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(response)

	ConvertEnv(&env)

	url := fmt.Sprintf(
		"https://lockbox.%s.milezero.com/lockbox-war/api/location/%s",
		env,
		orgId,
	)
	method := "POST"

	if err := SendResquet(url, method, updatedAddress, response); err != nil {
		// maybe change the return type to bool or remove completely since the error is being printed here
		fmt.Println("An error occurred when trying to update the address: ", err)
		return err
	}

	if _, err := CheckResponse(response); err != nil {
		fmt.Println(err)
	}

	return nil
}

func SearchAddressWithGeoCoder(env, street, city, state, zip, provider string) ([]byte, error) {
	response := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(response)

	ConvertEnv(&env)

	method := "GET"
	url := fmt.Sprintf(
		"http://geocoder.%s.milezero.com/gc/api/address?street=%s&city=%s&state=%s&zip_code=%s&cc=US",
		env, street, city, state, zip,
	)

	if provider != "" {
		url = fmt.Sprintf("%s&provider=%s", url, strings.ToUpper(provider))
	}

	if err := SendResquet(url, method, nil, response); err != nil {
		// maybe change the return type to bool or remove completely since the error is being printed here
		fmt.Println("An error occurred when trying to update the address: ", err)
		return nil, err
	}

	return CheckResponse(response)
}

// TODO: change this function's return type later to return a cromag hubs object (not implemented yet)
func GetLocationFromLockbox(env, locationId string) ([]byte, error) {
	response := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(response)

	ConvertEnv(&env)

	url := fmt.Sprintf(
		"https://lockbox.%s.milezero.com/lockbox-war/api/location/%s",
		env, locationId,
	)
	method := "GET"

	if err := SendResquet(url, method, nil, response); err != nil {
		fmt.Println("An error occurred when trying to update the address: ", err)
		return nil, err
	}

	return CheckResponse(response)
}
