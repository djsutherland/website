.PHONY : FORCE_MAKE
# make is byzantine and obnoxious: https://stackoverflow.com/q/4122831/344821
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:

all: index.html biblio.bib cv.pdf

%: papers.json build.py templates/%
	python build.py $@

cv.pdf: cv.tex biblio.bib FORCE_MAKE
	cd cv-build && \
	ln -f ../cv.tex . && \
	latexmk -pdf cv && \
	ln -f cv.pdf ../cv.pdf
