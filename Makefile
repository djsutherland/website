# make is byzantine and obnoxious: https://stackoverflow.com/q/4122831/344821
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:
.PHONY: all ubc-cv clean clean-all

LATEXMK ?= latexmk
PYTHON ?= python

all: index.html biblio.bib cv.tex cv.pdf ccv-info.txt ubc-cv
ubc-cv: ubc-cv-invited-talks.tex ubc-cv-contributed-talks.tex

%: papers.yaml build.py templates/%
	$(PYTHON) build.py $@

biblio.bib: biblio-cv.bib
	sed -e '/author+an = /d; /addendum = /d; /keywords = /d;' < $< > $@

%.pdf: %.tex biblio-cv.bib
	mkdir -p .build/$</
	ln -f $+ .build/$</
	cd .build/$</ && $(LATEXMK) -pdf -silent $<
	ln -f .build/$</$@ .

tidy:
	rm -rf .build/

clean: tidy
	rm -f index.html biblio.bib biblio-cv.bib cv.tex cv.pdf ccv-info.txt
