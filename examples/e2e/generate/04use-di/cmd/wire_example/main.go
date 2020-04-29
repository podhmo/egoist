package main
// this packaage is auto generated

import (
	"flag"
	"os"
	"log"
	"m/internal"
)

// Option ...
type Option struct {
	Grumby bool // for `-grumby`
}


func main()  {
	opt := &Option{}
	cmd := flag.NewFlagSet("wire_example", flag.ContinueOnError)

	cmd.BoolVar(&opt.Grumby, "grumby", false, "-")

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
	v0 := internal.NewMessage()
	v1 := internal.NewGreeter(v0, opt.Grumby)
	v2, err := internal.NewEvent(v1)
	if err != nil  {
		return err
	}
	v2.Start()
	return nil
}