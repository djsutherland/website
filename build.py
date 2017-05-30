#!/usr/bin/env python
import argparse
import json
import os

from staticjinja import make_site


_dir = os.path.abspath(os.path.dirname(__file__))


def paper_data():
    with open(os.path.join(_dir, "papers.json")) as f:
        return json.load(f)

def venue_url(venue, year=None):
    if 'web_by_year' in venue and year in venue['web_by_year']:
        return venue['web_by_year'][year]
    elif 'web' in venue:
        return venue['web']
    return None

def maybe_link(content, url=None):
    if url:
        return "<a href={}>{}</a>".format(url, content)
    else:
        return content

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', action='store_true', default=False)
    args = parser.parse_args()


    site = make_site(
        contexts=[('index.html', paper_data)],
        filters={
            'venue_url': venue_url,
            'maybe_link': maybe_link,
        },
    )
    site.render(use_reloader=args.watch)
