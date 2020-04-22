package main
// this packaage is auto generated

import (
	"fmt"
	"flag"
	"os"
	"log"
)

type Option struct {
	Name string
	Age uint
	Debug bool
}


func main()  {
	opt := &Option{}
	cmd := flag.NewFlagSet("hello", flag.ContinueOnError)

	cmd.StringVar(&opt.Name, "name", "world", "-")
	cmd.UintVar(&opt.Age, "age", 0, "-")
	cmd.BoolVar(&opt.Debug, "debug", false, "-")

	if err := cmd.Parse(os.Args[1:]); err != nil {
		if err != flag.ErrHelp {
			cmd.Usage()
		}
		os.Exit(1)
	}
	if err := run(opt); err != nil {
		log.Fatalf("!!%+v", err)
	}
}

func run(opt *Option) error {
	fmt.Printf("hello %s(%d)\n", opt.Name, opt.Age)
	return nil
}