# make is byzantine and obnoxious: https://stackoverflow.com/q/4122831/344821
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:
.PHONY: all tidy clean FORCE_MAKE

LATEXMK ?= latexmk
PYTHON ?= python
OUTDIR ?= built

STATIC := $(notdir $(wildcard static/*))
TEMPLATE := $(notdir $(wildcard templates/*))
TEX := 
UBC_CV_PARTS := $(notdir $(wildcard templates/ubc-cv-*.tex))
OTHER := biblio.bib ubc-cv.pdf ubc-cv-anno.pdf cv.pdf 

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

${TEX_TARGETS}: ${OUTDIR}/%.pdf: ${OUTDIR}/%.tex
	mkdir -p .build/$(notdir $<)/
	ln -f $+ .build/$(notdir $<)/
	$(LATEXMK) -cd -pdf -silent .build/$(notdir $<)/$(notdir $<)
	ln -f .build/$(notdir $<)/$(notdir $@) $@

$(addprefix ubc-cv/,${UBC_CV_PARTS}): ubc-cv/%.tex: ${OUTDIR}/%.tex
	ln -f $< $@
ubc-cv/biblio-cv.bib: ${OUTDIR}/biblio-cv.bib
	ln -f $< $@
ubc-cv/biblio-cv-subs.bib: ${OUTDIR}/biblio-cv-subs.bib
	ln -f $< $@
ubc-cv/ubc-cv.pdf ubc-cv/ubc-cv-anno.pdf ubc-cv/cv.pdf: ubc-cv/ubc-cv.tex $(addprefix ubc-cv/,${UBC_CV_PARTS}) ubc-cv/biblio-cv.bib FORCE_MAKE
	$(LATEXMK) -cd -pdf -silent -jobname=$(basename $(notdir $@)) $<
${OUTDIR}/ubc-cv.pdf ${OUTDIR}/ubc-cv-anno.pdf ${OUTDIR}/cv.pdf: ${OUTDIR}/%.pdf: ubc-cv/%.pdf
	ln -f $< $@

${OUTDIR}/biblio.bib: ${OUTDIR}/biblio-cv.bib
	sed -e '/author+an = /d; /addendum = /d; /keywords = /d; /pubstate =/d; /arinfo =/d;' < $< > $@

tidy:
	rm -rf .build/
	$(LATEXMK) -cd -silent -jobname=ubc-cv -c ubc-cv/ubc-cv.tex
	$(LATEXMK) -cd -silent -jobname=ubc-cv-anno -c ubc-cv/ubc-cv.tex
	$(LATEXMK) -cd -silent -jobname=cv -c ubc-cv/ubc-cv.tex
	rm -f $(addprefix ${OUTDIR}/,${UBC_CV_PARTS}) ubc-cv/biblio-cv.bib ubc-cv/*.bbl ubc-cv/*.run.xml ubc-cv/*.synctex*

clean: tidy
	rm -f ${ALL_TARGETS} ubc-cv/ubc-cv.pdf ubc-cv/ubc-cv-anno.pdf ubc-cv/cv.pdf
