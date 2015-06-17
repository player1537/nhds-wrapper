SHELL := /bin/bash
NHDS_BASE_URL := ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS
NHDS_RAW_TEXT_YEARS := $(shell echo 20{05..10})
NHDS_ZIP_FILE_YEARS := $(shell echo 19{96..99} 20{00..04})

.PHONY: print-%
print-%: ; @echo $*=$($*)

.PRECIOUS: download/nhds/%

# Example: download/nhds/2009.dat
$(addprefix download/nhds/,$(NHDS_RAW_TEXT_YEARS:=.dat)):
	@mkdir -p $(dir $@)
	date=$@; \
	date=$${date#download/nhds/??}; \
	date=$${date%.dat}; \
	wget $(NHDS_BASE_URL)/nhds$${date}/NHDS$${date}.PU.TXT -O- > $@

# Example: download/nhds/2001.dat
$(addprefix download/nhds/,$(NHDS_ZIP_FILE_YEARS:=.dat)):
	@mkdir -p $(dir $@)
	date=$@; \
	date=$${date#download/nhds/??}; \
	date=$${date%.dat}; \
	wget $(NHDS_BASE_URL)/nhds$${date}/NHDS$${date}PU.zip -O- | \
	funzip > $@

.PHONY: clean
clean:
	rm -f -- $(wildcard *~) $(wildcard **/*~) $(wildcard **/**/*~)
	rm -f -- $(wildcard *.pyc) $(wildcard **/*.pyc) $(wildcard **/**/*.pyc)
