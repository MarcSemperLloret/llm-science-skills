"""Check a bibliography and the claims it is meant to support.

Three failures cost more than the rest put together: a reference that does not
exist or does not say what it is cited for, a novelty claim with nothing behind
it, and a bibliography that has drifted from the text. The first has become
common wherever drafting is assisted, and it is the one a reader can verify in
seconds and an author never re-checks.

    python litcheck.py references.bib
    python litcheck.py references.bib manuscript.tex
    python litcheck.py references.bib manuscript.tex --verify      # resolve DOIs
    python litcheck.py references.bib --verify --limit 40

--verify queries Crossref for every DOI and compares the stored title and year
with the registered record. It needs network access, no credentials, and is
polite by default; give --mailto your address to be served faster.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

# Sentences that promise something to a reviewer. Each one has to be defensible
# against the literature, and each is the first thing a hostile reviewer tests.
NOVELTY = re.compile(
    r"\b(first (?:study|paper|work|time|to)\b"
    r"|to (?:the best of )?our knowledge"
    r"|no (?:previous|prior|other) (?:study|work|paper)"
    # Only the negative sense. Plain "has been shown" is ordinary prose about
    # the work itself and matched everywhere.
    r"|(?:has|have|had) (?:not|never) been (?:previously )?"
    r"(?:studied|reported|shown|done|attempted|measured)"
    r"|what has not been"
    r"|novel(?:ty)?\b|unprecedented|for the first time"
    r"|we are the first)",
    re.I,
)

STOPWORDS = {"the", "a", "an", "of", "and", "in", "on", "for", "with", "to",
             "from", "by", "at", "as", "is", "are", "using", "via"}


def _fields(body):
    """Field values, counting braces.

    A regex cannot do this: titles protect capitals as {E}urope, so the first
    closing brace is not the end of the value, and everything after it
    desynchronises.
    """
    fields, position = {}, 0
    while True:
        match = re.compile(r"(\w+)\s*=\s*").search(body, position)
        if not match:
            return fields
        name, start = match.group(1).lower(), match.end()
        if start < len(body) and body[start] in "{\"":
            opener = body[start]
            closer = "}" if opener == "{" else '"'
            depth, index = 0, start
            while index < len(body):
                char = body[index]
                if char == opener and (opener == "{" or index == start):
                    depth += 1
                elif char == closer:
                    depth -= 1
                    if depth == 0:
                        break
                index += 1
            value, position = body[start + 1:index], index + 1
        else:
            end = body.find(",", start)
            end = len(body) if end < 0 else end
            value, position = body[start:end], end
        fields[name] = " ".join(value.split())


def split_entries(text):
    """Whole entries, counting braces.

    The obvious pattern ends an entry at a closing brace in the first column,
    which is a house style, not the format. A registrar returns the entry on one
    line, and that pattern then matches nothing and reports no entries at all --
    a silent, plausible, wrong answer rather than an error.
    """
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        depth, index = 1, match.end()
        while index < len(text) and depth:
            depth += (text[index] == "{") - (text[index] == "}")
            index += 1
        yield match.group(1).lower(), match.group(2).strip(), text[match.end():index - 1]


def parse_bib(path):
    """Entries as dicts. Deliberately tolerant: this is a lint, not a parser."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return [{"kind": kind, "key": key, **_fields(body)}
            for kind, key, body in split_entries(text)]


def _words(title):
    return [w for w in re.sub(r"[^a-z0-9 ]", " ", (title or "").lower()).split()
            if w not in STOPWORDS and len(w) > 2]


def _similar(a, b):
    """Word overlap, which is enough to tell a match from a different paper."""
    wa, wb = set(_words(a)), set(_words(b))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / min(len(wa), len(wb))


def check_bib(entries):
    findings = []
    seen_doi, seen_title = {}, {}
    for entry in entries:
        key = entry["key"]
        if entry["kind"] not in ("misc", "unpublished", "software", "dataset"):
            if not entry.get("doi") and not entry.get("url"):
                findings.append(("NOTE", "no-doi",
                                 f"{key}: no DOI and no URL; a reader cannot follow it"))
        year = entry.get("year", "")
        if year and not re.fullmatch(r"(19|20)\d\d", year):
            findings.append(("NOTE", "year", f"{key}: year {year!r} is not a year"))
        doi = (entry.get("doi") or "").lower().replace("https://doi.org/", "")
        if doi:
            if doi in seen_doi:
                findings.append(("FAIL", "duplicate",
                                 f"{key} and {seen_doi[doi]} carry the same DOI"))
            seen_doi[doi] = key
        title = entry.get("title", "")
        if title:
            flat = " ".join(_words(title))
            if flat in seen_title and seen_title[flat] != key:
                findings.append(("NOTE", "duplicate",
                                 f"{key} and {seen_title[flat]} have the same title"))
            seen_title[flat] = key
    return findings


def check_usage(entries, tex_paths, min_refs=30):
    findings = []
    text = ""
    for path in tex_paths:
        text += Path(path).read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"(?<!\\)%.*", "", text)

    cited = set()
    for group in re.findall(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}", text):
        cited.update(k.strip() for k in group.split(",") if k.strip())

    keys = {e["key"] for e in entries}
    for orphan in sorted(cited - keys):
        findings.append(("FAIL", "missing-entry",
                         f"{orphan} is cited but has no bibliography entry"))
    unused = sorted(keys - cited)
    if unused:
        findings.append(("NOTE", "unused-entry",
                         f"{len(unused)} entries are never cited: "
                         f"{', '.join(unused[:8])}"
                         f"{' ...' if len(unused) > 8 else ''}"))

    selfcites = [e for e in entries
                 if e["key"] in cited and "Semper" in e.get("author", "")]
    if cited and len(selfcites) / len(cited) > 0.15:
        findings.append(("NOTE", "self-citation",
                         f"{len(selfcites)} of {len(cited)} cited works are ours "
                         f"({len(selfcites) / len(cited):.0%}); editors notice"))

    if cited and len(cited) < min_refs:
        findings.append(("NOTE", "reference-count",
                         f"only {len(cited)} works are cited. A reviewer for a strong "
                         f"journal reads a short bibliography as not knowing the "
                         f"field, whatever the paper says; {min_refs} is a floor, not "
                         "a target"))

    years = sorted(int(e["year"]) for e in entries
                   if e["key"] in cited and re.fullmatch(r"(19|20)\d\d", e.get("year", "")))
    if years:
        # The baseline is today, not the newest entry in the file. Taking the
        # maximum lets one forthcoming paper dated next year redefine what
        # "recent" means and quietly disqualify this year's citations.
        import datetime

        now = datetime.date.today().year
        newest = max(years)
        median = years[len(years) // 2]
        current = sum(1 for y in years if y >= now - 1)
        findings.append(("INFO", "recency",
                         f"{len(years)} dated citations, median {median}, "
                         f"{current} from {now - 1} or later, newest {newest}"))
        if newest > now:
            findings.append(("NOTE", "future-year",
                             f"a citation is dated {newest}, which is in the future; "
                             "if it is forthcoming, say so in the entry"))
        # Currency and volume are different failures. A short bibliography can be
        # entirely current; a long one can be entirely old. Both get read as not
        # following the field.
        if current < 5:
            findings.append(("NOTE", "currency",
                             f"only {current} citations from {now - 1} or later; a "
                             "reviewer checks whether the current literature is known "
                             "before reading the method"))
        if now - median > 8:
            findings.append(("NOTE", "currency",
                             f"the median citation is from {median} while the field "
                             f"has reached {now}; the bibliography reads as "
                             "assembled some time ago"))

    # Sentences, not lines: LaTeX wraps wherever the column ends, so a line is
    # not a unit of meaning, and a claim is routinely positioned by the sentence
    # before it rather than by a citation inside it.
    flat = " ".join(text.split())
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", flat)
    for index, sentence in enumerate(sentences):
        match = NOVELTY.search(sentence)
        if not match:
            continue
        window = " ".join(sentences[max(0, index - 2):index + 2])
        placed = "cite" in window
        findings.append((
            "NOTE", "novelty-claim",
            f"{match.group(0)!r} in: {sentence.strip()[:90]}..."
            + ("; the surrounding sentences do cite, check that they support it"
               if placed else "; NOTHING is cited near it, so the claim is unplaced"),
        ))
    return findings


def verify_dois(entries, limit=None, mailto=None, pause=0.15):
    """Resolve each DOI against Crossref and compare title and year."""
    findings = []
    targets = [e for e in entries if e.get("doi")]
    if limit:
        targets = targets[:limit]
    from urllib.parse import quote

    for entry in targets:
        doi = entry["doi"].strip().replace("https://doi.org/", "")
        # doi.org content negotiation, not a registrar API: it resolves Crossref,
        # DataCite and the rest, so Zenodo deposits answer too. The path is
        # quoted because real DOIs contain brackets, slashes and semicolons.
        url = "https://doi.org/" + quote(doi, safe="/")
        headers = ["-H", "Accept: application/vnd.citationstyles.csl+json"]
        if mailto:
            headers += ["-H", f"User-Agent: litcheck (mailto:{mailto})"]
        result = subprocess.run(
            ["curl", "-sL", "--max-time", "25", *headers, url],
            capture_output=True, encoding="utf-8", errors="replace",
        )
        time.sleep(pause)
        try:
            message = json.loads(result.stdout)
        except ValueError:
            findings.append(("FAIL", "doi-unresolved",
                             f"{entry['key']}: DOI {doi} does not resolve"))
            continue
        title = message.get("title") or ""
        registered = title[0] if isinstance(title, list) else title
        score = _similar(entry.get("title", ""), registered)
        if score < 0.5:
            findings.append(("FAIL", "doi-mismatch",
                             f"{entry['key']}: the DOI registers "
                             f"{registered[:70]!r}, the entry says "
                             f"{entry.get('title', '')[:70]!r}"))
            continue
        parts = (message.get("issued", {}).get("date-parts") or [[None]])[0]
        if parts and parts[0] and entry.get("year"):
            if abs(int(parts[0]) - int(entry["year"])) > 1:
                findings.append(("NOTE", "doi-year",
                                 f"{entry['key']}: registered {parts[0]}, entry says "
                                 f"{entry['year']}"))
    findings.append(("INFO", "verified", f"{len(targets)} DOIs resolved via doi.org"))
    return findings


if hasattr(sys.stdout, "reconfigure"):    # titles carry Greek and dashes
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def report(findings, header=None):
    if header:
        print(header)
    if not findings:
        print("  no findings")
        return True
    for severity, code, message in findings:
        print(f"  {severity:<4}  {code:<16}  {message}")
    fails = sum(1 for f in findings if f[0] == "FAIL")
    notes = sum(1 for f in findings if f[0] == "NOTE")
    print(f"  -> {fails} FAIL, {notes} NOTE")
    return fails == 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    verify = "--verify" in argv
    argv = [a for a in argv if a != "--verify"]
    limit = mailto = None
    min_refs = 30
    for flag, cast in (("--limit", int), ("--mailto", str), ("--min-refs", int)):
        if flag in argv:
            index = argv.index(flag)
            value = cast(argv[index + 1])
            argv = argv[:index] + argv[index + 2:]
            if flag == "--limit":
                limit = value
            elif flag == "--min-refs":
                min_refs = value
            else:
                mailto = value

    bib, tex = argv[0], argv[1:]
    entries = parse_bib(bib)
    findings = [("INFO", "entries", f"{len(entries)} bibliography entries")]
    findings += check_bib(entries)
    if tex:
        findings += check_usage(entries, tex, min_refs=min_refs)
    if verify:
        findings += verify_dois(entries, limit=limit, mailto=mailto)
    return 0 if report(findings, f"{bib}") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
