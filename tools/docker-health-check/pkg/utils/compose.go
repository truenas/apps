package utils

import (
	"fmt"

	"github.com/compose-spec/compose-go/cli"
	"github.com/compose-spec/compose-go/types"
)

// CreateProjectWithNameFromFiles creates a project from the given files and name
func CreateProjectWithNameFromFiles(name string, files []string) (*types.Project, error) {
	// Create the project options
	composeOpts, err := cli.NewProjectOptions(
		files, cli.WithName(name),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create project options: %w", err)
	}

	project, err := cli.ProjectFromOptions(composeOpts)
	if err != nil {
		return nil, fmt.Errorf("failed to create project: %w", err)
	}

	return project, nil
}
