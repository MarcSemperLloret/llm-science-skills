"""Consistency checks a reviewer performs with a pencil, done mechanically.

A reviewer who finds one number in the abstract that does not appear anywhere in
the results stops trusting the rest of the paper. The drift is easy to create --
a value is refined late and the abstract keeps the old one -- and almost
impossible to see by reading, because both numbers look right in their own
place.

    python reviewcheck.py manuscript.tex

FAIL is an inconsistency a reviewer will find. NOTE is a habit that invites one.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

# A number with enough shape to be a reported quantity rather than a section
# number, a year or an equation index. The separator before the per-cent sign
# allows LaTeX spacing macros: 51\,\% is one quantity, not the integer 51.
NUMBER = re.compile(
    r"(?<![\w.])(\d+\.\d+|\d{1,3}(?:,\d{3})+|\d+)"
    r"(?:\s|\\,|\\;|\\ |~|\\thinspace)*(\\?%|\\percent)?"
)

# Conventional levels, not results: an abstract that says "95% CI" is not
# quoting a finding the body must repeat.
CONVENTION = {"90%", "95%", "99%", "50%"}

HEDGE_FREE = re.compile(
    r"\b(prove[sd]?|demonstrat\w+|establish\w+|confirm\w+)\b", re.I)
CAUSAL = re.compile(
    r"\b(caus\w+|because of|due to|leads? to|results? in|drives?|driven by)\b", re.I)


def _strip(text):
    text = re.sub(r"(?<!\\)%.*", "", text)
    return text


def _numbers(text):
    """Reported quantities, as strings, ignoring years and small integers."""
    found = []
    for match in NUMBER.finditer(text):
        value, percent = match.group(1), match.group(2)
        if re.fullmatch(r"(19|20)\d\d", value):
            continue
        if "." not in value and "," not in value and not percent and len(value) < 3:
            continue
        found.append(value.replace(",", "") + ("%" if percent else ""))
    return found


def check(path):
    findings = []
    tex = _strip(Path(path).read_text(encoding="utf-8", errors="replace"))

    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    if not match:
        findings.append(("NOTE", "abstract", "no abstract environment found"))
        return findings
    abstract, body = match.group(1), tex[match.end():]

    # Compare numerically with rounding, not as text. An abstract quotes one
    # decimal where the body carries two, and 2.8 is not a prefix of 2.79 even
    # though 2.79 is exactly what 2.8 means.
    body_values = []
    for token in _numbers(body):
        try:
            body_values.append(float(token.rstrip("%")))
        except ValueError:
            pass

    missing = []
    for value in dict.fromkeys(_numbers(abstract)):
        if value in CONVENTION:
            continue
        bare = value.rstrip("%")
        try:
            quoted = float(bare)
        except ValueError:
            continue
        places = len(bare.split(".")[1]) if "." in bare else 0
        # An abstract routinely states as a percentage what the results state as
        # a fraction: 55.8% in front, 0.558 behind. Reporting that as a value
        # that appears nowhere sends the author hunting for a drift that is not
        # there, and the next real drift is trusted less for it.
        targets = [quoted]
        if value.endswith("%"):
            targets.append(quoted / 100)
        elif quoted <= 1:
            targets.append(quoted * 100)
        if any(round(candidate, places) == target
               or round(candidate, places + 2) == round(target, places + 2)
               for candidate in body_values for target in targets):
            continue
        missing.append(value)
    for value in missing:
        findings.append(("FAIL", "abstract-drift",
                         f"the abstract reports {value} and no such value appears in "
                         "the body; either it moved or the abstract was not updated"))

    for pattern, code, message in (
        (HEDGE_FREE, "over-claim",
         "states a result as proven or established; in an observational design a "
         "reviewer reads that as over-claiming"),
        (CAUSAL, "causal-language",
         "uses causal language; check that the design supports it and not only an "
         "association"),
    ):
        hits = Counter(m.group(0).lower() for m in pattern.finditer(abstract))
        if hits:
            words = ", ".join(f"{w} x{c}" if c > 1 else w for w, c in hits.items())
            findings.append(("NOTE", code, f"abstract {message}: {words}"))

    if re.search(r"\bp\s*[<=>]\s*0?\.\d+", tex) and not re.search(
            r"\b(correct\w+|Bonferroni|Holm|Benjamini|false discovery|family-wise)\b",
            tex, re.I):
        findings.append(("NOTE", "multiplicity",
                         "p-values are reported and no multiplicity correction is "
                         "mentioned; a reviewer will ask how many tests were run"))

    if re.search(r"\bsignifican\w+", tex, re.I) and not re.search(
            r"\b(confidence interval|CI\b|credible interval|standard error)\b", tex):
        findings.append(("NOTE", "significance",
                         "significance is claimed without an interval anywhere in the "
                         "text; report the estimate and its uncertainty"))

    limitations = re.search(r"\\section\*?\{[^}]*[Ll]imitation", tex)
    if not limitations and not re.search(r"\blimitations?\b", tex, re.I):
        findings.append(("NOTE", "limitations",
                         "no limitations are stated anywhere; every reviewer asks"))

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
