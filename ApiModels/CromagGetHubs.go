package models

import "time"

type CromagGetHubs struct {
	Hubs             []Hub         `json:"hubs,omitempty"`
	Count            int64         `json:"count,omitempty"`
	StackTrace       []interface{} `json:"stackTrace,omitempty"`
	Status           string        `json:"status,omitempty"`
	StatusCode       int64         `json:"statusCode,omitempty"`
	Message          string        `json:"message,omitempty"`
	LocalizedMessage string        `json:"localizedMessage,omitempty"`
	Suppressed       []interface{} `json:"suppressed,omitempty"`
}

type Hub struct {
	ID                  string          `json:"id,omitempty"`
	Name                string          `json:"name,omitempty"`
	OrganizationID      string          `json:"organizationId,omitempty"`
	Description         string          `json:"description,omitempty"`
	Type                string          `json:"type,omitempty"`
	Notes               string          `json:"notes,omitempty"`
	Location            Location        `json:"location,omitempty"`
	Contact             Contact         `json:"contact,omitempty"`
	LogoURL             string          `json:"logoUrl,omitempty"`
	DeliveryDays        []string        `json:"deliveryDays,omitempty"`
	CutoffTimes         CutoffTimes     `json:"cutoffTimes,omitempty"`
	ExtraProperties     ExtraProperties `json:"extraProperties,omitempty"`
	GeofenceRadius      GeofenceRadius  `json:"geofenceRadius,omitempty"`
	Active              bool            `json:"active,omitempty"`
	CreationDate        time.Time       `json:"creationDate,omitempty"`
	LastUpdatedDate     time.Time       `json:"lastUpdatedDate,omitempty"`
	Version             int64           `json:"version,omitempty"`
	LastUpdatedByUserID string          `json:"lastUpdatedByUserId,omitempty"`
	LastUpdatedTime     int64           `json:"lastUpdatedT ime,omitempty"`
}

type Contact struct {
	ContactID string `json:"contactId,omitempty"`
	Name      string `json:"name,omitempty"`
	Phone     string `json:"phone,omitempty"`
	SMS       string `json:"sms,omitempty"`
	Email     string `json:"email,omitempty"`
}

type CutoffTimes struct {
	MessagingCutoffTime string `json:"messagingCutoffTime,omitempty"`
	ExecutionCutoffTime string `json:"executionCutoffTime,omitempty"`
	DepartCutoffTime    string `json:"departCutoffTime,omitempty"`
	DriverCutoffTime    string `json:"driverCutoffTime,omitempty"`
}

type CutoffTime struct {
	Hour   string `json:"hour,omitempty"`
	Minute string `json:"minute,omitempty"`
	Second string `json:"second,omitempty"`
	Nano   string `json:"nano,omitempty"`
}

type ExtraProperties struct {
}

type Location struct {
	LocationID string  `json:"locationId,omitempty"`
	TimeZone   string  `json:"timeZone,omitempty"`
	Latitude   float64 `json:"latitude,omitempty"`
	Longitude  float64 `json:"longitude,omitempty"`
}

type GeofenceRadius struct {
	Unit  string  `json:"unit,omitempty"`
	Value float32 `json:"value,omitempty"`
}
