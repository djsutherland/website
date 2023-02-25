# make is byzantine and obnoxious: https://stackoverflow.com/q/4122831/344821
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:
.PHONY: all tidy clean FORCE_MAKE

LATEXMK ?= latexmk
PYTHON ?= python
OUTDIR ?= built

STATIC := $(notdir $(wildcard static/*))
TEMPLATE := $(notdir $(wildcard templates/*))
TEX := cv form100-contributions form100a-contributions
UBC_CV_PARTS := $(notdir $(wildcard templates/ubc-cv-*.tex))
OTHER := biblio.bib ubc-cv.pdf

STATIC_TARGETS := $(addprefix ${OUTDIR}/,${STATIC})
TEMPLATE_TARGETS := $(addprefix ${OUTDIR}/,${TEMPLATE})
TEX_TARGETS := $(addprefix ${OUTDIR}/,$(addsuffix .pdf,${TEX}))
OTHER_TARGETS := $(addprefix ${OUTDIR}/,${OTHER})
ALL_TARGETS := ${STATIC_TARGETS} ${TEMPLATE_TARGETS} ${TEX_TARGETS} ${OTHER_TARGETS}

all: ${ALL_TARGETS}

${STATIC_TARGETS}: ${OUTDIR}/%: static/%
	@mkdir -p ${OUTDIR}
	cp $< $@

${OUTDIR}/biblio-cv-subs.bib: templates/biblio-cv.bib
${TEMPLATE_TARGETS}: ${OUTDIR}/%: templates/% papers.yaml build.py
	@mkdir -p ${OUTDIR}
	$(PYTHON) build.py --output-path ${OUTDIR} $(notdir $@)

${OUTDIR}/cv.pdf: ${OUTDIR}/biblio-cv.bib
${OUTDIR}/form100-contributions.pdf: ${OUTDIR}/biblio-cv-subs.bib
${OUTDIR}/form100a-contributions.pdf: ${OUTDIR}/biblio-cv-subs.bib
${TEX_TARGETS}: ${OUTDIR}/%.pdf: ${OUTDIR}/%.tex
	mkdir -p .build/$(notdir $<)/
	ln -f $+ .build/$(notdir $<)/
	cd .build/$(notdir $<)/ && $(LATEXMK) -pdf -silent $(notdir $<)
	ln -f .build/$(notdir $<)/$(notdir $@) $@

ubc-cv/ubc-cv.pdf: $(addprefix ${OUTDIR}/,${UBC_CV_PARTS}) ${OUTDIR}/biblio-cv.bib FORCE_MAKE
	ln -f $(addprefix ${OUTDIR}/,${UBC_CV_PARTS}) ${OUTDIR}/biblio-cv.bib ubc-cv/
	cd ubc-cv && $(LATEXMK) -pdf -silent ubc-cv
${OUTDIR}/ubc-cv.pdf: ubc-cv/ubc-cv.pdf
	ln -f $< $@

${OUTDIR}/biblio.bib: ${OUTDIR}/biblio-cv.bib
	sed -e '/author+an = /d; /addendum = /d; /keywords = /d; /pubstate =/d; /arinfo =/d;' < $< > $@

tidy:
	rm -rf .build/
	cd ubc-cv && $(LATEXMK) -silent -c ubc-cv
	rm -f $(addprefix ${OUTDIR}/,${UBC_CV_PARTS}) ubc-cv/biblio-cv.bib

clean: tidy
	rm -f ${ALL_TARGETS} ubc-cv/ubc-cv.pdf
