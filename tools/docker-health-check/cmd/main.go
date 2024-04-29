package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"sync"
	"time"

	"ixsystems/docker-health-check/pkg/utils"

	"github.com/docker/docker/api/types"
)

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

	checkResults := make(utils.Results)
	checksCh := make(chan utils.Result, len(containers))
	var wg sync.WaitGroup

	// Spin go routines to check each container
	for _, c := range containers {
		wg.Add(1)
		fmt.Printf("Watching [%s] ...\n", normalizeContainerName(c.Names))
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

	unhealthyContainers := utils.LogResultsAndReturnUnhealthy(checkResults)
	if unhealthyContainers > 0 {
		fmt.Println("Found unhealthy containers")
		os.Exit(unhealthyContainers)
	}
}

// Container names seem to have a leading slash
func normalizeContainerName(n []string) string {
	return strings.TrimLeft(n[0], "/")
}

func checkContainerWithHealthCheck(c types.Container) (utils.Result, error) {
	start := time.Now()

	result := utils.Result{
		Name:     normalizeContainerName(c.Names),
		HasCheck: true,
	}

	var err error
	for {
		result.InspectData, err = utils.GetInspectData(c.ID)
		if err != nil {
			return result, err
		}

		result.ExitCode = utils.GetExitCode(result.InspectData)
		if utils.IsHealthy(result.InspectData) {
			handleHealthy(&c, &result)
			return result, nil
		}

		if time.Since(start) > timeout {
			handleTimeout(&c, &result)
			return result, nil
		}

		// Wait 2 seconds to avoid spamming
		time.Sleep(2 * time.Second)
	}
}

func checkContainerWithNoHealthCheck(c types.Container) (utils.Result, error) {
	start := time.Now()

	result := utils.Result{
		Name:     normalizeContainerName(c.Names),
		HasCheck: false,
	}

	var err error
	for {
		result.InspectData, err = utils.GetInspectData(c.ID)
		if err != nil {
			return result, err
		}

		result.ExitCode = utils.GetExitCode(result.InspectData)
		if utils.IsExited(result.InspectData) {
			if utils.IsZeroExitCode(result.InspectData) {
				handleHealthy(&c, &result)
				return result, nil
			}

			handleNonZeroExitCode(&c, &result)

			return result, nil
		}

		// TODO: For a container without health check that has no exited
		// we cannot really be sure if its a stuck init container or
		// just a container that should run for ever but missing a health check
		// For now we assume it is healthy
		if utils.IsRunning(result.InspectData) {
			result.Healthy = true
			result.Logs, _ = utils.GetLogs(c.ID)
			return result, nil
		}

		if time.Since(start) > timeout {
			result.Healthy = false
			result.Logs, _ = utils.GetLogs(c.ID)
			return result, nil
		}

		// Wait 2 seconds to avoid spamming
		time.Sleep(2 * time.Second)
	}
}

func checkContainer(c types.Container, checksCh chan utils.Result) {
	var result utils.Result

	container, _ := utils.GetInspectData(c.ID)
	hasCheck := utils.HasHealthCheck(container)

	if hasCheck {
		result, _ = checkContainerWithHealthCheck(c)
	} else {
		fmt.Printf("[WARN] Container [%s] has no health check\n", normalizeContainerName(c.Names))
		result, _ = checkContainerWithNoHealthCheck(c)
	}

	checksCh <- result
}

func handleNonZeroExitCode(c *types.Container, res *utils.Result) {
	fmt.Printf("Container [%s] has a non-zero [%d] exit code, will be marked unhealthy\n", c.ID, res.ExitCode)
	res.Healthy = false
	res.Logs, _ = utils.GetLogs(c.ID)
	res.Fatal = true
	if res.HasCheck {
		res.ProbeLogs, _ = utils.GetFailedProbeLogs(res.InspectData)
	}
}

func handleTimeout(c *types.Container, res *utils.Result) {
	fmt.Printf("Container [%s] has timed out, Container will be marked unhealthy\n", c.ID)
	res.Healthy = false
	res.TimedOut = true
	res.Logs, _ = utils.GetLogs(c.ID)
	res.ProbeLogs, _ = utils.GetFailedProbeLogs(res.InspectData)
}

func handleHealthy(c *types.Container, res *utils.Result) {
	fmt.Printf("Container [%s] is marked healthy\n", c.ID)
	res.Healthy = true
	res.Logs, _ = utils.GetLogs(c.ID)
}
