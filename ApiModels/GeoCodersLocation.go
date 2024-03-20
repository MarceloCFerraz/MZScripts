package models

type GCLocation struct {
	Street1        string  `json:"street1,omitempty"`
	City           string  `json:"city,omitempty"`
	State          string  `json:"state,omitempty"`
	Zip            string  `json:"zip,omitempty"`
	CountryCode    string  `json:"countryCode,omitempty"`
	Lat            float64 `json:"lat,omitempty"`
	Lon            float64 `json:"lon,omitempty"`
	Provider       string  `json:"provider,omitempty"`
	GeocodeQuality string  `json:"geocodeQuality,omitempty"`
	TimeZone       string  `json:"timeZone,omitempty"`

	StackTrace       []interface{} `json:"stackTrace,omitempty"`
	Status           string        `json:"status,omitempty"`
	Arg              string        `json:"arg,omitempty"`
	StatusCode       int64         `json:"statusCode,omitempty"`
	Message          string        `json:"message,omitempty"`
	LocalizedMessage string        `json:"localizedMessage,omitempty"`
	Suppressed       []interface{} `json:"suppressed,omitempty"`
}
