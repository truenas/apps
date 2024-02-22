package engine

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestBoolFuncs(t *testing.T) {
	type test struct {
		name    string
		input   interface{}
		want    bool
		wantErr bool
	}

	var tests []test = []test{
		{name: "BoolTrue", input: true, want: true, wantErr: false},
		{name: "BoolFalse", input: false, want: false, wantErr: false},
		{name: "StringTrue", input: "true", want: true, wantErr: false},
		{name: "StringYes", input: "yes", want: true, wantErr: false},
		{name: "StringFalse", input: "false", want: false, wantErr: false},
		{name: "StringNo", input: "no", want: false, wantErr: false},
		{name: "InvalidString", input: "invalid", want: false, wantErr: true},
		{name: "InvalidType", input: 123, want: false, wantErr: true},
	}

	e := &engine{}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := e.mustBoolFunc(tt.input)
			assert.Equal(t, tt.wantErr, err != nil, "mustBoolFunc() error = %v, wantErr %v", err, tt.wantErr)
			assert.Equal(t, tt.want, got, "mustBoolFunc() = %v, want %v", got, tt.want)

			got = e.boolFunc(tt.input)
			assert.Equal(t, tt.want, got, "boolFunc() = %v, want %v", got, tt.want)
		})
	}
}
