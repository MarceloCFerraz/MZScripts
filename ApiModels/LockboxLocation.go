package models

type LBLocation struct {
	ID                    string        `json:"id,omitempty"`
	Name                  string        `json:"name,omitempty"`
	Geo                   Geo           `json:"geo,omitempty"`
	TypedAddress          TypedAddress  `json:"typedAddress,omitempty"`
	Timezone              string        `json:"timezone,omitempty"`
	CommercialType        string        `json:"commercialType,omitempty"`
	Attributes            []interface{} `json:"attributes,omitempty"`
	Precision             Precision     `json:"precision,omitempty"`
	ExecutionScannableIDS Execution     `json:"executionScannableIds,omitempty"`
	ExecutionProperties   Execution     `json:"executionProperties,omitempty"`
	GpsMergable           bool          `json:"gpsMergable,omitempty"`
}

type Execution struct {
}

type Geo struct {
	Latitude  float64 `json:"latitude,omitempty"`
	Longitude float64 `json:"longitude,omitempty"`
}

type Precision struct {
	Precision string `json:"precision,omitempty"`
	Source    string `json:"source,omitempty"`
}

type TypedAddress struct {
	AddressType     string `json:"addressType,omitempty"`
	CountryCode     string `json:"countryCode,omitempty"`
	Name            string `json:"name,omitempty"`
	Address1        string `json:"address1,omitempty"`
	Address2        string `json:"address2,omitempty"`
	City            string `json:"city,omitempty"`
	State           string `json:"state,omitempty"`
	BriefPostalCode string `json:"briefPostalCode,omitempty"`
	PostalCode      string `json:"postalCode,omitempty"`
}
