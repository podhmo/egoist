export CHECK ?=
BUILD_FILE := ./x

default: 00 01 02 03
strict:
	CHECK=1 $(MAKE)

# simple
00:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# handling metadata, `yaml:"<field>" json:"<field>"`
01:
	$(MAKE) -C $(shell echo $@*/)
	diff --label 00/models.go --label 01/models.go -u $(shell echo 00*/models/models.go) $(shell echo $@*/models/models.go) > $(shell echo $@*/)/00to$@.diff || exit 0
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# object
02:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# recursion
03:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models


clean:
	rm -f ${BUILD_FILE}
