package utils

import (
	"encoding/json"
	"fmt"

	"github.com/valyala/fasthttp"
)

func GetAddressFromGazetteer(request *fasthttp.Request, response *fasthttp.Response, env string, orgId string, hubName string, index int) error {
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
		return err
	}

	request.SetBody(body)
	request.Header.SetMethod("POST")
	request.Header.SetContentType("application/json")
	request.Header.SetContentLength(len(body))

	if err = fasthttp.Do(request, response); err != nil {
		fmt.Println("An error occurred when marshaling payload for ", request)
		return err
	}

	return nil
}
