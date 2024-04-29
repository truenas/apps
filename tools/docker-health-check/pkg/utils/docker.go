package utils

import (
	"context"
	"fmt"
	"io"
	"log"

	"github.com/docker/docker/api/types"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/filters"
	"github.com/docker/docker/client"
)

var apiClient *client.Client

const composeLabel = "com.docker.compose.project"

func init() {
	c, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		log.Fatal(err)
	}

	apiClient = c
}

// GetInspectData returns the inspect data of the container
func GetInspectData(cID string) (types.ContainerJSON, error) {
	container, err := apiClient.ContainerInspect(context.Background(), cID)
	if err != nil {
		return types.ContainerJSON{}, fmt.Errorf("failed to inspect container: %w", err)
	}
	return container, nil
}

// GetLogs returns the logs of the container
func GetLogs(cID string) (string, error) {
	body, err := apiClient.ContainerLogs(context.Background(), cID,
		container.LogsOptions{
			ShowStdout: true,
			ShowStderr: true,
			Timestamps: false,
			Tail:       "any",
		},
	)
	if err != nil {
		return "", fmt.Errorf("failed to get logs: %w", err)
	}
	defer body.Close()

	out, err := io.ReadAll(body)
	return string(out), err
}

// GetContainersFromProject returns the containers from the compose project based on the label
func GetContainersFromProject(composeName string) ([]types.Container, error) {
	containers, err := apiClient.ContainerList(
		context.Background(),
		container.ListOptions{All: true, Filters: filters.NewArgs(
			filters.Arg("label", fmt.Sprintf("%s=%s", composeLabel, composeName)),
		)},
	)

	if err != nil {
		return nil, fmt.Errorf("failed to list containers: %w", err)
	}

	return containers, nil
}
