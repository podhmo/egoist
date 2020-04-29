package main
import (
	"flag"
	"fmt"
	"time"
	"os"
	"log"
)

// this package is generated by egoist.generate.clikit

// Option ...
type Option struct {
	Name string // for `-name`
	Age uint // for `-age`
	Debug bool // for `-debug`
	Dur time.Duration // for `-dur`
}


func main()  {
	opt := &Option{}
	cmd := flag.NewFlagSet("hello", flag.ContinueOnError)
	cmd.Usage = func(){
		fmt.Fprintln(cmd.Output(), `hello - hello message`)
		fmt.Fprintln(cmd.Output(), "")
		fmt.Fprintln(cmd.Output(), "Usage:")
		cmd.PrintDefaults()
	}
	cmd.StringVar(&opt.Name, "name", "world", "-")
	cmd.UintVar(&opt.Age, "age", 0, "-")
	cmd.BoolVar(&opt.Debug, "debug", false, "-")
	cmd.DurationVar(&opt.Dur, "dur", 0*time.Second, "-")

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