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

var envName string
var l *log.Logger

func init() {
	l = log.New(os.Stderr, "", 0)
	flag.StringVar(&envName, "env-name", "CHANGED_FILES", "Environment variable to use for the changed files")
	flag.Parse()

	if envName == "" {
		l.Fatal("env-name is required")
	}
}

func main() {
	// Print to stderr, in order to keep stdout only for data
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
		l.Fatal("Failed to unmarshal json: ", err)
		return
	}

	for _, f := range files {
		// Only look for apps
		if !appRegex.MatchString(f) {
			continue
		}

		parts := strings.Split(f, "/")
		key := fmt.Sprintf("%s/%s", parts[1], parts[2])
		if _, ok := result[key]; !ok {
			result[key] = []string{}
		}
	}

	// All apps must have at least one CI values file
	for k := range result {
		// Read the app directory
		fs, err := os.ReadDir(fmt.Sprintf("ix-dev/%s/ci", k))
		if err != nil {
			l.Fatal("Failed to read dir: ", err)
		}

		// Iterate over the files
		for _, f := range fs {
			// Only look for .yaml files
			if !strings.HasSuffix(f.Name(), ".yaml") {
				continue
			}

			result[k] = append(result[k], f.Name())
		}

		if len(result[k]) == 0 {
			l.Fatalf(fmt.Sprintf("No CI values found for %s", k))
		}
	}

	// Marshal the result
	result_json, err := json.Marshal(result)
	if err != nil {
		l.Fatal("Failed to marshal result: ", err)
		return
	}

	// Print the result
	fmt.Println(string(result_json))
}
