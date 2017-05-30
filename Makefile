all: index.html biblio.bib

%: papers.json build.py templates/%
	python build.py $@
