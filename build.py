#!/usr/bin/env python
from __future__ import unicode_literals

import argparse
import io
import json
import os

from staticjinja import make_site


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

@filter
def last_name(author_dict):
    if 'last_name' in author_dict:
        return author_dict['last_name']
    return author_dict['name'].split()[-1]

@filter
def bibtex_authors(authors, coauthors):
    return ' and '.join(
        get_author(a, coauthors)['name'] for a in authors)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', action='store_true', default=False)
    parser.add_argument('files', nargs='*')
    args = parser.parse_args()

    site = make_site(
        contexts=[('.*', paper_data)],
        filters=filters,
    )
    site._env.tests['falsey'] = lambda x: not x
    if args.files:
        for file in args.files:
            site.render_template(site.get_template(file))
    else:
        site.render(use_reloader=args.watch)
