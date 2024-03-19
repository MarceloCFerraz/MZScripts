package models

type LBLocation struct {
	ID                    string        `json:"id,omitempty"`
	Name                  string        `json:"name,omitempty"`
	Geo                   Geo           `json:"geo,omitempty"`
	TypedAddress          TypedAddress  `json:"typedAddress,omitempty"`
	CustomDescription     string        `json:"customDescription,omitempty"`
	Timezone              string        `json:"timezone,omitempty"`
	CommercialType        string        `json:"commercialType,omitempty"`
	Attributes            []interface{} `json:"attributes,omitempty"`
	ExecutionScannableIDS interface{}   `json:"executionScannableIds,omitempty"`
	ExecutionProperties   interface{}   `json:"executionProperties,omitempty"`
	GpsMergable           bool          `json:"gpsMergable,omitempty"`
}

type Geo struct {
	Latitude  float64 `json:"latitude,omitempty"`
	Longitude float64 `json:"longitude,omitempty"`
}

type TypedAddress struct {
	AddressType string `json:"addressType,omitempty"`
	CountryCode string `json:"countryCode,omitempty"`
	Address1    string `json:"address1,omitempty"`
	City        string `json:"city,omitempty"`
	State       string `json:"state,omitempty"`
	PostalCode  string `json:"postalCode,omitempty"`
}
