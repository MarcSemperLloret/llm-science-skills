"""Check a manuscript against the house front and end matter.

The front and end matter are fixed, which means deviations are detectable. They
are also invisible while writing: an author name carried over from an older
file, a funding string retyped with a different grant, an AI declaration that
still names the tool used two drafts ago. Every one of those has happened.

    python checkfront.py manuscript.tex [more.tex ...]

FAIL is a deviation from the house convention. NOTE needs a look.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

AUTHORS = ("Marc Semper", "Manuel Curado", "Jose F. Vicent")

# The long form is a real name but not the published one. It keeps coming back
# from older files, and it must not reach a submission.
WRONG_NAME = "Semper Lloret"

AFFILIATION = "Department of Computer Science and Artificial Intelligence"
GRANT = "PID2025-175296OB-I00"
FUNDER = "MICIU/AEI/10.13039/501100011033"
EQUAL = "All authors contributed equally"

TOOL_NAMES = (
    r"\b(ChatGPT|GPT-?[0-9]|OpenAI|Codex|Claude|Anthropic|Gemini|Copilot"
    r"|Llama|Mistral|DeepSeek|Perplexity)\b"
)


def _strip_comments(text):
    return re.sub(r"(?<!\\)%.*", "", text)


def _flat(text):
    """One line, single spaces: names and phrases wrap across lines in LaTeX."""
    return " ".join(text.split())


def check(path):
    findings = []
    tex = _strip_comments(Path(path).read_text(encoding="utf-8", errors="replace"))
    flat = _flat(tex)

    if WRONG_NAME in flat:
        findings.append(("FAIL", "author-name",
                         f"{WRONG_NAME!r} appears; the published form of the first "
                         "author is 'Marc Semper', without the second surname"))

    # A different collaboration is legitimate, so departing from the house
    # default is a NOTE. What is never legitimate is a name in the author list
    # that the CRediT statement does not cover, and that is checked against this
    # manuscript's own authors rather than against the defaults.
    declared = re.findall(r"\\author\[[^\]]*\]\{([^}]*)\}", tex)
    clean = []
    if declared:
        # The outer capture stops at the first closing brace, so an author
        # carrying \corref{cor1} arrives truncated as "Marc Semper\corref{cor1".
        # Everything from the first backslash on is markup, not a name.
        clean = [d.split("\\")[0].strip() for d in declared]
        clean = [c for c in clean if c]
        missing = [e for e in AUTHORS if not any(e in name for name in clean)]
        extra = [c for c in clean if not any(e in c for e in AUTHORS)]
        if missing or extra:
            findings.append(("NOTE", "author-list",
                             "this paper does not carry the default author list"
                             + (f"; missing {', '.join(map(repr, missing))}" if missing
                                else "")
                             + (f"; also {', '.join(map(repr, extra))}" if extra
                                else "")
                             + ". Confirm it is intended rather than inherited"))
        if not missing and AFFILIATION not in flat:
            findings.append(("FAIL", "affiliation",
                             "the default authors are present but the University of "
                             "Alicante affiliation block is missing or altered"))

    # The end matter is only expected where the end matter lives.
    if re.search(r"CRediT authorship contribution", tex):
        block = _flat(tex.split("CRediT authorship contribution")[1][:900])
        for name in clean:
            surname = name.split()[-1]
            if surname not in block:
                findings.append(("FAIL", "credit",
                                 f"{name!r} is in the author list and not in the "
                                 "CRediT statement; every author needs a role"))
        if EQUAL not in flat:
            findings.append(("NOTE", "credit",
                             f"the CRediT statement does not end with {EQUAL!r}; "
                             "correct if the contributions genuinely differed"))

    if re.search(r"section\*?\{Funding", tex):
        if GRANT not in flat or FUNDER not in flat:
            findings.append(("NOTE", "funding",
                             f"the funding section does not carry grant {GRANT} from "
                             f"{FUNDER}. Correct if this work was funded otherwise, "
                             "and never leave an inherited grant number in place"))

    declaration = re.search(r"generative AI(.*?)(\\section|\Z)", tex, re.S)
    if declaration:
        named = sorted(set(re.findall(TOOL_NAMES, declaration.group(1), re.I)))
        if named:
            findings.append(("FAIL", "ai-declaration",
                             f"the AI declaration names {', '.join(named)}; it says "
                             "what was done and names no product"))
        if re.search(r"accessed\s+\d", declaration.group(1), re.I):
            findings.append(("FAIL", "ai-declaration",
                             "the AI declaration carries an access date; drop it"))

    match = re.search(r"\\documentclass(\[[^\]]*\])?\{([^}]*)\}", tex)
    if match:
        options, cls = match.group(1) or "", match.group(2)
        if cls != "elsarticle":
            findings.append(("NOTE", "class",
                             f"document class is {cls!r}, not elsarticle"))
        elif "preprint" not in options or "12pt" not in options:
            findings.append(("NOTE", "class",
                             f"class options are {options}; the house setting is "
                             "[preprint,12pt,numbers,sort&compress]"))
        if "microtype" in tex and not ("lmodern" in tex or "newtxtext" in tex):
            findings.append(("FAIL", "packages",
                             "microtype without a scalable font package; the build "
                             "aborts. Add fontenc and lmodern"))
        if r"\begin{figure" in tex and "placeins" not in tex:
            findings.append(("NOTE", "packages",
                             "no placeins; floats drift past the bibliography"))

    return findings


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
    if not argv or {"-h", "--help"} & set(argv):
        print(__doc__)
        return 0 if argv else 2
    ok = True
    for path in argv:
        ok &= report(check(path), f"{path}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
