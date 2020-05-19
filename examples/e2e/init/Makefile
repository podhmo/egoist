default: 00 01 02 03 04 05

00:
	cd $(shell echo $@*/) && rm -rf * && egoist init
01:
	cd $(shell echo $@*/) && rm -rf * && egoist init structkit
02:
	cd $(shell echo $@*/) && rm -rf * && egoist init filekit
03:
	cd $(shell echo $@*/) && rm -rf * && egoist init dirkit
04:
	cd $(shell echo $@*/) && egoist init new-command --name=foo
05:
	cd $(shell echo $@*/) && egoist init new-directive --name=foo
