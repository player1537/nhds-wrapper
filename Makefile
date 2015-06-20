SHELL := /bin/bash
NHDS_BASE_URL := ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHDS
NHDS_RAW_TEXT_YEARS := $(shell echo 20{05..10})
NHDS_ZIP_FILE_YEARS := $(shell echo 19{96..99} 20{00..04})

DISEASES := 174:breast-cancer 611:lump-or-mass-in-breast 410:heart-disease \
            429:heart-failure 331:alzheimers 290:senile-dementia \
            29010:pre-senile-dementia 29011:dementia-with-delirium \
            296:bipolar 487:influenza
DISEASES_ICD9 := $(foreach disease,$(DISEASES),$(word 1,$(subst :, ,$(disease))))
DISEASES_NAME := $(foreach disease,$(DISEASES),$(word 2,$(subst :, ,$(disease))))

ICD9_BASE_URL := \
	https://www.cms.gov/Medicare/Coding/ICD9ProviderDiagnosticCodes/Downloads

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

download/icd9.dat:
	wget $(ICD9_BASE_URL)/ICD-9-CM-v32-master-descriptions.zip -O- | funzip > $@

gen/as_csv/%.csv: download/nhds/%.dat
	@mkdir -p $(dir $@)
	python -m nhds.parse_nhds \
	--strip-fields \
	--consolidate-date \
	--short-column-names \
	--estimate-count \
	--target 09 \
	$< > $@

define MATCH_IMS_DISEASE
gen/match_ims/$(1).txt: gen/as_csv/2009.csv gen/as_csv/2010.csv
	@mkdir -p $$(dir $$@)
	python -m nhds.match_ims $$^ --match-icd9 $(2) > $$@
endef

$(foreach disease,$(DISEASES), \
  $(eval $(call MATCH_IMS_DISEASE,$(word 2,$(subst :, ,$(disease))), \
                                  $(word 1,$(subst :, ,$(disease))))))

gen/match_ims.tar.gz: $(addprefix gen/match_ims/,$(DISEASES_NAME:=.txt))
	@mkdir -p $(dir $@)
	tar cf - $^ | gzip -c > $@

.PHONY: clean
clean:
	rm -f -- $(wildcard *~) $(wildcard **/*~) $(wildcard **/**/*~)
	rm -f -- $(wildcard *.pyc) $(wildcard **/*.pyc) $(wildcard **/**/*.pyc)
