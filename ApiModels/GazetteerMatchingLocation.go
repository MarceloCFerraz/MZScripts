package models

type GzMatchingLocation struct {
	StackTrace       []interface{}         `json:"stackTrace,omitempty"`
	Status           string                `json:"status,omitempty"`
	Resource         string                `json:"resource,omitempty"`
	StatusCode       int64                 `json:"statusCode,omitempty"`
	Message          string                `json:"message,omitempty"`
	LocalizedMessage string                `json:"localizedMessage,omitempty"`
	Suppressed       []interface{}         `json:"suppressed,omitempty"`
	Locations        map[string]GzLocation `json:"locations,omitempty"`
	Count            int64                 `json:"count,omitempty"`
	Total            int64                 `json:"total,omitempty"`
	Latency          int64                 `json:"latency,omitempty"`
}

type GzLocation struct {
	ID       string    `json:"id,omitempty"`
	Name     string    `json:"name,omitempty"`
	HubNames []string  `json:"hubNames,omitempty"`
	Address  GzAddress `json:"address,omitempty"`
	Contact  GzContact `json:"contact,omitempty"`
}

type GzAddress struct {
	AddressType string `json:"addressType,omitempty"`
	CountryCode string `json:"countryCode,omitempty"`
	Name        string `json:"name,omitempty"`
	Address1    string `json:"address1,omitempty"`
	Address2    string `json:"address2,omitempty"`
	City        string `json:"city,omitempty"`
	State       string `json:"state,omitempty"`
	PostalCode  string `json:"postalCode,omitempty"`
}

type GzContact struct {
	Name  string `json:"name,omitempty"`
	Phone string `json:"phone,omitempty"`
}
