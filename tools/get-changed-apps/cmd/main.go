package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/fs"
	"log"
	"os"
	"regexp"
	"strings"
)

type App struct {
	Path  string   `json:"path"`
	Files []string `json:"files"`
}

type Result []App

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

	// Github's matrix want the result under an "include" key
	matrix := map[string]Result{
		"include": result,
	}

	// Marshal the result
	result_json, err := json.Marshal(matrix)
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

		result = append(result, App{
			Path:  path,
			Files: getValuesFiles(fmt.Sprintf("ix-dev/%s/ci", path)),
		})
		tracker[path] = struct{}{}
	}

	return result
}

func getValuesFiles(path string) []string {
	var result []string

	fs, err := os.ReadDir(path)
	if err != nil {
		l.Fatal("Failed to read dir: ", err)
	}

	result = getYamlFiles(fs)

	if len(result) == 0 {
		l.Fatalf(fmt.Sprintf("No CI values found for %s", path))
	}

	return result
}

func getYamlFiles(fs []fs.DirEntry) []string {
	var result []string
	for _, f := range fs {
		// Only look for .yaml files
		if !strings.HasSuffix(f.Name(), ".yaml") {
			continue
		}
		result = append(result, f.Name())
	}

	return result
}
