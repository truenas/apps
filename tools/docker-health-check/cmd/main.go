package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"strings"
	"sync"
	"time"

	"ixsystems/docker-health-check/pkg/utils"

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

var flag_name string
var flag_files string
var flag_timeout int

var name string
var files []string
var timeout time.Duration

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
	p, err := utils.CreateProjectWithNameFromFiles(name, files)
	if err != nil {
		log.Fatal(err)
	}

	if err != nil {
		log.Fatal(err)
	}

	// Get the container list
	containers, err := utils.GetContainersFromProject(p.Name)
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
		go func(c types.Container) {
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

		if !res.Healthy {
			unhealthy++
			if res.Fatal {
				fmt.Printf("Exit Code: %d\n", res.ExitCode)
				if res.ProbeLogs != "" {
					fmt.Printf("Probe Logs: %s\n", res.ProbeLogs)
				}
			}

			data, _ := json.MarshalIndent(res.InspectData, "", "  ")
			fmt.Printf("Inspect Data: %s\n", string(data))
		}

		fmt.Printf("%s\n\n", strings.Repeat("=", 100+len(name)))
	}

	fmt.Println("Summary:")
	fmt.Printf("Containers: %d\n", len(containers))
	fmt.Printf("Healthy: %d\n", len(containers)-unhealthy)
	fmt.Printf("Unhealthy: %d\n", unhealthy)
	if unhealthy > 0 {
		log.Fatal("\nUnhealthy containers\n")
	}
}

// Container names seem to have a leading slash
func getContainerName(n []string) string {
	return strings.TrimLeft(n[0], "/")
}
func checkContainer(c types.Container, checksCh chan Result) {
	start := time.Now()
	var res Result
	res.HasCheck, _ = utils.HasHealthCheck(c.ID)
	res.Name = getContainerName(c.Names)
	running, _ := utils.IsRunning(c.ID)
	exitCode, _ := utils.GetExitCode(c.ID)

	// If its not running,
	if !running {
		if res.ExitCode != 0 {
			res.Healthy = false
			res.Logs, _ = utils.GetLogs(c.ID)
			res.InspectData, _ = utils.GetInspectData(c.ID)
			res.Fatal = true
			res.ExitCode = exitCode
			if res.HasCheck {
				res.ProbeLogs, _ = utils.GetFailedProbeLogs(c.ID)
			}
			checksCh <- res
			return
		} else {
			// This case is for example an "init" container
			// that started, did a job and exited. eg permission fix
			res.Healthy = true
			res.Logs, _ = utils.GetLogs(c.ID)
			res.InspectData, _ = utils.GetInspectData(c.ID)
			checksCh <- res
			return
		}
	}

	// If its running, and does not have a health check
	// assume it is healthy and stop checking
	health, _ := utils.GetHealth(c.ID)
	if !res.HasCheck {
		if health == "running" {
			res.Healthy = true
			res.Logs, _ = utils.GetLogs(c.ID)
			checksCh <- res
			return
		} else {
			// Log any other states so we can see how to handle them
			fmt.Printf("Container [%s] has a health state of [%s]\n", res.Name, health)
			res.Healthy = false
			res.ExitCode, _ = utils.GetExitCode(c.ID)
			res.Logs, _ = utils.GetLogs(c.ID)
			res.InspectData, _ = utils.GetInspectData(c.ID)
			checksCh <- res
			return
		}
	}

	// If its running and has a health check, keep checking
	// until it is healthy or timeout is reached
	for {
		health, _ = utils.GetHealth(c.ID)

		// If its healthy, stop checking
		if health == "healthy" {
			res.Healthy = true
			res.Logs, _ = utils.GetLogs(c.ID)
			checksCh <- res
			return
		}

		// Stop after the timeout is reached
		if time.Since(start) > timeout {
			res.Healthy = false
			res.TimedOut = true
			res.Logs, _ = utils.GetLogs(c.ID)
			res.ProbeLogs, _ = utils.GetFailedProbeLogs(c.ID)
			res.InspectData, _ = utils.GetInspectData(c.ID)
			checksCh <- res
			return
		}

		// Sleep for 2 seconds to avoid spamming the API
		time.Sleep(2 * time.Second)
	}
}
