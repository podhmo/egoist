export BUILD_CHECK ?=
BUILD_FILE := ./x

default: 00 01 02
strict:
	BUILD_CHECK=1 $(MAKE)

00:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${BUILD_CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

01:
	$(MAKE) -C $(shell echo $@*/)
	diff --label 00/models.go --label 01/models.go -u $(shell echo 00*/models/models.go) $(shell echo $@*/models/models.go) > $(shell echo $@*/)/00to$@.diff || exit 0
	test -z "${BUILD_CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

02:
	$(MAKE) -C $(shell echo $@*/)
	test -z "${BUILD_CHECK}" || go build -o ${BUILD_FILE} ./$(shell echo $@*/)models

clean:
	rm -f ${BUILD_FILE}
