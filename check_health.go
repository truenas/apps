package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"strings"
	"sync"
	"time"

	c_cli "github.com/compose-spec/compose-go/cli"
	c_types "github.com/compose-spec/compose-go/types"
	d_types "github.com/docker/docker/api/types"
	d_container "github.com/docker/docker/api/types/container"
	d_filters "github.com/docker/docker/api/types/filters"
	d_client "github.com/docker/docker/client"
)

type Result struct {
	Name      string
	Fatal     bool
	Healthy   bool
	HasCheck  bool
	Logs      string
	ProbeLogs string
}

type Results map[string]Result

var flag_name string
var flag_files string
var flag_timeout int

var name string
var files []string
var timeout time.Duration

var apiClient *d_client.Client

func main() {
	flag.StringVar(&flag_name, "project", "", "project name")
	flag.StringVar(&flag_files, "files", "", "docker-compose file(s). comma separated")
	flag.IntVar(&flag_timeout, "timeout", 600, "timeout in seconds")
	flag.Parse()
	if flag_name == "" || flag_files == "" {
		flag.Usage()
		log.Fatal("project and file are required")
	}

	name = flag_name
	timeout = time.Duration(flag_timeout) * time.Second
	files = append(files, strings.Split(flag_files, ",")...)

	var err error
	// Parse the docker-compose file
	p, err := createProjectWithNameFromFiles(name, files)
	if err != nil {
		log.Fatal(err)
	}

	// Create a client for docker
	apiClient, err = d_client.NewClientWithOpts(
		d_client.FromEnv, d_client.WithAPIVersionNegotiation(),
	)
	if err != nil {
		log.Fatal(err)
	}

	// Get the container list
	containers, err := getContainersFromProject(p.Name)
	if err != nil {
		log.Fatal(err)
	}

	checkResults := make(Results)
	checksCh := make(chan Result, len(containers))
	var wg sync.WaitGroup

	// Spin go routines to check each container
	for _, c := range containers {
		wg.Add(1)
		fmt.Printf("Watching [%s] ...\n", getContainerName(c.Names))
		go func(c d_types.Container) {
			defer wg.Done()
			checkContainer(c, checksCh)
		}(c)
	}

	// Spin go routine to close the channel when all go routines are done
	go func() {
		wg.Wait()
		close(checksCh)
	}()

	// Read from the channel
	for check := range checksCh {
		checkResults[check.Name] = check
	}

	unhealthy := 0

	// Print the results
	for name, res := range checkResults {
		fmt.Println(strings.Repeat("=", 50), name, strings.Repeat("=", 20))
		fmt.Printf("Container: %s\n", name)
		fmt.Printf("Healthy: %t\n", res.Healthy)
		fmt.Printf("Fatal: %t\n", res.Fatal)
		if res.Logs != "" {
			fmt.Printf("Logs: %s\n", res.Logs)
		} else {
			fmt.Println("Logs: No logs available")
		}
		if res.Fatal {
			unhealthy++
			if res.ProbeLogs != "" {
				fmt.Printf("Probe Logs: %s\n", res.ProbeLogs)
			}
		}
		fmt.Println(strings.Repeat("=", 100+len(name)))
	}

	fmt.Println("Summary:")
	fmt.Printf("Containers: %d\n", len(containers))
	fmt.Printf("Healthy: %d\n", len(containers)-unhealthy)
	fmt.Printf("Unhealthy: %d\n", unhealthy)
	if unhealthy > 0 {
		log.Fatal("Unhealthy containers")
	}
}

// Container names seem to have a leading slash
func getContainerName(n []string) string {
	return strings.TrimLeft(n[0], "/")
}
func checkContainer(c d_types.Container, checksCh chan Result) {
	start := time.Now()
	var res Result
	res.HasCheck, _ = hasHealthCheck(c.ID)
	res.Name = getContainerName(c.Names)
	running, _ := isRunning(c.ID)
	if !running {
		res.Fatal = true
		res.Logs, _ = getLogs(c.ID)
		res.ProbeLogs, _ = getFailedProbeLogs(c.ID)
		checksCh <- res
		return
	}

	var health string
	for {
		health, _ = getHealth(c.ID)

		if res.HasCheck && health == "healthy" {
			res.Healthy = true
			res.Logs, _ = getLogs(c.ID)
			checksCh <- res
			return
		}

		if !res.HasCheck && health == "running" {
			res.Healthy = true
			res.Logs, _ = getLogs(c.ID)
			checksCh <- res
			return
		}

		if time.Since(start) > timeout {
			res.Healthy = false
			res.Logs, _ = getLogs(c.ID)
			res.ProbeLogs, _ = getFailedProbeLogs(c.ID)
			checksCh <- res
			return
		}

		time.Sleep(2 * time.Second)
	}
}

// hasHealthCheck checks if the container has a health check
func hasHealthCheck(cID string) (bool, error) {
	container, err := apiClient.ContainerInspect(context.Background(), cID)
	if err != nil {
		return false, fmt.Errorf("failed to inspect container: %w", err)
	}

	if len(container.Config.Healthcheck.Test) > 0 {
		return true, nil
	}

	return false, nil
}

// isRunning returns true if the container is in the "running" state
func isRunning(cID string) (bool, error) {
	container, err := apiClient.ContainerInspect(context.Background(), cID)
	if err != nil {
		return false, fmt.Errorf("failed to inspect container: %w", err)
	}

	return container.State.Running, nil
}

// getHealth returns the health status of the container
func getHealth(cID string) (string, error) {
	container, err := apiClient.ContainerInspect(context.Background(), cID)
	if err != nil {
		return "", fmt.Errorf("failed to inspect container: %w", err)
	}

	return container.State.Health.Status, nil
}

// getFailedProbeLogs returns the logs of the failed probes
func getFailedProbeLogs(cID string) (string, error) {
	container, err := apiClient.ContainerInspect(context.Background(), cID)
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

// createProjectWithNameFromFiles creates a project from the given files and name
func createProjectWithNameFromFiles(name string, files []string) (*c_types.Project, error) {
	// Create the project options
	composeOpts, err := c_cli.NewProjectOptions(
		files, c_cli.WithName(name),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create project options: %w", err)
	}

	project, err := c_cli.ProjectFromOptions(composeOpts)
	if err != nil {
		return nil, fmt.Errorf("failed to create project: %w", err)
	}

	return project, nil
}

// getLogs returns the logs of the container
func getLogs(cID string) (string, error) {
	body, err := apiClient.ContainerLogs(context.Background(), cID,
		d_container.LogsOptions{
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

// getContainersFromProject returns the containers from the project
func getContainersFromProject(composeName string) ([]d_types.Container, error) {
	containers, err := apiClient.ContainerList(
		context.Background(),
		d_container.ListOptions{All: true, Filters: d_filters.NewArgs(
			d_filters.Arg("label", fmt.Sprintf("com.docker.compose.project=%s", composeName)),
		)},
	)

	if err != nil {
		return nil, fmt.Errorf("failed to list containers: %w", err)
	}

	return containers, nil
}
