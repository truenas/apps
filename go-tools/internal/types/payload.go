package types

import (
	"fmt"
)

// Payload is the payload that is sent from the middleware
type Payload struct {
	// Metadata that is sent from the middleware
	AppCtx AppContext `json:"app_context"`
	// User configuration that is sent from the middleware (coming from UI)
	Values map[string]interface{} `json:"values"`
	// Templates directory (eg "/mnt/POOL/ix-applications/plex/templates")
	TemplatesDir string `json:"templates_dir"`
}

// AppContext holds the metadata about the application
type AppContext struct {
	// The name of the app (eg "plex")
	Name string `json:"name"`
	// The version of the app (eg "1.18.0")
	Version string `json:"version"`
	// The operation that is being performed (eg "install")
	Operation string `json:"operation"`
	// The upgrade metadata
	UpgradeMetadata UpgradeMetadata `json:"upgrade_metadata"`
	// The system metadata
	System SystemData `json:"system"`
	// Add more fields as needed
}

// UpgradeMetadata holds the metadata about the upgrade
type UpgradeMetadata struct {
	// The version that the app is being upgraded from (eg "1.17.0")
	FromVersion string `json:"from_version"`
	// The version that the app is being upgraded to (eg "1.18.0")
	ToVersion string `json:"to_version"`
	// Add more fields as needed
}

// SystemData holds the metadata about the system
type SystemData struct {
	// The version of SCALE that is being used (eg "21.02")
	ScaleVersion string `json:"scale_version"`
	// The dataset allocated for the app (eg "/mnt/POOL/ix-applications/releases/plex")
	AppDataset string `json:"app_dataset"`
	// The version of this tool
	ToolVersion string
	// Add more fields as needed
}

func (p *Payload) IsValid() error {
	if p.TemplatesDir == "" {
		return fmt.Errorf("error no template directory provided")
	}

	if p.Values == nil {
		return fmt.Errorf("error no values provided")
	}

	if p.AppCtx == (AppContext{}) {
		return fmt.Errorf("error no app metadata provided")
	}

	return nil
}
