#!/usr/bin/env python
from __future__ import unicode_literals

import argparse
import collections
from copy import copy
import datetime
import heapq
import io
import itertools
import json
import os
import re
import subprocess

from ruamel.yaml import YAML
import six
import staticjinja
from unidecode import unidecode


_dir = os.path.abspath(os.path.dirname(__file__))
today = datetime.date.today()
this_year = today.year


class MergedSequencesLookup(object):
    def __init__(self):
        self.seqs = collections.defaultdict(list)
        self.counter = iter(itertools.count())

    def __getitem__(self, keys):
        assert not isinstance(keys, six.string_types)
        return [v for k, v in heapq.merge(*(self.seqs[k] for k in keys))]

    def add(self, key, item):
        self.seqs[key].append((next(self.counter), item))


def paper_data():
    with io.open(os.path.join(_dir, "papers.yaml")) as f:
        data = YAML().load(f)

    data["topics"] = t = set()
    for obj in itertools.chain(data["papers"], data["talks"]):
        t.update(obj.get("topics", []))

    data["coauthor_count"] = c = collections.Counter()
    data["venue_type_map"] = v = MergedSequencesLookup()
    for paper in data["papers"]:
        for key in paper.get("authors", []):
            if key.endswith("*"):
                key = key[:-1]
            c[key] += 1

        venue_type = data["venues"].get(paper["venue"], {}).get("type", None)
        v.add(venue_type, paper)

    data["coauthor_count_sorted"] = sorted(
        ((key, data["coauthors"][key], count) for key, count in c.items()),
        key=lambda kac: (kac[1]["last"], kac[1]["first"]),
    )

    data["today"] = today

    return data


filters = {}


def filter(fn):
    filters[fn.__name__] = fn
    return fn


@filter
def tojson(x):
    return json.dumps(x)


@filter
def venue_url(venue, year=None):
    if year is not None:
        year = int(year)
    if "web_by_year" in venue and year in venue["web_by_year"]:
        return venue["web_by_year"][year]
    elif "web" in venue:
        return venue["web"]
    return None


def _rate_str(got_in, out_of):
    rate = got_in / out_of
    if rate >= 0.01:
        return f"{got_in:,}/{out_of:,} = {rate :.0%}"
    elif rate >= 0.001:
        return f"{got_in:,}/{out_of:,} = {rate :.1%}"
    else:
        return f"{got_in:,}/{out_of:,} < 0.1%"


@filter
def ar_info(paper, venue):
    if "accepts" not in venue or paper["year"] not in venue["accepts"]:
        return None
    info = venue["accepts"][paper["year"]]

    this_kind = paper.get("accept-kind", "unspecial")

    to_this_yet = False
    this_or_better = 0
    any_accept = 0
    for kind, num in info.items():
        if not to_this_yet:
            this_or_better += num
        if kind == this_kind:
            to_this_yet = True

        if kind == "submitted":
            submitted = num
            break
        else:
            any_accept += num

    if this_kind == "unspecial":
        return _rate_str(this_or_better, info["submitted"])
    else:
        return (
            f"{this_kind}: {_rate_str(this_or_better, submitted)}; "
            f"overall: {_rate_str(any_accept, submitted)}"
        )


@filter
def get_author(author, coauthors, year=None):
    is_equal = author.endswith("*")
    if is_equal:
        author = author[:-1]
    d = copy(coauthors[author])
    d["is_equal"] = is_equal
    d["key"] = author
    if "student_years" in d:
        if not year:
            d["my_student"] = True
        else:
            first, last = d["student_years"]
            if first <= year <= last:
                d["my_student"] = True
    return d


@filter
def get_paper(key, papers):
    return next(paper for paper in papers if paper["key"] == key)


@filter
def paper_short_venue(paper, venues):
    if "venue" not in paper:
        return paper["title"]
    venue = venues[paper["venue"]]
    if venue.get("short"):
        return venue["short"] + "-" + str(paper["year"])[2:]
    else:
        return venue["name"] + " " + paper["year"]


translation_table = {}


@filter
def latex_escape(string):
    "Turn unicode accented characters into LaTeX escapes."
    # based on https://stackoverflow.com/a/4579006/344821
    global translation_table

    if not string:
        return string

    if not translation_table:
        p = re.compile(r"%?.*\DeclareUnicodeCharacter\{(\w+)\}\{(.*)\}")
        fn = subprocess.check_output(["kpsewhich", "utf8enc.dfu"]).strip()
        with io.open(fn) as f:
            for line in f:
                m = p.match(line)
                if m:
                    codepoint, latex = m.groups()
                    latex = latex.replace("@tabacckludge", "")
                    translation_table[int(codepoint, 16)] = "{" + latex + "}"

    return string.translate(translation_table)


@filter
def bibtex_escape(string):
    if not string:
        return string
    string = latex_escape(string)
    string = string.replace("%", r"\%")
    string = string.replace("<", r"$<$")
    string = string.replace(">", r"$>$")
    return string


filters["unidecode"] = unidecode


@filter
def full_name(author_dict):
    if "full_name" in author_dict:
        return author_dict["full_name"]
    return "{} {}".format(author_dict["first"], author_dict["last"])


@filter
def last_name(author_dict):
    return author_dict["last"]


@filter
def first_name(author_dict):
    return author_dict["first"]


@filter
def first_inits(author_dict):
    def init(x):
        return "-".join(n[0] for n in x.split("-"))

    return " ".join(init(n) for n in author_dict["first"].split())


@filter
def bibtex_authors(authors, coauthors, year=None):
    return " and ".join(
        latex_escape(full_name(get_author(a, coauthors, year=year))) for a in authors
    )


@filter
def bibtex_author_an(authors, coauthors, year=None):
    anns = []
    for i, a in enumerate(authors, 1):
        info = get_author(a, coauthors, year=year)
        auth_anns = []
        if info.get("is_equal"):
            auth_anns.append("equal")
        if info.get("is_me"):
            auth_anns.append("me")
        if info.get("my_student"):
            auth_anns.append("mystudent")
        if auth_anns:
            anns.append("{}={}".format(i, ",".join(auth_anns)))
    return "; ".join(anns)


@filter
def bibtex_key(paper, coauthors, year=None):
    auth = get_author(paper["authors"][0], coauthors, year=year)
    prefix = unidecode(last_name(auth)).lower()
    return "{}:{}".format(prefix, paper["key"])


@filter
def in_last_years(obj, n, month=1, day=1):
    if "date" in obj:
        old = datetime.date(year=this_year - n, month=month, day=day)
        return obj["date"] >= old
    else:
        return obj["year"] >= this_year - n


@filter
def in_last_year(obj, **kwargs):
    return in_last_years(obj, 1, **kwargs)


@filter
def maybe_wrap(content, before, after):
    if content:
        return "{}{}{}".format(before, content, after)
    else:
        return ""


@filter
def maybe_punc(content, after="."):
    if content and content[-1] not in ".?!:-–":
        return content + after
    else:
        return content


@filter
def maybe_link(content, url=None):
    if url:
        return "<a href={}>{}</a>".format(url, content)
    else:
        return content


@filter
def last_edit_dt(filenames):
    # is the file currently edited in git?
    fs = list(filenames)
    try:
        subprocess.check_output(["git", "diff-index", "--quiet", "HEAD"] + fs, cwd=_dir)
    except subprocess.CalledProcessError:
        return datetime.datetime.now()
    else:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%ct"] + fs, cwd=_dir
        )
        return datetime.datetime.fromtimestamp(int(out.strip()))


def make_site():
    site = staticjinja.Site.make_site(
        contexts=[(".*", paper_data)],
        filters=filters,
    )
    site._env.tests["falsey"] = lambda x: not x
    return site


def render(site, files=None, watch=False):
    if files:
        for file in files:
            site.render_template(site.get_template(file))
    else:
        site.render(use_reloader=watch)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", default=False)
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    site = make_site()
    render(site, files=args.files, watch=args.watch)
