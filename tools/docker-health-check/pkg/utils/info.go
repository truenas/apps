package utils

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/docker/docker/api/types"
)

type Result struct {
	Name        string              // Name of the container
	Fatal       bool                // True if the container is exited with a non-zero exit code.
	Healthy     bool                // True if the container is healthy, false if probe is failing
	HasCheck    bool                // True if the container has a health check
	TimedOut    bool                // True if the container timed out
	ExitCode    int                 // Exit code of the container
	Logs        string              // Logs of the container
	ProbeLogs   string              // Logs of the probe
	InspectData types.ContainerJSON // The full inspect data of the container
}

// map[container name]result
type Results map[string]Result

func LogResultsAndReturnUnhealthy(results Results) int {
	unhealthy := 0
	for name, res := range results {
		fmt.Println(strings.Repeat("=", 50), name, strings.Repeat("=", 50))
		fmt.Printf("Container: %s\n", name)
		fmt.Printf("Health Check: %t\n", res.HasCheck)
		fmt.Printf("Timed Out: %t\n", res.TimedOut)
		fmt.Printf("Healthy: %t\n", res.Healthy)
		fmt.Printf("Fatal: %t\n", res.Fatal)
		if res.Logs != "" {
			fmt.Printf("Logs: %s\n", res.Logs)
		} else {
			fmt.Println("Logs: No logs available")
		}

		if res.Fatal {
			fmt.Printf("Exit Code: %d\n", res.ExitCode)
			if res.ProbeLogs != "" {
				fmt.Printf("Probe Logs: %s\n", res.ProbeLogs)
			}
		}

		if !res.Healthy {
			unhealthy++
			data, _ := json.MarshalIndent(res.InspectData, "", "  ")
			fmt.Printf("Inspect Data: %s\n", string(data))
		}

		fmt.Printf("%s\n\n", strings.Repeat("=", 100+len(name)+2))
	}

	fmt.Println("Summary:")
	fmt.Printf("Containers: %d\n", len(results))
	fmt.Printf("Healthy: %d\n", len(results)-unhealthy)
	fmt.Printf("Unhealthy: %d\n", unhealthy)
	fmt.Println(strings.Repeat("-", 100))

	return unhealthy
}
