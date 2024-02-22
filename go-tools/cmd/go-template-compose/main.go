package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/truenas/go-template-compose/internal/compose"
	"github.com/truenas/go-template-compose/internal/engine"
	"github.com/truenas/go-template-compose/internal/types"
	"sigs.k8s.io/yaml"
)

const version = "0.0.1"
const (
	jsonOutput = "json"
	yamlOutput = "yaml"
)

var (
	// Format of the output (json or yaml)
	outputFormat string
	// Only output the compose data based on the output format
	composeOnly bool
)

func main() {
	parseFlags()
	var err error
	var out []byte

	result, err := run()
	if err != nil {
		result.Trace = err.Error()
	} else {
		result.Success = true
	}

	out, err = marshalResult(result)
	if err != nil {
		log.Fatalf("error marshalling %s: %v", outputFormat, err)
	}

	// Write to stdout
	fmt.Println(string(out))
}

func parseFlags() {
	flag.StringVar(&outputFormat, "out", "json", "output format (json or yaml)")
	flag.BoolVar(&composeOnly, "compose-only", false, "only output the compose data")
	flag.Parse()
}

func marshalResult(result types.Result) ([]byte, error) {
	var data interface{}
	if composeOnly {
		data = result.Compose
	} else {
		data = result
	}

	switch outputFormat {
	case yamlOutput:
		return yaml.Marshal(data)
	case jsonOutput:
		return json.Marshal(data)
	default:
		return nil, fmt.Errorf("error invalid output format: %s", outputFormat)
	}
}

func run() (types.Result, error) {
	var result types.Result
	var payload types.Payload

	// Read from stdin
	err := json.NewDecoder(os.Stdin).Decode(&payload)
	if err != nil {
		return result, fmt.Errorf("error decoding JSON: %w", err)
	}

	// Make sure the payload is valid
	if err := payload.IsValid(); err != nil {
		return result, err
	}

	// Create the template engine
	engine, err := engine.New(payload.TemplatesDir)
	if err != nil {
		return result, fmt.Errorf("error creating engine: %w", err)
	}

	// Prepare the template context
	templateCtx := types.NewTemplateContext(
		payload, version,
	)

	// Render the template
	composeBuf, err := engine.Render(templateCtx)
	if err != nil {
		result.Error = engine.CustomError
		return result, fmt.Errorf("error rendering template: %w", err)
	}

	// Append warnings and errors from the template engine
	result.Warnings = append(result.Warnings, engine.Warnings...)

	// Parse rendered template (from YAML)
	yamlData, err := compose.Parse(composeBuf)
	if err != nil {
		return result, fmt.Errorf("error parsing rendered template: %w", err)
	}

	// Convert compose to JSON
	result.Compose, err = json.Marshal(yamlData)
	if err != nil {
		return result, fmt.Errorf("error marshalling JSON: %w", err)
	}

	return result, nil
}
