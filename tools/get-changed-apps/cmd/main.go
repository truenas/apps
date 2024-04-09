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

type Result []string

// ix-dev/{train}/{app}
var appRegex = regexp.MustCompile(`^ix-dev\/(.+)\/(.+)`)

var envName string
var l *log.Logger

func init() {
	// Print to stderr, in order to keep stdout only for data
	l = log.New(os.Stderr, "", 0)
	flag.StringVar(&envName, "env-name", "CHANGED_FILES", "Environment variable to use for the changed files")
	flag.Parse()

	if envName == "" {
		l.Fatal("env-name is required")
	}
}

func main() {
	// Get the changed files (json formatted)
	json_files := os.Getenv(envName)
	if json_files == "" {
		l.Printf("Environment variable %s is empty", envName)
		return
	}
	// Remove escaped backslashes coming from shell
	json_files = strings.ReplaceAll(json_files, "\\", "")
	l.Printf("Changed files: %s\n\n", json_files)

	// Parse the json
	var files []string
	if err := json.Unmarshal([]byte(json_files), &files); err != nil {
		l.Fatal("Failed to unmarshal json: ", err)
		return
	}

	// Get the changed apps
	result := getChangedApps(files)
	l.Printf("Result: %+v\n\n", result)

	// Marshal the result
	result_json, err := json.Marshal(result)
	if err != nil {
		l.Fatal("Failed to marshal result: ", err)
		return
	}

	// Print the result
	fmt.Println(string(result_json))
}

func getChangedApps(files []string) Result {
	result := Result{}

	tracker := make(map[string]struct{})

	for _, f := range files {
		// Only look for apps
		if !appRegex.MatchString(f) {
			continue
		}

		parts := strings.Split(f, "/")
		path := fmt.Sprintf("%s/%s", parts[1], parts[2])

		if _, ok := tracker[path]; ok {
			continue
		}

		result = append(result, path)
		tracker[path] = struct{}{}
	}

	return result
}
