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
func checkContainer(c types.Container, checksCh chan utils.Result) {
	start := time.Now()
	var res utils.Result
	res.Name = normalizeContainerName(c.Names)

	res.HasCheck, _ = utils.HasHealthCheck(c.ID)
	if !res.HasCheck { // If there is no HC, and container exited with 0, mark it healthy
		fmt.Printf("[WARN] Container [%s] has no health check\n", res.Name)
		exited, _ := utils.IsExited(c.ID)
		exitCode, _ := utils.GetExitCode(c.ID)
		if exited {
			if exitCode == 0 {
				fmt.Printf("Container [%s] has exited with a zero exit code, will be marked healthy\n", res.Name)
				res.Healthy = true
				res.Logs, _ = utils.GetLogs(c.ID)
				res.InspectData, _ = utils.GetInspectData(c.ID)
				checksCh <- res
				return
			} else {
				fmt.Printf("Container [%s] has exited with a non-zero exit code, will be marked unhealthy\n", res.Name)
				res.Healthy = false
				res.Logs, _ = utils.GetLogs(c.ID)
				res.InspectData, _ = utils.GetInspectData(c.ID)
				res.Fatal = true
				res.ExitCode = exitCode
				checksCh <- res
				return
			}
		}
	}

	running, _ := utils.IsRunning(c.ID)
	if !running {
		exitCode, _ := utils.GetExitCode(c.ID)
		if res.ExitCode != 0 {
			fmt.Printf("Container [%s] is not running and has a non-zero exit code, will be marked unhealthy\n", res.Name)
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
		} else if !res.HasCheck {
			fmt.Printf("Container [%s] is not running and has no health check, will be marked healthy\n", res.Name)
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
		count := 10
		// There are cases where health is empty initially, so check a few times
		for health == "" && count > 0 {
			fmt.Printf("Container [%s] has an empty health state\n", res.Name)
			health, _ = utils.GetHealth(c.ID)
			time.Sleep(2 * time.Second)
			count--
		}
		if health == "running" {
			res.Healthy = true
			res.Logs, _ = utils.GetLogs(c.ID)
			checksCh <- res
			return
		} else if health == "" {
			// Ignore this case for now
			fmt.Printf("Container [%s] has no health check and has an empty health state, Doing nothing\n", res.Name)
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
			fmt.Printf("Container [%s] has timed out, Container will be marked unhealthy\n", res.Name)
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
