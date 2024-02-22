package engine

import (
	"bytes"
	"fmt"
	"text/template"

	"github.com/truenas/go-template-compose/internal/types"
)

const (
	// The name of the base template (entrypoint for the template engine)
	baseTemplateName = "docker-compose.yaml.tmpl"
)

// Engine is an implementation of a template engine.
type engine struct {
	// Contains the custom error signaled from the template by an app developer.
	CustomError string
	// A list of warnings encountered during rendering.
	Warnings []string
	// The glob pattern to use when parsing templates.
	TemplatesDir string
	// The base template where everything is attached to (eg funcs, other templates, options)
	BaseTemplate *template.Template
	// A map for parsed templates. Its used to execute specific templates by name. (See includeFunc in funcs.go)
	Templates map[string]*template.Template
	// A map to keep track of included template names. Used to prevent infinite recursion.
	IncludedNames map[string]int
}

// New creates a new instance of Engine.
func New(tmplDir string) (engine, error) {
	if tmplDir == "" {
		return engine{}, fmt.Errorf("error no template directory provided")
	}

	return engine{
		Warnings:      []string{},
		Templates:     make(map[string]*template.Template),
		IncludedNames: make(map[string]int),
		TemplatesDir:  tmplDir,
		BaseTemplate:  template.New("ix-template"),
	}, nil
}

// Render takes a TemplateContext and returns the rendered template.
func (e *engine) Render(data types.TemplateContext) (rendered bytes.Buffer, err error) {
	e.setOpts()
	e.initFuncMap()

	if err := e.ParseGlob(); err != nil {
		return bytes.Buffer{}, fmt.Errorf("error parsing glob: %w", err)
	}

	if err := e.RegisterTemplates(); err != nil {
		return bytes.Buffer{}, fmt.Errorf("error registering templates: %w", err)
	}

	if _, ok := e.Templates[baseTemplateName]; !ok {
		return bytes.Buffer{}, fmt.Errorf("error finding base template: %s", baseTemplateName)
	}

	buf := bytes.Buffer{}
	if err := e.BaseTemplate.ExecuteTemplate(&buf, baseTemplateName, data); err != nil {
		return bytes.Buffer{}, fmt.Errorf("error executing base template: %w", err)
	}

	return buf, nil
}

// initFuncMap creates the Engine's FuncMap and adds context-specific functions.
func (e *engine) initFuncMap() {
	e.BaseTemplate.Funcs(funcMap(e))
}

// setOpts sets the options for the template.
func (e *engine) setOpts() {
	e.BaseTemplate.Option("missingkey=error")
}

// ParseGlob parses the glob pattern and adds the templates to the engine.
func (e *engine) ParseGlob() error {
	_, err := e.BaseTemplate.ParseGlob(e.TemplatesDir + "/*.tmpl")
	if err != nil {
		return err
	}

	return nil
}

// RegisterTemplates registers the templates to the engine.
func (e *engine) RegisterTemplates() error {
	// Populate the templates map, and check for duplicates
	for _, t := range e.BaseTemplate.Templates() {
		if _, ok := e.Templates[t.Name()]; ok {
			return fmt.Errorf("error duplicate template: %s", t.Name())
		}

		e.Templates[t.Name()] = t
	}

	return nil
}
