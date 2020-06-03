package gofmtrpc

import (
	"log"
	"net/http"
	"os"

	"github.com/semrush/zenrpc"
)

func Run(addr string) error {
	rpc := zenrpc.NewServer(zenrpc.Options{ExposeSMD: true})
	rpc.Register("", GofmtService{}) // public
	rpc.Use(zenrpc.Logger(log.New(os.Stderr, "", log.LstdFlags)))

	http.Handle("/", rpc)

	log.Printf("starting gofmtsrv on %s", addr)
	return http.ListenAndServe(addr, nil)
}
