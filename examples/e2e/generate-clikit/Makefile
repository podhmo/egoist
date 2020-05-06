default: 00 01 02 03 04

00:
	$(MAKE) -C $(shell echo $@*/)
00-run:
	cd $(shell echo $(subst -run,,$@*/)) && go run cmd/hello/main.go -h

01:
	$(MAKE) -C $(shell echo $@*/)
01-run:
	cd $(shell echo $(subst -run,,$@*/)) && go run cmd/hello/main.go -h

02:
	$(MAKE) -C $(shell echo $@*/)
02-run:
	cd $(shell echo $(subst -run,,$@*/)) && go run cmd/hello/main.go -h

03:
	$(MAKE) -C $(shell echo $@*/)
03-run:
	cd $(shell echo $(subst -run,,$@*/)) && go run cmd/hello/main.go -h

04:
	$(MAKE) -C $(shell echo $@*/)
04-run:
	cd $(shell echo $(subst -run,,$@*/)) && go run cmd/wire_example/main.go
05:
	$(MAKE) -C $(shell echo $@*/)
05-run:
	cd $(shell echo $(subst -run,,$@*/)) && go run cmd/hello/main.go --name foo xxx yyy zzz
