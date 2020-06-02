package gofmtrpc

import (
	"go/format"

	"github.com/k0kubun/pp"
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
