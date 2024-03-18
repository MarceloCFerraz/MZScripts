package utils

import (
	"fmt"

	"github.com/valyala/fasthttp"
)

func GetAllHubs(env *string, orgId *string) ([]byte, error) {
	response := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(response)

	ConvertEnv(env)

	url := fmt.Sprintf("http://cromag.%s.milezero.com/retail/api/hubs/org/%s", *env, *orgId)
	method := "GET"

	if err := SendResquet(url, method, nil, response); err != nil {
		fmt.Println("An error occurred with request for ", url)
		fmt.Println("ERROR: ", err)
		return nil, err
	}

	return CheckResponse(response)
}

// TODO: change this function's return type later to return a cromag hubs object (not implemented yet)
func GetAllHubNames(env *string, orgId *string, hubNames *[]string) error {
	allHubs, err := GetAllHubs(env, orgId)

	if allHubs == nil || err != nil {
		fmt.Println("Couldn't get all Hub Names. Check error from GetAllHubs")
		return nil
	}

	// TODO:
	// create type for cromag response
	// unmarshal bytes received
	// return typed object
	return nil
}
