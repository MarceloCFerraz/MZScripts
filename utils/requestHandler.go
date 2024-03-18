package utils

import (
	"fmt"

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
		return nil, fmt.Errorf(
			"request to %s failed with status code %d. body: %v",
			response.RemoteAddr(),
			response.StatusCode(),
			string(response.Body()),
		)
	}

	return response.Body(), nil
}
