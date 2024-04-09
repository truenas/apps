package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"regexp"
	"strings"
)

type Apps map[string][]string

// ix-dev/{train}/{app}
var appRegex = regexp.MustCompile(`^ix-dev\/(.+)\/(.+)`)

// ix-dev/{train}/{app}/ci/{app}.yaml
var ciValRegex = regexp.MustCompile(`^ix-dev\/(.+)\/(.+)\/ci\/(.+)\.yaml$`)

var envName string

func main() {
	flag.StringVar(&envName, "env-name", "CHANGED_FILES", "Environment variable to use for the changed files")
	flag.Parse()

	if envName == "" {
		log.Fatal("env-name is required")
	}

	// Print to stderr, in order to keep stdout only for data
	l := log.New(os.Stderr, "", 0)
	result := make(Apps)

	// Get the changed files (json formatted)
	json_files := os.Getenv(envName)
	if json_files == "" {
		l.Printf("Environment variable %s is empty", envName)
		return
	}

	// Parse the json
	var files []string
	if err := json.Unmarshal([]byte(json_files), &files); err != nil {
		log.Fatal("Failed to unmarshal json: ", err)
		return
	}

	for _, f := range files {
		// Only look for apps
		if !appRegex.MatchString(f) {
			continue
		}

		train := strings.Split(f, "/")[1]
		app := strings.Split(f, "/")[2]

		key := fmt.Sprintf("%s/%s", train, app)
		if _, ok := result[key]; !ok {
			result[key] = []string{}
		}

		// Get the CI values
		if ciValRegex.MatchString(f) {
			result[key] = append(result[key], strings.Split(f, "/")[4])
			continue
		}
	}

	// All apps must have at least one CI values file
	for k, v := range result {
		if len(v) == 0 {
			log.Fatal(fmt.Sprintf("No CI values found for %s", k))
		}
	}

	// Marshal the result
	result_json, err := json.Marshal(result)
	if err != nil {
		log.Fatal("Failed to marshal result: ", err)
		return
	}

	// Print the result
	fmt.Println(string(result_json))
}
