# make is byzantine and obnoxious: https://stackoverflow.com/q/4122831/344821
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:
.PHONY: all clean clean-all

LATEXMK ?= latexmk
PYTHON ?= python

all: index.html biblio.bib cv.pdf ccv-info.txt

%: papers.yaml build.py templates/%
	$(PYTHON) build.py $@

biblio.bib: biblio-cv.bib
	sed -e '/author+an = /d; /addendum = /d' < $< > $@

cv.pdf: cv.tex biblio-cv.bib
	mkdir -p .cv-build
	ln -f cv.tex biblio-cv.bib .cv-build/
	cd .cv-build && $(LATEXMK) -pdf -silent cv
	ln -f .cv-build/cv.pdf .

clean:
	rm -rf .cv-build

clean-all: clean
	rm -f index.html biblio.bib biblio-cv.bib cv.pdf
