package types

import "encoding/json"

// Result is the return value that is sent back to the middleware
type Result struct {
	// Indicates if the operation was successful.
	Success bool `json:"success"`
	// Error message to be displayed to the user.
	Error string `json:"error"`
	// Trace of the error for debugging purposes.
	Trace string `json:"trace"`
	// List of warnings to be displayed to the user.
	// (TODO: See if we can make them actionable, eg "This will do X operation, do you want to continue, Y/N?")
	Warnings []string `json:"warnings"`
	// Short summary of the configuration or markdown to be displayed to the user (Similar to NOTES.txt in helm)
	Summary string `json:"summary"`
	// List of portals that are created. This will populate the UI with button(s) to access the service(s)
	Portals []Portal `json:"portals"`
	// Security context that is created (per container). This can be displayed in the UI for the user to review
	SecurityContext map[string]SecurityContext `json:"security_context"`
	// Devices that are added (per container). This can be displayed in the UI for the user to review
	Devices map[string][]Device `json:"devices"`
	// The rendered docker compose definition
	Compose json.RawMessage `json:"compose"`
	// Add more fields as needed
}

// Portal holds the information about a button
type Portal struct {
	// Name of the portal (Button name eg "Open")
	Name string `json:"name"`
	// Scheme of the portal (eg "http")
	Scheme string `json:"scheme"`
	// Host of the portal (eg "192.168.1.100")
	Host string `json:"host"`
	// Port of the portal (eg 32400)
	Port int `json:"port"`
}

// SecurityContext holds the security context for a container
type SecurityContext struct {
	User       string   `json:"user"`
	Group      string   `json:"group"`
	CapsAdd    []string `json:"caps_add"`
	CapsDrop   []string `json:"caps_drop"`
	Privileged bool     `json:"privileged"`
	// Add more fields as needed
}

// Device holds the information about a device (eg a usb)
type Device struct {
	PathOnHost      string `json:"path_on_host"`
	PathInContainer string `json:"path_in_container"`
}
