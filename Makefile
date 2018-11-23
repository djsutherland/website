# make is byzantine and obnoxious: https://stackoverflow.com/q/4122831/344821
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:
.PHONY: all clean clean-all

LATEXMK ?= latexmk
PYTHON ?= python

all: index.html biblio.bib cv.pdf pub-list.pdf

%: papers.yaml build.py templates/%
	$(PYTHON) build.py $@

biblio.bib: biblio-cv.bib
	sed -e '/author+an = /d; /addendum = /d' < $< > $@

cv.pdf: cv.tex biblio-cv.bib
	mkdir -p .cv-build
	ln -f cv.tex .cv-build/
	cd .cv-build && $(LATEXMK) -pdf cv
	ln -f .cv-build/cv.pdf .

pub-list.pdf: pub-list.tex biblio-cv.bib
	mkdir -p .publist-build
	ln -f pub-list.tex .publist-build/
	cd .publist-build && $(LATEXMK) -pdf pub-list
	ln -f .publist-build/pub-list.pdf .

clean:
	rm -rf .cv-build .publist-build

clean-all: clean
	rm -f index.html biblio.bib biblio-cv.bib cv.pdf pub-list.pdf
