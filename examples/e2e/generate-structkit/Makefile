export CHECK ?=
BUILD_FILE := ./x

default: 00 01 02 03 04 05 06 07 08 09 10 11 12
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

# list
04:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# map
05:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# more nested (BROKEN)
06:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# embedded
07:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# empty
08:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# enums
09:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# docstring
10:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# sum types (union)
11:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# with other packages
12:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

# more pointer ****x
13:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models


clean:
	rm -f ${BUILD_FILE}
