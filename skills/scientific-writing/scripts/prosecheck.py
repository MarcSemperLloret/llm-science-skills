"""Measure the writing habits that make a manuscript read like generated text.

None of these is a grammar error, and a spell checker sees none of them. They
are habits: a bold label at the head of every paragraph doing the job a
transition should do, a word italicised for stress, a paragraph that recites a
table, the same sentence appearing in the results and again in the discussion,
a wide table rescued by shrinking the type.

    python prosecheck.py manuscript.tex
    python prosecheck.py manuscript.tex --max-columns 6

FAIL is a defect that will reach the page. NOTE is a habit worth looking at,
reported with the worst instance so it can be judged rather than obeyed. The
thresholds are conventions, not findings: pass your own if the field differs.

Standard library only.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Words that carry no content on their own. Italicising one of these is stress
# marking: the emphasis is doing work that word order should do.
FUNCTION_WORDS = {
    "not", "and", "or", "but", "the", "a", "an", "is", "are", "was", "were",
    "be", "been", "very", "only", "also", "both", "all", "any", "each", "this",
    "that", "these", "those", "if", "then", "when", "where", "which", "who",
    "how", "why", "before", "after", "same", "different", "more", "less",
    "must", "can", "do", "does", "did", "no", "never", "always", "here",
}

HEDGE = re.compile(
    r"\b(may|might|could|possibly|potentially|perhaps|appears? to|seems? to"
    r"|tends? to|somewhat|relatively|arguably|it is possible that)\b", re.I)

# \small and \footnotesize are ordinary table sizes in a 12pt class.
# These two are not: they are a width problem being hidden.
SHRINK = re.compile(r"\\(tiny|scriptsize)\b")


def _strip_comments(text):
    return re.sub(r"(?<!\\)%.*", "", text)


def _body(tex):
    """The prose only.

    From the first section to the end matter, with floats removed. Front matter
    is metadata, the CRediT block is not written prose, and a tabular counted as
    a paragraph reports its own cells as numeric density.
    """
    text = tex.split("\\section{", 1)[-1] if "\\section{" in tex else tex
    text = re.split(r"\\section\*\{(?:CRediT|Funding|Declaration|Data)", text)[0]
    for environment in ("table", "table\\*", "figure", "figure\\*", "tabular",
                        "equation", "align", "lstlisting", "verbatim"):
        text = re.sub(r"\\begin\{" + environment + r"\}.*?\\end\{"
                      + environment + r"\}", " ", text, flags=re.S)
    return text


def _words(text):
    return len(re.sub(r"\\[a-zA-Z]+\*?", " ", text).split())


def _paragraphs(text, minimum=40):
    return [p for p in re.split(r"\n\s*\n", text) if _words(p) >= minimum]


def check_leadins(tex):
    """Bold or italic labels standing in for narrative structure."""
    findings = []
    hits = re.findall(r"\n\s*\n\s*\\(?:textbf|emph|textit)\{([^}]{1,60})\}",
                      tex)
    if len(hits) >= 3:
        findings.append((
            "FAIL" if len(hits) >= 4 else "NOTE", "lead-in",
            f"{len(hits)} paragraphs open with a bold or italic label "
            f"({', '.join(repr(h) for h in hits[:3])} ...). Formatting is "
            "standing in for narrative structure; if consecutive paragraphs need "
            "labels to explain their purpose, the section is organised wrongly"))
    elif hits:
        findings.append(("NOTE", "lead-in",
                         f"{len(hits)} paragraph(s) open with a label: "
                         f"{', '.join(repr(h) for h in hits)}. Fine as an "
                         "exception, a habit if it spreads"))
    return findings


def check_emphasis(body, per_thousand=3.0):
    """Emphasis used for stress rather than for meaning."""
    findings = []
    words = _words(body)
    marks = re.findall(r"\\(?:emph|textit)\{([^}]{1,60})\}", body)
    if not words:
        return findings
    rate = 1000 * len(marks) / words
    stress = [m for m in marks
              if m.strip().lower().strip(".,;:") in FUNCTION_WORDS]
    if rate > per_thousand:
        findings.append((
            "NOTE", "emphasis",
            f"{len(marks)} italicised spans, {rate:.1f} per 1000 words. "
            "Reserve italics for notation, taxa and defined terms"))
    if len(stress) >= 3:
        findings.append((
            "NOTE", "emphasis-stress",
            f"{len(stress)} of them are function words "
            f"({', '.join(repr(s) for s in stress[:5])}). Emphasising these is "
            "stress marking; scientific prose does it with word order"))
    bold = re.findall(r"\\textbf\{([^}]{1,60})\}", body)
    if 1000 * len(bold) / words > per_thousand:
        findings.append(("NOTE", "bold",
                         f"{len(bold)} bold spans in the body, "
                         f"{1000 * len(bold) / words:.1f} per 1000 words"))
    return findings


def check_density(body, limit=6.0):
    """Paragraphs that recite a table instead of stating a pattern."""
    findings = []
    worst = (0, "")
    total = 0
    paragraphs = _paragraphs(body)
    for paragraph in paragraphs:
        count = len(re.findall(r"\d+\.\d+", paragraph))
        total += count
        if count > worst[0]:
            worst = (count, " ".join(paragraph.split())[:80])
    if worst[0] > limit:
        findings.append((
            "NOTE", "numeric-density",
            f"one paragraph carries {worst[0]} decimal figures: {worst[1]}... "
            "A paragraph should communicate a pattern; the numbers needed only "
            "for reproducibility belong in a table"))
    if paragraphs:
        mean = total / len(paragraphs)
        findings.append(("INFO", "numeric-density",
                         f"{mean:.1f} decimal figures per substantial paragraph "
                         f"across {len(paragraphs)}"))
    return findings


def check_tables(tex, max_columns=8):
    """Width, and the font size used to hide it."""
    findings = []
    for spec in re.findall(r"\\begin\{tabular[*x]?\}(?:\[[^\]]*\])?\{([^}]*)\}", tex):
        columns = len(re.findall(r"[lcrpXSm]", re.sub(r"@\{[^}]*\}", "", spec)))
        if columns > max_columns:
            findings.append((
                "NOTE", "table-width",
                f"a table declares {columns} columns. Before touching the type "
                "size: drop what is not needed, cut decimal places, shorten the "
                "headers, split it, or move the detail to the supplement"))
    for match in re.finditer(r"\\begin\{table\*?\}(.{0,2500}?)\\end\{table\*?\}",
                             tex, re.S):
        block = match.group(1)
        shrink = SHRINK.search(block)
        if shrink and "tabular" in block:
            findings.append((
                "NOTE", "table-shrink",
                f"a table is set in \\{shrink.group(1)}. Shrinking the type "
                "hides the width problem rather than solving it, and it is the "
                "first thing a copy editor reverses"))
        if "\\resizebox" in block:
            findings.append((
                "NOTE", "table-resize",
                "a table is wrapped in \\resizebox, which scales the type to "
                "whatever fits and makes it unpredictable across the paper"))
    return findings


def check_repetition(body):
    """The same sentence, or nearly, appearing more than once."""
    findings = []
    flat = " ".join(body.split())
    sentences = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", flat)
                 if len(s.split()) >= 10]
    seen = Counter()
    for sentence in sentences:
        key = " ".join(sorted(set(
            w for w in re.sub(r"[^a-z ]", " ", sentence.lower()).split()
            if len(w) > 4)))[:120]
        if key:
            seen[key] += 1
    repeats = [k for k, n in seen.items() if n > 1]
    if repeats:
        findings.append((
            "NOTE", "repetition",
            f"{len(repeats)} statement(s) appear more than once in substantially "
            "the same words. A claim restated in the discussion should add "
            "something to it, not repeat it"))
    return findings


def check_hedging(body, ceiling=6.0):
    """Over-defensive writing, which reviewers do complain about."""
    findings = []
    words = _words(body)
    hedges = HEDGE.findall(body)
    if not words:
        return findings
    rate = 1000 * len(hedges) / words
    findings.append(("INFO", "hedging",
                     f"{len(hedges)} hedging words, {rate:.1f} per 1000"))
    if rate > ceiling:
        findings.append((
            "NOTE", "over-hedged",
            f"hedging runs at {rate:.1f} per 1000 words. Hedging should match "
            "the uncertainty in the evidence, not anxiety about reviewers; a "
            "result the data establish directly should be stated directly"))
    return findings


def check_openings(body):
    """Paragraphs that all start the same way."""
    findings = []
    openings = Counter()
    for paragraph in _paragraphs(body, minimum=25):
        words = " ".join(paragraph.split()).split()
        opening = " ".join(w for w in words[:3] if not w.startswith("\\"))
        if opening:
            openings[opening.lower().strip(",.")] += 1
    for opening, count in openings.most_common(2):
        if count >= 4:
            findings.append((
                "NOTE", "opening",
                f"{count} paragraphs open with {opening!r}. Vary the entry, or "
                "the reader stops registering where a new point starts"))
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
    max_columns = 8
    if "--max-columns" in argv:
        index = argv.index("--max-columns")
        max_columns = int(argv[index + 1])
        argv = argv[:index] + argv[index + 2:]

    path = Path(argv[0])
    tex = _strip_comments(path.read_text(encoding="utf-8", errors="replace"))
    body = _body(tex)
    findings = (check_leadins(body)
                + check_emphasis(body)
                + check_density(body)
                + check_tables(tex, max_columns)
                + check_repetition(body)
                + check_hedging(body)
                + check_openings(body))
    return 0 if report(findings, f"{path}  ({_words(body)} words)") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
