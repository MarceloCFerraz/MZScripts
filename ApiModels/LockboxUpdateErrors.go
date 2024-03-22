package models

type LockBoxUpdateErrors []UpdateError

type UpdateError struct {
	Entity       string  `json:"entity,omitempty"`
	Property     string  `json:"property,omitempty"`
	InvalidValue *string `json:"invalidValue,omitempty"`
	Message      string  `json:"message,omitempty"`
}
