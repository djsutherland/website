My homepage.

The main interesting bit is how it generates a website / bib file / CV with Jinja templates from [a YAML file](papers.yaml) containing paper info. Feel free to steal ideas; this repository, _except for `photo.jpg` and contents under `ubc-cv/`_,  is public domain under the Unlicense.

Requirements:

- The python packages listed in [`requirements.txt`](requirements.txt) (`pip install -r requirements.txt`).
- A working `git` command line.
- A LaTeX installation, including `latexmk` and the standard base system.
