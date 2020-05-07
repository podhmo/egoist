default: 00 01

00:
	$(MAKE) -C $(shell echo $@*/)
01:
	$(MAKE) -C $(shell echo $@*/)
	diff --label 00/models.go --label 01/models.go -u $(shell echo 00*/models/models.go) $(shell echo $@*/models/models.go) > $(shell echo $@*/)/00to$@.diff || exit 0
