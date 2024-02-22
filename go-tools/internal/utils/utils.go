package utils

import (
	"bytes"
	"strings"
)

func ReplaceTabsWithSpaces(buf *bytes.Buffer, spaceCount int) {
	// Create a new buffer with the modified content
	// and re-assign it to the original buffer
	buf = bytes.NewBuffer(bytes.ReplaceAll(
		buf.Bytes(),
		[]byte("\t"),
		[]byte(strings.Repeat(" ", spaceCount)),
	))
}
