package types

type TemplateContext struct {
	// Application metadata such as name, version, etc
	AppCtx AppContext
	// User configuration values
	Values interface{}
}

func NewTemplateContext(p Payload, toolVersion string) TemplateContext {
	tCtx := TemplateContext{
		AppCtx: p.AppCtx,
		Values: p.Values,
	}

	tCtx.AppCtx.System.ToolVersion = toolVersion

	return tCtx
}
