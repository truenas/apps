package compose

import (
	"bytes"
	"fmt"

	"github.com/truenas/go-template-compose/internal/utils"
	"sigs.k8s.io/yaml"
)

func Parse(b bytes.Buffer) (interface{}, error) {
	// Replace tabs with spaces
	utils.ReplaceTabsWithSpaces(&b, 2)

	var yamlData interface{}
	if err := yaml.Unmarshal(b.Bytes(), &yamlData); err != nil {
		return nil, fmt.Errorf("error decoding yaml: %w", err)
	}

	// TODO: Parse the rendered template for any data we want to extract here
	// eg ports, volumes, security context, etc

	return yamlData, nil
}
