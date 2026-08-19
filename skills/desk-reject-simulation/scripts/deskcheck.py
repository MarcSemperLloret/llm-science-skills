"""Mechanical submission checks on a LaTeX manuscript and its compiled PDF.

An editor's first screen is partly judgement and partly a checklist, and the
checklist half is where most desk rejects are earned: a missing statement, an
abstract over the limit, a figure nobody cites, a broken reference. None of that
needs an opinion, so none of it should cost a submission.

    python deskcheck.py manuscript.tex [manuscript.pdf] [--abstract-max 250]

FAIL is something that will stop a submission. NOTE is something an editor will
notice. The judgement half of the screen is in SKILL.md and is not automatable.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = {
    "CRediT": r"CRediT authorship contribution",
    "funding": r"section\*?\{Funding",
    "competing interests": r"[Cc]ompeting interest",
    "data availability": r"[Dd]ata (?:and \w+ )?availability"
                         r"|[Aa]vailability of (?:the )?data",
    "AI declaration": r"generative AI",
}

# Naming a model, a vendor or an access date in the AI declaration is easy to
# leave behind from an earlier draft, and it is exactly what a screening editor
# reads first.
NOVELTY = re.compile(
    r"\b(first (?:study|paper|work|time|to)\b"
    r"|to (?:the best of )?our knowledge"
    r"|no (?:previous|prior|other) (?:study|work|paper)"
    r"|(?:has|have|had) (?:not|never) been (?:previously )?"
    r"(?:studied|reported|shown|done|attempted|measured)"
    r"|what has not been|we are the first"
    r"|novel(?:ty)?\b|unprecedented|for the first time"
    # Careful writing states novelty as a gap rather than a boast. A checker
    # that knows only the boastful register reports the best-written papers as
    # making no claim at all.
    r"|a (?:clear )?gap remains|gap in the literature"
    r"|(?:remains?|remain) (?:largely )?(?:unaddressed|unexplored|untested|open)"
    r"|no (?:existing|published|current|available) "
    r"(?:study|work|approach|method|framework|analysis)"
    r"|we are (?:aware of no|not aware of any)"
    r"|(?:has|have) yet to be"
    # The bare phrase catches ordinary methods prose -- "none of these
    # observations enters the validation field" -- so require a verb that can
    # only be predicated of prior work.
    r"|none of (?:them|these|which|the above) (?:couples?|combines?|addresses"
    r"|address|evaluates?|examines?|tests?|measures?|provides?|reports?"
    r"|has|have|does|do|is|are)\b)",
    re.I,
)

# This pattern has been silently destroyed twice by an escape being eaten before
# it reached the file, each time leaving a checker that matched nothing and
# reported every manuscript as making no claim. A pattern that cannot fail
# loudly will fail quietly, so make it prove itself at import.
for _probe in ("To our knowledge, no previous study has done this",
               "a gap remains, in that none of them couples A to B",
               "we introduce a novel framework"):
    assert NOVELTY.search(_probe), "the novelty pattern is broken: " + _probe
assert not NOVELTY.search("none of these observations enters the field")


TOOL_NAMES = (
    r"\b(ChatGPT|GPT-?[0-9]|OpenAI|Codex|Claude|Anthropic|Gemini|Copilot"
    r"|Llama|Mistral|DeepSeek|Perplexity)\b"
)


def _strip_comments(text):
    """Drop LaTeX comments, keeping escaped per-cent signs."""
    return re.sub(r"(?<!\\)%.*", "", text)


def check_tex(path, abstract_max=250):
    findings = []
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    tex = _strip_comments(raw)

    for label, pattern in REQUIRED_SECTIONS.items():
        if not re.search(pattern, tex):
            findings.append(("FAIL", "missing-statement",
                             f"no {label} statement; most journals refuse the "
                             "submission without it"))

    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    if match:
        words = len(re.sub(r"\\[a-zA-Z]+\*?", " ", match.group(1)).split())
        if words > abstract_max:
            findings.append(("FAIL", "abstract-length",
                             f"abstract is {words} words against a {abstract_max}-word "
                             "limit"))
        elif words > abstract_max * 0.92:
            findings.append(("NOTE", "abstract-length",
                             f"abstract is {words} words, close to the "
                             f"{abstract_max} limit"))
    else:
        findings.append(("NOTE", "abstract", "no abstract environment found"))

    match = re.search(r"\\title\{(.*?)\}", tex, re.S)
    if match and len(match.group(1)) > 150:
        findings.append(("NOTE", "title-length",
                         f"title is {len(match.group(1))} characters; most journals "
                         "cap it near 120"))

    match = re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", tex, re.S)
    if match:
        count = len([k for k in match.group(1).split(r"\sep") if k.strip()])
        if not 3 <= count <= 8:
            findings.append(("NOTE", "keywords",
                             f"{count} keywords; journals usually ask for 4 to 6"))

    declaration = re.search(r"generative AI(.*?)(\\section|\Z)", tex, re.S)
    if declaration:
        named = sorted(set(re.findall(TOOL_NAMES, declaration.group(1), re.I)))
        if named:
            findings.append(("FAIL", "ai-declaration",
                             f"the AI declaration names {', '.join(named)}; it should "
                             "say what was done and name no product"))
        if re.search(r"accessed\s+\d", declaration.group(1), re.I):
            findings.append(("NOTE", "ai-declaration",
                             "the AI declaration carries an access date; drop it"))

    labels = set(re.findall(r"\\label\{((?:fig|tab):[^}]+)\}", tex))
    cited = set()
    for reference in re.findall(r"\\(?:ref|autoref|cref|Cref)\{([^}]+)\}", tex):
        cited.update(part.strip() for part in reference.split(","))
    for orphan in sorted(labels - cited):
        findings.append(("FAIL", "uncited-float",
                         f"{orphan} is never referred to in the text; every figure "
                         "and table must be cited"))

    if re.search(r"\\todo|\\TODO|XXX|FIXME|\?\?\?", tex):
        findings.append(("FAIL", "placeholder",
                         "the source still contains a TODO, FIXME or ??? marker"))
    if re.search(r"<[a-z][a-z ]{2,}>", tex):
        findings.append(("NOTE", "placeholder",
                         "the source still contains an angle-bracket placeholder"))

    findings += check_novelty(tex)
    return findings


def check_novelty(tex):
    """Whether the paper says what is new, and places it.

    Insufficient novelty is a desk-reject reason an editor gives in one line.
    They are not judging whether the work is new; they are judging whether the
    paper says what is new and against what. A manuscript that never makes the
    claim leaves the editor to construct it, and the safe thing to do with a
    paper you cannot place is return it.
    """
    findings = []
    flat = " ".join(tex.split())
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", flat)

    claims = [(i, s) for i, s in enumerate(sentences) if NOVELTY.search(s)]
    if not claims:
        findings.append(("NOTE", "novelty",
                         "no sentence states what is new. An editor should not have "
                         "to infer the contribution; say it in the abstract and again "
                         "at the end of the introduction"))
    for index, sentence in claims:
        window = " ".join(sentences[max(0, index - 2):index + 2])
        if "cite" not in window:
            findings.append(("NOTE", "novelty",
                             f"a novelty claim with nothing cited around it: "
                             f"{sentence.strip()[:80]}..."))
    return findings


def _venue_key(name):
    """A journal name reduced to what makes it that journal.

    Substring matching is wrong here and wrong in a way that flatters: "Internet
    of Things" occurs inside "IEEE Internet of Things Journal", and "Water
    Research" inside "Water Research X". Those are different journals, and
    counting them as the target turns a failed fit check into a pass.
    """
    name = re.sub(r"[^a-z0-9 ]", " ", (name or "").lower())
    return " ".join(w for w in name.split() if w not in ("the", "of", "and"))


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


def check_bibliography(bib_path, tex, min_refs=30, journal=None):
    """The three things an editor checks about the references in a minute.

    Volume, currency, and whether the paper engages with the journal it is being
    sent to. The last is the fit signal: a submission that cites nothing from
    its target venue reads as sent to the wrong address, whatever its subject.
    """
    import datetime

    findings = []
    text = Path(bib_path).read_text(encoding="utf-8", errors="replace")
    entries = list(split_entries(text))

    cited = set()
    for group in re.findall(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}", tex):
        cited.update(k.strip() for k in group.split(",") if k.strip())
    used = [(k.strip(), body) for _, k, body in entries if k.strip() in cited]

    if used and len(used) < min_refs:
        findings.append(("FAIL", "reference-count",
                         f"only {len(used)} works are cited; for a strong journal that "
                         "is itself a desk-reject reason, and editors say so"))

    now = datetime.date.today().year
    years = sorted(int(m.group(1)) for _, body in used
                   for m in [re.search(r"year\s*=\s*[{\"]?((?:19|20)\d\d)", body)] if m)
    if years:
        median = years[len(years) // 2]
        current = sum(1 for y in years if y >= now - 1)
        findings.append(("INFO", "recency",
                         f"{len(years)} dated, median {median}, {current} from "
                         f"{now - 1} or later"))
        if current < 5:
            findings.append(("NOTE", "currency",
                             f"only {current} citations from {now - 1} or later"))
        if now - median > 8:
            findings.append(("NOTE", "currency",
                             f"median citation {median}, {now - median} years behind"))

    if journal:
        target = _venue_key(journal)
        hits = 0
        for _, body in used:
            field = re.search(r"journal\s*=\s*[{\"]([^}\"]*)", body)
            if field and _venue_key(field.group(1)) == target:
                hits += 1
        if hits == 0:
            findings.append(("FAIL", "journal-fit",
                             f"nothing in the bibliography is published in {journal!r}. "
                             "An editor reads that as a paper sent to the wrong "
                             "journal; cite the conversation you are joining"))
        elif hits < 3:
            findings.append(("NOTE", "journal-fit",
                             f"{hits} reference(s) from {journal!r}; thin engagement "
                             "with the venue"))
        else:
            findings.append(("INFO", "journal-fit",
                             f"{hits} references from {journal!r}"))
    return findings


def check_log(path):
    """Undefined references and citations, read from the LaTeX log."""
    findings = []
    log = Path(path).with_suffix(".log")
    if not log.exists():
        return findings
    text = log.read_text(encoding="utf-8", errors="replace")
    for pattern, message in (
        (r"Citation `([^']+)' (?:on page \d+ )?undefined",
         "citation {} has no bibliography entry"),
        (r"Reference `([^']+)' (?:on page \d+ )?undefined",
         "reference {} points at no label"),
    ):
        for name in sorted(set(re.findall(pattern, text))):
            findings.append(("FAIL", "undefined", message.format(repr(name))))
    if "There were multiply-defined labels" in text:
        findings.append(("NOTE", "labels", "the log reports multiply-defined labels"))
    return findings


def check_pdf(path):
    findings = []
    try:
        import fitz
    except ImportError:
        return findings
    doc = fitz.open(path)
    findings.append(("INFO", "length", f"{doc.page_count} pages"))
    text = "".join(page.get_text() for page in doc)
    named = sorted(set(re.findall(TOOL_NAMES, text, re.I)))
    if named:
        findings.append(("NOTE", "tool-names",
                         f"the compiled manuscript mentions {', '.join(named)}; check "
                         "that every mention is deliberate"))
    return findings


def report(findings, header=None):
    if header:
        print(header)
    if not findings:
        print("  no findings")
        return True
    for severity, code, message in findings:
        print(f"  {severity:<4}  {code:<18}  {message}")
    fails = sum(1 for f in findings if f[0] == "FAIL")
    notes = sum(1 for f in findings if f[0] == "NOTE")
    print(f"  -> {fails} FAIL, {notes} NOTE")
    return fails == 0


def main(argv):
    if not argv or {"-h", "--help"} & set(argv):
        print(__doc__)
        return 0 if argv else 2
    abstract_max, min_refs = 250, 30
    journal = bib_path = None
    for flag in ("--abstract-max", "--min-refs", "--journal", "--bib"):
        if flag in argv:
            index = argv.index(flag)
            value = argv[index + 1]
            argv = argv[:index] + argv[index + 2:]
            if flag == "--abstract-max":
                abstract_max = int(value)
            elif flag == "--min-refs":
                min_refs = int(value)
            elif flag == "--journal":
                journal = value
            else:
                bib_path = value
    tex = argv[0]
    findings = check_tex(tex, abstract_max) + check_log(tex)

    source = _strip_comments(Path(tex).read_text(encoding="utf-8", errors="replace"))
    if journal is None:
        match = re.search(r"\\journal\{([^}]*)\}", source)
        journal = match.group(1).strip() if match else None
    bib = Path(tex).with_name("references.bib") if bib_path is None else Path(bib_path)
    if bib.exists():
        findings += check_bibliography(bib, source, min_refs=min_refs, journal=journal)
    else:
        findings.append(("NOTE", "bibliography",
                         f"no bibliography found at {bib}; pass --bib to point at it"))

    for extra in argv[1:]:
        findings += check_pdf(extra)
    return 0 if report(findings, f"{tex}") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
