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
    "data availability": r"[Dd]ata availability",
    "AI declaration": r"generative AI",
}

# Naming a model, a vendor or an access date in the AI declaration is easy to
# leave behind from an earlier draft, and it is exactly what a screening editor
# reads first.
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
    if not argv:
        print(__doc__)
        return 2
    abstract_max = 250
    if "--abstract-max" in argv:
        index = argv.index("--abstract-max")
        abstract_max = int(argv[index + 1])
        argv = argv[:index] + argv[index + 2:]
    tex = argv[0]
    findings = check_tex(tex, abstract_max) + check_log(tex)
    for extra in argv[1:]:
        findings += check_pdf(extra)
    return 0 if report(findings, f"{tex}") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
