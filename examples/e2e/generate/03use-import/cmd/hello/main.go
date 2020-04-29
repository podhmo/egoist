package main
import (
	"flag"
	"fmt"
	"os"
	"log"
	"m/hello"
)

// this packaage is auto generated

// Option ...
type Option struct {
	Name string // for `-name`
}


func main()  {
	opt := &Option{}
	cmd := flag.NewFlagSet("hello", flag.ContinueOnError)
	cmd.Usage = func(){
		fmt.Fprintln(cmd.Output(), `hello - hello message`)
		cmd.PrintDefaults()
	}
	cmd.StringVar(&opt.Name, "name", "World", "-")

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
	hello.Hello(opt.Name)
	return nil
}