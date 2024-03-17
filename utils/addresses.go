package utils

import (
	"encoding/json"
	"errors"
	"fmt"

	"github.com/valyala/fasthttp"
)

func GetAllHubs(env *string, orgId *string)

func GetAllHubNames(env *string, orgId *string, hubNames *[]string) error {
	return nil

}

func GetAddressFromGazetteer(env string, orgId string, hubName string, index int) ([]byte, error) {
	request := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(request)

	response := fasthttp.AcquireResponse()
	defer fasthttp.ReleaseResponse(response)
	response.Body()
	request.SetRequestURI(
		fmt.Sprintf(
			"https://gazetteer.%s.milezero.com/gazetteer-war/api/location/matching/org/%s",
			env, orgId,
		),
	)
	payload := map[string]interface{}{
		"hubName":    hubName,
		"queryMode":  "MATCH_ALL_IN_ORDER",
		"pagination": map[string]interface{}{"from": index, "size": 500},
	}

	body, err := json.Marshal(payload)

	if err != nil {
		fmt.Println(
			"An error occurred when marshaling payload for ",
			string(request.RequestURI()),
			": ", err,
		)
		return nil, err
	}

	request.SetBody(body)
	request.Header.SetMethod("POST")
	request.Header.SetContentType("application/json")
	request.Header.SetContentLength(len(body))

	if err = fasthttp.Do(request, response); err != nil {
		fmt.Println("An error occurred when marshaling payload for ", request)
		return nil, err
	}

	if !(response.StatusCode() < 400) {
		fmt.Println("Request failed with status ", response.StatusCode())
		fmt.Println("Body: ", string(response.Body()))
		return nil, errors.New("Get Request failed")
	}

	return response.Body(), nil
}
