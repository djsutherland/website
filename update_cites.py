#!/usr/bin/env python
from datetime import date
from pathlib import Path


from ruamel.yaml import YAML

yaml = YAML()
yaml.width = 1000
yaml.indent(mapping=2, sequence=4, offset=2)

fn = Path(__file__).parent / "papers.yaml"
data = yaml.load(fn)


if True:
    from scholarly import scholarly

    me = scholarly.search_author_id("uO_NqicAAAAJ", filled=True)
    assert me["email_domain"] == "@cs.ubc.ca"

    data["cite_meta"]["last_cite_update"] = "{:%Y-%m-%d}".format(date.today())
    data["cite_meta"]["total"] = me["citedby"]
    data["cite_meta"]["total_5y"] = me["citedby5y"]
    data["cite_meta"]["h_index"] = me["hindex"]
    data["cite_meta"]["h_index_5y"] = me["hindex5y"]
    data["cite_meta"]["i10_index"] = me["i10index"]
    data["cite_meta"]["i10_index_5y"] = me["i10index5y"]

    touched = set()

    for pub in me["publications"]:
        if "cites_id" not in pub:
            continue
        cites_ids = frozenset(pub["cites_id"])

        if cites_ids == {"7841818900121312344"}:  # dumb undergrad python thing
            continue

        matches = [
            p
            for p in data["papers"]
            if frozenset(str(p.get("gs_id", "")).split()) & cites_ids
        ]
        if not matches:
            print(f"No matches for GS paper: {pub['num_citations']} cites\n{pub!r}\n")
            continue
        elif len(matches) > 1:
            raise ValueError(
                "multiple matches for GS publication: {' '.join(p['key'] for p in matches)}\n{pub!r}\n"
            )
        (p,) = matches

        if p["key"] in touched:
            print(f"Warning: hitting paper {p['key']} more than once, consider merging on GS profile")
            p["citations"] += pub["num_citations"]
        else:
            p["citations"] = pub["num_citations"]
            touched.add(p["key"])

    untouched = [
        p["key"]
        for p in data["papers"]
        if p["key"] not in touched and p.get("citations", 0) > 0
    ]
    if untouched:
        raise ValueError(
            "uh-oh: these papers didn't show up but I think they have cites!"
            f"\n{' '.join(untouched)}"
        )

# semantic scholar code...nicer but numbers are so much lower tho
#
# from semanticscholar import SemanticScholar
# ss = SemanticScholar()
#
# for p in tqdm(data["papers"]):
#     if "ss_id" not in p:
#         if "venue" not in p:
#             print(f"No ss_id or venue for paper {p['key']}...")
#         elif data["venues"][p["venue"]].get("type") not in {"private", "workshop"}:
#             print(f"No ss_id for paper {p['key']} at {p['venue']}")
#         p["citations"] = 0
#         continue
#
#     ssp = ss.get_paper(p["ss_id"])
#     p["citations"] = ssp["citationCount"]
#


if True:
    # fill stupid publication ranks, lol
    # google never seems to respond on this page to python requests even via scholarly w/ proxies,
    # but this should work:
    import subprocess
    import bs4

    import warnings

    warnings.filterwarnings("ignore", category=bs4.GuessedAtParserWarning)  # shut up

    res = subprocess.check_output(
        ["curl", "-SsL", "https://scholar.google.com/citations?view_op=top_venues"]
    )

    soup = bs4.BeautifulSoup(res)
    wants = {
        "International Conference on Learning Representations": "iclr",
        "Neural Information Processing Systems": "neurips",
        "International Conference on Machine Learning": "icml",
    }
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 4:
            long_name = tds[1].get_text()
            if long_name in wants:
                rank = tds[0].get_text()
                assert rank.endswith(".")
                rank = int(rank[:-1])
                data["venues"][wants[long_name]]["h5_rank"] = rank


with open(fn, "w") as out:
    yaml.dump(data, out)
