"""Search the literature across several open APIs, with provenance.

One database is one field's blind spot. Crossref and OpenAlex index almost
everything with a DOI, Europe PMC reaches the biomedical literature and its
preprints, and arXiv holds the physics, computing and statistics that often
never acquire a DOI at all. A novelty claim checked against one of them is not
checked.

    python litsearch.py "convective outflow detection mesonet"
    python litsearch.py "urban heat accessibility" --source openalex --rows 20
    python litsearch.py "wastewater resistome" --venue "Water Research" --rows 50
    python litsearch.py --doi 10.1175/BAMS-D-16-0067.1            # what it is
    python litsearch.py --cites 10.1175/BAMS-D-16-0067.1          # who cites it
    python litsearch.py --refs 10.1175/BAMS-D-16-0067.1           # what it cites
    python litsearch.py --bibtex 10.1175/BAMS-D-16-0067.1 ...     # ready to paste

No credentials are needed. Give --mailto your address to enter the polite pools
and be served faster. Every row carries the source that returned it, so a claim
can say where it was checked.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import unicodedata
from urllib.parse import quote_plus, quote

SOURCES = ("crossref", "openalex", "europepmc", "arxiv")


def _get(url, accept="application/json"):
    """Body and HTTP status, kept apart.

    Returning only the body makes a refused request look like an empty one, and
    an empty result is a claim about the literature. Rate limiting is the common
    case: several queries in a row and the index starts declining, quietly.
    """
    result = subprocess.run(
        ["curl", "-sL", "--max-time", "30", "-w", "\n%{http_code}",
         "-H", f"Accept: {accept}", url],
        capture_output=True, encoding="utf-8", errors="replace",
    )
    body, _, status = result.stdout.rpartition("\n")
    time.sleep(0.34)                      # stay inside the polite request rate
    return body, status.strip()


def _json(url):
    body, status = _get(url)
    if status != "200":
        raise RuntimeError(f"HTTP {status or 'no response'}")
    try:
        return json.loads(body)
    except ValueError:
        raise RuntimeError("the reply was not JSON")


def _record(source, title, year, authors, doi, venue, cited=None):
    return {
        "source": source,
        "title": " ".join((title or "").split()),
        "year": str(year or ""),
        "authors": authors or "",
        "doi": (doi or "").lower().replace("https://doi.org/", ""),
        "venue": " ".join((venue or "").split())[:40],
        "cited": cited,
    }


def crossref(query, rows, mailto):
    url = f"https://api.crossref.org/works?query={quote_plus(query)}&rows={rows}"
    if mailto:
        url += f"&mailto={mailto}"
    data = _json(url)
    out = []
    for item in (data or {}).get("message", {}).get("items", []):
        authors = ", ".join(
            f"{a.get('family', '')}" for a in item.get("author", [])[:3]) or ""
        parts = (item.get("issued", {}).get("date-parts") or [[None]])[0]
        out.append(_record("crossref", (item.get("title") or [""])[0], parts[0],
                           authors, item.get("DOI"),
                           (item.get("container-title") or [""])[0],
                           item.get("is-referenced-by-count")))
    return out


def openalex(query, rows, mailto):
    url = f"https://api.openalex.org/works?search={quote_plus(query)}&per-page={rows}"
    if mailto:
        url += f"&mailto={mailto}"
    data = _json(url)
    out = []
    for item in (data or {}).get("results", []):
        authors = ", ".join(
            a.get("author", {}).get("display_name", "").split()[-1]
            for a in item.get("authorships", [])[:3])
        venue = ((item.get("primary_location") or {}).get("source") or {})
        out.append(_record("openalex", item.get("title"), item.get("publication_year"),
                           authors, item.get("doi"), venue.get("display_name"),
                           item.get("cited_by_count")))
    return out


def europepmc(query, rows, mailto):
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
           f"{quote_plus(query)}&format=json&pageSize={rows}")
    data = _json(url)
    out = []
    for item in (data or {}).get("resultList", {}).get("result", []):
        out.append(_record("europepmc", item.get("title"), item.get("pubYear"),
                           item.get("authorString", "")[:60], item.get("doi"),
                           item.get("journalTitle"), item.get("citedByCount")))
    return out


def arxiv(query, rows, mailto):
    url = ("http://export.arxiv.org/api/query?search_query=all:"
           f"{quote_plus(query)}&max_results={rows}")
    text, status = _get(url, accept="application/atom+xml")
    if status != "200":
        raise RuntimeError(f"HTTP {status}")
    out = []
    for entry in re.findall(r"<entry>(.*?)</entry>", text, re.S):
        title = re.search(r"<title>(.*?)</title>", entry, re.S)
        published = re.search(r"<published>(\d{4})", entry)
        names = re.findall(r"<name>(.*?)</name>", entry)
        doi = re.search(r"<arxiv:doi[^>]*>(.*?)</arxiv:doi>", entry, re.S)
        link = re.search(r"<id>(.*?)</id>", entry, re.S)
        out.append(_record("arxiv", title.group(1) if title else "",
                           published.group(1) if published else "",
                           ", ".join(n.split()[-1] for n in names[:3]),
                           doi.group(1) if doi else "",
                           (link.group(1) if link else "").replace(
                               "http://arxiv.org/abs/", "arXiv:")))
    return out


def by_doi(doi, mailto):
    data = _json("https://api.openalex.org/works/https://doi.org/" + quote(doi, safe="/"))
    if not data:
        return []
    venue = ((data.get("primary_location") or {}).get("source") or {})
    authors = ", ".join(a.get("author", {}).get("display_name", "").split()[-1]
                        for a in data.get("authorships", [])[:3])
    return [_record("openalex", data.get("title"), data.get("publication_year"),
                    authors, data.get("doi"), venue.get("display_name"),
                    data.get("cited_by_count"))]


def cites(doi, rows, mailto):
    """Forward chaining: what has cited this since."""
    work = _json("https://api.openalex.org/works/https://doi.org/" + quote(doi, safe="/"))
    if not work:
        return []
    url = (f"https://api.openalex.org/works?filter=cites:{work['id'].split('/')[-1]}"
           f"&per-page={rows}&sort=cited_by_count:desc")
    if mailto:
        url += f"&mailto={mailto}"
    data = _json(url)
    out = []
    for item in (data or {}).get("results", []):
        authors = ", ".join(a.get("author", {}).get("display_name", "").split()[-1]
                            for a in item.get("authorships", [])[:3])
        source = ((item.get("primary_location") or {}).get("source") or {})
        out.append(_record("cites", item.get("title"), item.get("publication_year"),
                           authors, item.get("doi"), source.get("display_name"),
                           item.get("cited_by_count")))
    return out


def refs(doi, rows, mailto):
    """Backward chaining: what this cites."""
    work = _json("https://api.openalex.org/works/https://doi.org/" + quote(doi, safe="/"))
    out = []
    for ref in (work or {}).get("referenced_works", [])[:rows]:
        item = _json(f"https://api.openalex.org/works/{ref.split('/')[-1]}")
        if not item:
            continue
        authors = ", ".join(a.get("author", {}).get("display_name", "").split()[-1]
                            for a in item.get("authorships", [])[:3])
        source = ((item.get("primary_location") or {}).get("source") or {})
        out.append(_record("refs", item.get("title"), item.get("publication_year"),
                           authors, item.get("doi"), source.get("display_name"),
                           item.get("cited_by_count")))
    return out


def _protect_caps(title):
    """Brace the capitals BibTeX would otherwise flatten.

    A registrar returns the title as plain text, and a style that lowercases
    titles then turns "SARS-CoV-2 RNA" into "Sars-cov-2 rna" in the printed
    reference list. It is silent, it survives every compile, and it is exactly
    what a screening editor sees. Braces stop it.
    """
    words = title.split()
    out = []
    for index, word in enumerate(words):
        core = re.sub(r"[^A-Za-z0-9-]", "", word)
        interior = core[1:] if index == 0 else core
        if "{" not in word and any(c.isupper() for c in interior):
            head = re.match(r"^\W*", word).group(0)
            tail = re.search(r"\W*$", word).group(0)
            body = word[len(head):len(word) - len(tail) or None]
            word = f"{head}{{{body}}}{tail}"
        out.append(word)
    return " ".join(out)


def _citekey(entry):
    """A readable key built from the first author and the year.

    The registrar's own key drops any letter it cannot encode, so Munoz becomes
    Mu_oz and Celinski-Myslaw becomes Celi_ski_Mys_aw. Stripping the leftovers
    gives muoz2018 and celiskimysaw2020, which nobody can read in a citation.
    Fold the accents instead of deleting the letters.
    """
    author = re.search(r"author=\{(.*?)\}(?=,)", entry)
    year = re.search(r"year=\{(\d{4})\}", entry)
    if not author or not year:
        return None
    surname = author.group(1).split(" and ")[0].split(",")[0].strip()
    surname = surname.split()[-1] if "," not in author.group(1) else surname
    # NFKD folds a diacritic off its base letter, but a few letters are not a
    # base plus a mark at all -- the Polish stroked l among them -- and would
    # simply vanish, turning Myslaw into Mysaw.
    for letter, plain in ((chr(322), "l"), (chr(321), "L"), (chr(248), "o"),
                          (chr(216), "O"), (chr(273), "d"), (chr(223), "ss"),
                          (chr(230), "ae"), (chr(198), "Ae"), (chr(240), "d"),
                          (chr(254), "th"), (chr(261), "a")):
        surname = surname.replace(letter, plain)
    folded = unicodedata.normalize("NFKD", surname)
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    folded = re.sub(r"[^A-Za-z]", "", folded).lower()
    return f"{folded}{year.group(1)}" if folded else None


def bibtex(dois, mailto=None):
    """The registrar's own BibTeX for each DOI.

    Typing an entry from a search result is where fabrication enters: the year
    drifts, the volume is guessed, the title loses a word. Ask the registry for
    the record instead. doi.org content negotiation answers for Crossref and
    DataCite alike, so a Zenodo deposit produces an entry too.
    """
    for doi in dois:
        doi = doi.strip().replace("https://doi.org/", "")
        headers = ["-H", "Accept: application/x-bibtex"]
        if mailto:
            headers += ["-H", f"User-Agent: litsearch (mailto:{mailto})"]
        result = subprocess.run(
            ["curl", "-sL", "--max-time", "25", *headers,
             "https://doi.org/" + quote(doi, safe="/")],
            capture_output=True, encoding="utf-8", errors="replace",
        )
        entry = result.stdout.strip()
        if not entry.startswith("@"):
            print(f"% UNRESOLVED {doi} -- do not cite it", file=sys.stderr)
            continue
        # Some registrars deposit a bare record: a DOI, a journal and a year,
        # with no title and no authors. Pasted into a bibliography it prints as
        # an anonymous line that no reader can follow, and nothing downstream
        # objects. Fill it from the index instead of emitting it.
        if not re.search(r"(?i)title=\{", entry):
            patch = by_doi(doi, mailto)
            if patch and patch[0]["title"]:
                fields = f'title={{{patch[0]["title"]}}}, '
                if patch[0]["authors"]:
                    fields += f'author={{{patch[0]["authors"]}}}, '
                entry = re.sub(r"(\{[^,]+,\s*)", r"\1" + fields, entry, count=1)
                print(f"% NOTE the registrar's record for {doi} carried no title; "
                      "filled from the index and worth checking", file=sys.stderr)
            else:
                print(f"% INCOMPLETE {doi} -- no title on record, do not paste "
                      "this", file=sys.stderr)
                continue
        entry = re.sub(r"(?i)(title=\{)(.*?)(\},)",
                       lambda m: m.group(1) + _protect_caps(m.group(2)) + m.group(3),
                       entry, count=1)
        key = _citekey(entry)
        if key:
            entry = re.sub(r"(@\w+\{)[^,]+", lambda m: m.group(1) + key, entry, count=1)
        print(entry)
        print()


def resolve_venue(name):
    """The registry's identifier for a journal, from its name or ISSN.

    Filtering results after the fact cannot work for this: a keyword search
    returns what is popular across the whole literature, and a given journal
    contributes a handful of rows at best. Ask the index for that journal's
    works instead.
    """
    url = ("https://api.openalex.org/sources?search=" + quote_plus(name)
           + "&per-page=5")
    for item in (_json(url) or {}).get("results", []):
        if _venue_key(item.get("display_name")) == _venue_key(name):
            return item["id"].split("/")[-1], item.get("display_name")
    return None, None


def in_venue(query, rows, venue, mailto):
    """Works from one journal, ranked by relevance to the query."""
    source, display = resolve_venue(venue)
    if not source:
        print(f"  NOTE  no journal in the index is named {venue!r} exactly")
        return []
    url = (f"https://api.openalex.org/works?search={quote_plus(query)}"
           f"&filter=primary_location.source.id:{source}&per-page={rows}")
    if mailto:
        url += f"&mailto={mailto}"
    out = []
    for item in (_json(url) or {}).get("results", []):
        authors = ", ".join(a.get("author", {}).get("display_name", "").split()[-1]
                            for a in item.get("authorships", [])[:3])
        out.append(_record("in-venue", item.get("title"), item.get("publication_year"),
                           authors, item.get("doi"), display,
                           item.get("cited_by_count")))
    return out


def dedupe(records):
    """One row per work, remembering every source that returned it."""
    merged = {}
    for record in records:
        words = re.sub(r"[^a-z0-9 ]", " ", record["title"].lower()).split()
        key = record["doi"] or " ".join(words[:8])
        if not key:
            continue
        if key in merged:
            if record["source"] not in merged[key]["source"]:
                merged[key]["source"] += "+" + record["source"]
            if record["cited"] and not merged[key]["cited"]:
                merged[key]["cited"] = record["cited"]
        else:
            merged[key] = dict(record)
    return list(merged.values())


if hasattr(sys.stdout, "reconfigure"):    # titles carry Greek and dashes
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _venue_key(name):
    """A journal name reduced to what makes it that journal.

    Substring matching is wrong here and wrong in a way that flatters: "Internet
    of Things" occurs inside "IEEE Internet of Things Journal", and "Water
    Research" inside "Water Research X". Those are different journals, and
    counting them as the target turns a failed fit check into a pass.
    """
    name = re.sub(r"[^a-z0-9 ]", " ", (name or "").lower())
    return " ".join(w for w in name.split() if w not in ("the", "of", "and"))


def show(records, venue=None):
    if venue:
        target = _venue_key(venue)
        records = [r for r in records if _venue_key(r["venue"]) == target]
    if not records:
        print("  nothing found")
        return
    records.sort(key=lambda r: (-(r["cited"] or 0), r["year"]))
    for record in records:
        cited = f"{record['cited']:>5}" if record["cited"] is not None else "    -"
        print(f"  {record['year']:<5} {cited} cites  {record['source']:<18} "
              f"{record['title'][:74]}")
        if record["doi"]:
            print(f"        {record['doi']}  {record['venue'][:34]}  "
                  f"{record['authors'][:34]}")
    print(f"  -> {len(records)} distinct works")


def main(argv):
    if not argv or {"-h", "--help"} & set(argv):
        print(__doc__)
        return 0 if argv else 2
    rows, mailto, source, venue = 10, None, None, None
    for flag in ("--rows", "--mailto", "--source", "--venue"):
        if flag in argv:
            index = argv.index(flag)
            value = argv[index + 1]
            argv = argv[:index] + argv[index + 2:]
            if flag == "--rows":
                rows = int(value)
            elif flag == "--mailto":
                mailto = value
            elif flag == "--venue":
                venue = value
            else:
                source = value

    def guarded(function, *args):
        try:
            return function(*args)
        except RuntimeError as error:
            print(f"  NOTE  the index did not answer ({error}); this is not an "
                  "empty field")
            return []

    if "--bibtex" in argv:
        index = argv.index("--bibtex")
        bibtex(argv[index + 1:], mailto)
        return 0

    for flag, function in (("--doi", by_doi), ("--cites", cites), ("--refs", refs)):
        if flag in argv:
            doi = argv[argv.index(flag) + 1]
            print(f"{flag} {doi}")
            show(guarded(function, doi, mailto) if flag == "--doi"
                 else guarded(function, doi, rows, mailto), venue)
            return 0

    query = " ".join(argv)
    print(f"query: {query}" + (f"   in: {venue}" if venue else ""))
    records = []
    if venue:
        show(dedupe(guarded(in_venue, query, rows, venue, mailto)))
        return 0
    for name in (source,) if source else SOURCES:
        try:
            records += globals()[name](query, rows, mailto)
        except Exception as error:                      # one API down is not fatal
            print(f"  NOTE  {name} did not answer ({error}); that is not the same "
                  "as an empty field")
    show(dedupe(records), venue)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
