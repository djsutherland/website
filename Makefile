# make is byzantine and obnoxious: https://stackoverflow.com/q/4122831/344821
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:
.PHONY: all tidy clean

LATEXMK ?= latexmk
PYTHON ?= python
OUTDIR ?= built

STATIC := $(notdir $(wildcard static/*))
TEMPLATE := $(notdir $(wildcard templates/*))
TEX := cv form100-contributions
OTHER := biblio.bib

STATIC_TARGETS := $(addprefix ${OUTDIR}/,${STATIC})
TEMPLATE_TARGETS := $(addprefix ${OUTDIR}/,${TEMPLATE})
TEX_TARGETS := $(addprefix ${OUTDIR}/,$(addsuffix .pdf,${TEX}))
OTHER_TARGETS := $(addprefix ${OUTDIR}/,${OTHER})
ALL_TARGETS := ${STATIC_TARGETS} ${TEMPLATE_TARGETS} ${TEX_TARGETS} ${OTHER_TARGETS}

all: ${ALL_TARGETS}

${STATIC_TARGETS}: ${OUTDIR}/%: static/%
	@mkdir -p ${OUTDIR}
	cp $< $@

${TEMPLATE_TARGETS}: ${OUTDIR}/%: templates/% papers.yaml
	@mkdir -p ${OUTDIR}
	$(PYTHON) build.py --output-path ${OUTDIR} $(notdir $@)

${OUTDIR}/cv.pdf: ${OUTDIR}/biblio-cv.bib
${OUTDIR}/form100-contributions.pdf: ${OUTDIR}/biblio-cv-subs.bib
${TEX_TARGETS}: ${OUTDIR}/%.pdf: ${OUTDIR}/%.tex
	mkdir -p .build/$(notdir $<)/
	ln -f $+ .build/$(notdir $<)/
	cd .build/$(notdir $<)/ && $(LATEXMK) -pdf -silent $(notdir $<)
	ln -f .build/$(notdir $<)/$(notdir $@) $@

${OUTDIR}/biblio.bib: ${OUTDIR}/biblio-cv.bib
	sed -e '/author+an = /d; /addendum = /d; /keywords = /d; /pubstate =/d; /arinfo =/d;' < $< > $@


tidy:
	rm -rf .build/

clean: tidy
	rm -f ${ALL_TARGETS}
