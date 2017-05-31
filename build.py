#!/usr/bin/env python
from __future__ import unicode_literals

import argparse
import io
import json
import re
import os

from staticjinja import make_site
from unidecode import unidecode


_dir = os.path.abspath(os.path.dirname(__file__))


def paper_data():
    with io.open(os.path.join(_dir, "papers.json")) as f:
        return json.load(f)



filters = {}
def filter(fn):
    filters[fn.__name__] = fn
    return fn

@filter
def venue_url(venue, year=None):
    if 'web_by_year' in venue and year in venue['web_by_year']:
        return venue['web_by_year'][year]
    elif 'web' in venue:
        return venue['web']
    return None

@filter
def get_author(author, coauthors):
    if author.endswith('*'):
        author = author[:-1]
    return coauthors[author]

translation_table = {}
@filter
def latex_escape(string):
    "Turn unicode accented characters into LaTeX escapes."
    # https://stackoverflow.com/a/4579006/344821
    global translation_table

    if not translation_table:
        p = re.compile(r'%.*\DeclareUnicodeCharacter\{(\w+)\}\{(.*)\}')
        with io.open('utf8ienc.dtx') as f:
            for line in f:
                m = p.match(line)
                if m:
                    codepoint, latex = m.groups()
                    latex = latex.replace('@tabacckludge', '')
                    translation_table[int(codepoint, 16)] = '{' + latex + '}'

    return string.translate(translation_table)

filters['unidecode'] = unidecode

@filter
def last_name(author_dict):
    if 'last_name' in author_dict:
        return author_dict['last_name']
    return author_dict['name'].split()[-1]

@filter
def bibtex_authors(authors, coauthors):
    return ' and '.join(
        latex_escape(get_author(a, coauthors)['name']) for a in authors)

@filter
def author_equal(author):
    return author.endswith('*')

@filter
def maybe_wrap(content, before, after):
    if content:
        return "{}{}{}".format(before, content, after)
    else:
        return ""

@filter
def maybe_link(content, url=None):
    if url:
        return "<a href={}>{}</a>".format(url, content)
    else:
        return content


def make_site():
    site = make_site(
        contexts=[('.*', paper_data)],
        filters=filters,
    )
    site._env.tests['falsey'] = lambda x: not x
    return site


def render(site, files=None, watch=False):
    if files:
        for file in files:
            site.render_template(site.get_template(file))
    else:
        site.render(use_reloader=watch)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', action='store_true', default=False)
    parser.add_argument('files', nargs='*')
    args = parser.parse_args()

    site = make_site()
    render(site, files=args.files, watch=args.watch)
