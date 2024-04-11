package utils

import (
	"context"
	"fmt"
	"io"
	"log"
	"strings"

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

// HasHealthCheck checks if the container has a health check
func HasHealthCheck(cID string) (bool, error) {
	container, err := GetInspectData(cID)
	if err != nil {
		return false, fmt.Errorf("failed to inspect container: %w", err)
	}
	if container.Config.Healthcheck == nil {
		return false, nil
	}
	if len(container.Config.Healthcheck.Test) > 0 {
		return true, nil
	}

	return false, nil
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

// GetExitCode returns the exit code of the container
func GetExitCode(cID string) (int, error) {
	container, err := GetInspectData(cID)
	if err != nil {
		return 0, fmt.Errorf("failed to inspect container: %w", err)
	}

	return container.State.ExitCode, nil
}

// GetFailedProbeLogs returns the logs of the failed probes
func GetFailedProbeLogs(cID string) (string, error) {
	container, err := GetInspectData(cID)
	if err != nil {
		return "", fmt.Errorf("failed to inspect container: %w", err)
	}

	var buf strings.Builder
	for _, log := range container.State.Health.Log {
		if log.ExitCode != 0 && log.Output != "" {
			buf.WriteString(log.Output)
			buf.WriteString("\n")
		}
	}

	return buf.String(), nil
}

// IsRunning returns true if the container is in the "running" state
func IsRunning(cID string) (bool, error) {
	state, err := GetState(cID)
	if err != nil {
		return false, fmt.Errorf("failed to get container state: %w", err)
	}
	return state == "running", nil
}

func IsExited(cID string) (bool, error) {
	state, err := GetState(cID)
	if err != nil {
		return false, fmt.Errorf("failed to get container state: %w", err)
	}
	return state == "exited", nil
}

func GetState(cID string) (string, error) {
	container, err := GetInspectData(cID)
	if err != nil {
		return "", fmt.Errorf("failed to inspect container: %w", err)
	}
	return container.State.Status, nil
}

// GetHealth returns the health status of the container
func GetHealth(cID string) (string, error) {
	container, err := GetInspectData(cID)
	if err != nil {
		return "", fmt.Errorf("failed to inspect container: %w", err)
	}
	if container.State.Health == nil {
		return "", nil
	}
	return container.State.Health.Status, nil
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
