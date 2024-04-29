package utils

import (
	"strings"

	"github.com/docker/docker/api/types"
)

func IsHealthy(c types.ContainerJSON) bool {
	return c.State.Health.Status == "healthy"
}

func IsUnhealthy(c types.ContainerJSON) bool {
	return c.State.Health.Status == "unhealthy"
}

func IsExited(c types.ContainerJSON) bool {
	return c.State.Status == "exited"
}

func IsZeroExitCode(c types.ContainerJSON) bool {
	return c.State.ExitCode == 0
}

func GetExitCode(c types.ContainerJSON) int {
	return c.State.ExitCode
}

func IsRunning(c types.ContainerJSON) bool {
	return c.State.Status == "running"
}

func HasHealthCheck(c types.ContainerJSON) bool {
	return c.Config.Healthcheck != nil && len(c.Config.Healthcheck.Test) > 0
}

func GetFailedProbeLogs(c types.ContainerJSON) (string, error) {
	var buf strings.Builder
	for _, log := range c.State.Health.Log {
		if log.ExitCode != 0 && log.Output != "" {
			buf.WriteString(log.Output)
			buf.WriteString("\n")
		}
	}

	return buf.String(), nil
}
