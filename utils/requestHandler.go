package utils

import (
	"encoding/json"
	"errors"
	"fmt"

	models "github.com/MarceloCFerraz/MZScripts/ApiModels"
	"github.com/valyala/fasthttp"
)

func SendResquet(url, method string, body []byte, response *fasthttp.Response) error {
	request := fasthttp.AcquireRequest()
	defer fasthttp.ReleaseRequest(request)

	request.SetRequestURI(url)
	// request.Header.
	request.Header.SetMethod(method) // POST or PUT?
	if body != nil {
		request.SetBody(body)
		request.Header.SetContentType("application/json")
		request.Header.SetContentLength(len(body))
	}

	return fasthttp.Do(request, response)
}

func CheckResponse(response *fasthttp.Response) ([]byte, error) {
	if response.StatusCode() >= 400 {
		msg := fmt.Sprintf("status %d",
			response.StatusCode(),
		)

		// TODO: make this more future proof by extending somehow from just LockBoxUpdateError to something more generic

		var parsedBody models.LockBoxUpdateErrors
		err := json.Unmarshal(response.Body(), &parsedBody)

		if err == nil {
			for _, er := range parsedBody {
				msg = fmt.Sprintf("%s - %s %s",
					msg,
					er.Property, er.Message,
				)
			}

		} else {
			msg = fmt.Sprintf("%s - %v", msg, string(response.Body()))
		}
		return nil, errors.New(msg)
	}

	return response.Body(), nil
}
