package gofmtrpc

import (
	"go/format"
	"io/ioutil"
	"log"
	"os"

	"github.com/semrush/zenrpc"
)

//go:generate go run github.com/semrush/zenrpc/zenrpc

type GofmtService struct{ zenrpc.Service }

func (s GofmtService) Format(code string) (string, error) {
	b, err := format.Source([]byte(code))
	if err != nil {
		return "", zenrpc.NewError(401, err)
	}
	return string(b), nil
}

// todo: performance tuning

//zenrpc:output=""
func (s GofmtService) FormatFile(input string, output string) (string, error) {
	if output == "" {
		output = input
	}
	log.Printf("format %s -> %s", input, output)

	f, err := os.Open(input)
	if err != nil {
		return "", zenrpc.NewError(401, err)
	}
	defer f.Close()

	code, err := ioutil.ReadAll(f)
	if err != nil {
		return "", zenrpc.NewError(401, err)
	}
	b, err := format.Source(code)
	if err != nil {
		return "", zenrpc.NewError(401, err)
	}

	// todo: use tempfile
	if err := ioutil.WriteFile(output, b, 0744); err != nil {
		return "", zenrpc.NewError(401, err)
	}
	return output, nil
}
