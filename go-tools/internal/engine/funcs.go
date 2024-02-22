package engine

import (
	"bytes"
	"fmt"
	"strings"
	"text/template"

	"github.com/Masterminds/sprig/v3"
)

const (
	// Max number of times a template can include itself
	maxIncludedRecursion = 100
)

// funcMap returns a map of functions that are available to templates.
// the engine is passed to the functions so they can access the errors and warnings
// and potentially other engine state in the future.
func funcMap(e *engine) template.FuncMap {
	// TODO: sprig is unmaintained for a while, but it has a lot of useful functions
	// that Helm uses too. We can copy the functions we need from it and remove
	// the dependency. This will also allow us to fix or improve some of the functions
	funcMap := sprig.TxtFuncMap()

	// Add some extra functionality
	extra := template.FuncMap{
		"error":    e.errorFunc,
		"warn":     e.warnFunc,
		"include":  e.includeFunc,
		"mustBool": e.mustBoolFunc,
		"bool":     e.boolFunc,
	}

	for k, v := range extra {
		funcMap[k] = v
	}

	return funcMap
}

// error appends a message to the list of errors and stops the template execution.
func (e *engine) errorFunc(message string) (string, error) {
	e.CustomError = message
	return "", fmt.Errorf(message)
}

// warn appends a message to the list of warnings.
func (e *engine) warnFunc(message string) string {
	e.Warnings = append(e.Warnings, message)
	return ""
}

// includeFunc takes a template name and data, and returns the rendered template.
func (e *engine) includeFunc(name string, data interface{}) (string, error) {
	// Every time this function runs, we increment the include count
	// If we hit this point multiple times, we have a recursion. Some amount
	// is allowed, but not too much to avoid infinite loops.

	// The cases we can hit this is when we are
	// Executing a template that includes it self or its parent.
	if v, ok := e.IncludedNames[name]; ok {
		if v > maxIncludedRecursion {
			return "", fmt.Errorf("error max recursion limit (%d) reached for template: %s", maxIncludedRecursion, name)
		}
		e.IncludedNames[name]++
	} else {
		e.IncludedNames[name] = 1
	}

	if e.Templates[name] == nil {
		return "", fmt.Errorf("error template not found: %s", name)
	}

	// Create a buffer to write the template into.
	var buf bytes.Buffer

	// Execute the template with the provided data.
	err := e.Templates[name].Execute(&buf, data)

	// Always decrement the before returning after executing the each template
	// So when include is used in a non-recursing manner it won't error out
	e.IncludedNames[name]--

	if err != nil {
		return "", err
	}

	return strings.TrimSpace(buf.String()), nil
}

// mustBoolFunc converts a value to a boolean and returns an error if it fails.
func (e *engine) mustBoolFunc(b interface{}) (bool, error) {
	switch b := b.(type) {
	case bool:
		return b, nil
	case string:
		switch b {
		case "true", "yes":
			return true, nil
		case "false", "no":
			return false, nil
		default:
			return false, fmt.Errorf("error converting string value (%s) to boolean", b)
		}
	default:
		return false, fmt.Errorf("error converting value of type (%T) to boolean: %v", b, b)
	}
}

// boolFunc converts a value to a boolean and ignores any errors.
func (e *engine) boolFunc(b interface{}) bool {
	r, _ := e.mustBoolFunc(b)
	return r
}

// TODO:

// func fromTOML(str string) map[string]interface{} {
// 	m := make(map[string]interface{})

// 	if err := toml.Unmarshal([]byte(str), &m); err != nil {
// 		m["Error"] = err.Error()
// 	}
// 	return m
// }

// func toTOML(v interface{}) string {
// 	b := bytes.NewBuffer(nil)
// 	e := toml.NewEncoder(b)
// 	err := e.Encode(v)
// 	if err != nil {
// 		return err.Error()
// 	}
// 	return b.String()
// }

// func fromJSON(str string) map[string]interface{} {
// 	m := make(map[string]interface{})

// 	if err := json.Unmarshal([]byte(str), &m); err != nil {
// 		m["Error"] = err.Error()
// 	}
// 	return m
// }

// func toJSON(v interface{}) string {
// 	b, err := json.Marshal(v)
// 	if err != nil {
// 		return err.Error()
// 	}
// 	return string(b)
// }

// func fromYAML(str string) map[string]interface{} {
// 	m := make(map[string]interface{})
// 	if err := yaml.Unmarshal([]byte(str), &m); err != nil {
// 		m["Error"] = err.Error()
// 	}
// 	return m
// }

// func toYAML(v interface{}) string {
// 	data, err := yaml.Marshal(v)
// 	if err != nil {
// 		// Swallow errors inside of a template.
// 		return ""
// 	}
// 	return strings.TrimSuffix(string(data), "\n")
// }
