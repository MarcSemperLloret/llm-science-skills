"""Mechanical checks on the statistics a manuscript reports.

Most of what makes an analysis valid cannot be read off the text: whether the
unit of analysis is the unit that varies, whether the estimand matches the
question, whether the observations are independent. None of that is here.

What is here is the part a script can settle without knowing the design. A
percentage that no integer count could produce. A p value printed as zero. A
claim of significance with nothing to say how large the thing is. Twenty tests
and no mention of what that does to the error rate. Each of these has reached a
published paper, and each takes seconds to find.

    python statcheck.py manuscript.tex
    python statcheck.py manuscript.tex --alpha 0.01
    python statcheck.py results.md --max-tests 5

FAIL is arithmetically wrong or impossible. NOTE is something to justify before
a reviewer asks. A clean run says these particular defects are absent; it says
nothing about whether the inference is sound.

Standard library only.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# A percentage stated beside its denominator can be checked: some whole number
# of units out of that denominator has to round to it. This catches a mistyped
# digit, and it catches a figure that survived a re-run of the pipeline while
# its denominator changed underneath it.
# Deliberately tight. A loose version of this matched a percentage against the
# hour in "64.4% fall in 12:00-20:00" and against the integer part of "an odds
# ratio of 2.74", and reported both as arithmetically impossible. A FAIL that is
# wrong costs more than the finding is worth, so the denominator has to follow
# "of" directly and must not be the start of a time or a decimal.
PERCENT_OF = re.compile(
    r"(\d{1,3}(?:\.\d{1,2})?)\s*(?:\\)?%\s+of\s+(?:the\s+)?"
    r"(\d[\d,]{0,6})(?![\d.:])", re.I)
PERCENT_N = re.compile(
    r"(\d{1,3}(?:\.\d{1,2})?)\s*(?:\\)?%[^.;]{0,30}?"
    r"[(\[]\s*(?:n\s*=\s*)(\d[\d,]{0,6})\s*[)\]]", re.I)

PVALUE = re.compile(r"\bp\s*(?:-?\s*value)?\s*([<>=≤≥]{1,2})\s*(\d*\.\d+|\d+)", re.I)
# A claim that something *is* significant, not a mention of the concept.
SIGNIFICANT = re.compile(
    r"\b(?:was|were|is|are|remained?|becomes?)\s+(?:\w+\s+){0,2}significant\b"
    r"|\bstatistically significant\b|\bsignificantly\s+(?:higher|lower|greater"
    r"|larger|smaller|different|increased|decreased|associated|correlated)\b",
    re.I)
NOT_A_CLAIM = re.compile(
    r"\b(no|not|never|without|neither)\b[^.]{0,40}\bsignifican", re.I)
CORRECTION = re.compile(
    r"\b(Bonferroni|Holm|Benjamini|Hochberg|false discovery|FDR|Sidak|Tukey"
    r"|family-?wise|multiplicity|multiple (?:comparisons?|testing|tests))\b", re.I)
INTERVAL = re.compile(
    r"\b(\d{1,2}\s*\\?%\s*(?:CI|confidence|credible)|CI\b|confidence interval"
    r"|credible interval|\[\s*[-−+]?\d*\.?\d+\s*,\s*[-−+]?\d*\.?\d+\s*\])", re.I)
HEDGE = re.compile(
    r"\b(trend(?:ing)? (?:towards?|toward) significance|marginally significant"
    r"|approach\w* significance|borderline significan\w*|nearly significant)\b",
    re.I)
POWER = re.compile(r"\b(post-?hoc power|observed power|achieved power)\b", re.I)


def _strip(text):
    """Drop comments and the maths that would otherwise look like statistics."""
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = re.sub(r"\$[^$]*\$", " ", text)
    return text


def _sentences(text):
    return re.split(r"(?<=[.!?])\s+(?=[A-Z\\])", " ".join(text.split()))


def check_percentages(text):
    """A percentage has to be reachable from its own denominator."""
    findings = []
    seen = set()
    for pattern in (PERCENT_OF, PERCENT_N):
        for match in pattern.finditer(text):
            shown, denom = match.group(1), match.group(2).replace(",", "")
            key = (shown, denom)
            if key in seen:
                continue
            seen.add(key)
            n = int(denom)
            if not 1 < n <= 100000:
                continue
            places = len(shown.split(".")[1]) if "." in shown else 0
            value = float(shown)
            if n > 10 ** (places + 2):        # any value is reachable; nothing to say
                continue
            reachable = any(round(100 * k / n, places) == value
                            for k in range(n + 1))
            if not reachable:
                nearest = min((abs(100 * k / n - value), 100 * k / n)
                              for k in range(n + 1))[1]
                findings.append((
                    "FAIL", "percentage",
                    f"{shown}% of {n} is not attainable: no whole number out of "
                    f"{n} rounds to it, the nearest is {nearest:.{places}f}%. "
                    "Either the numerator, the denominator or the figure is stale"))
    return findings


def check_pvalues(text, alpha=0.05, max_tests=10):
    """Impossible values, unsupported claims, and unacknowledged multiplicity."""
    findings = []
    values = []
    for match in PVALUE.finditer(text):
        operator, raw = match.group(1), match.group(2)
        try:
            value = float(raw)
        except ValueError:
            continue
        values.append(value)
        if value > 1 or value < 0:
            findings.append(("FAIL", "p-range",
                             f"p {operator} {raw} is outside [0, 1]"))
        elif value == 0 and operator == "=":
            findings.append(("FAIL", "p-zero",
                             "p = 0 is not a probability a test returns; report "
                             "p < 0.001 with the precision the method supports"))
        elif operator == "=" and re.fullmatch(r"0\.0+", raw):
            findings.append(("NOTE", "p-zero",
                             f"p = {raw} rounds a positive number to zero; "
                             "report it as p < 0.001"))

    if len(values) > max_tests and not CORRECTION.search(text):
        findings.append((
            "NOTE", "multiplicity",
            f"{len(values)} p values are reported and no correction, false "
            "discovery rate or family-wise statement appears anywhere. Say which "
            "tests were confirmatory and what was done about the rest"))

    for sentence in _sentences(text):
        if (SIGNIFICANT.search(sentence) and not INTERVAL.search(sentence)
                and not NOT_A_CLAIM.search(sentence)):
            findings.append((
                "NOTE", "no-effect-size",
                f"significance claimed with no interval or effect size in the "
                f"same sentence: {sentence.strip()[:88]}..."))
    return findings


def check_language(text):
    """Phrases that describe a non-result as a partial result."""
    findings = []
    for match in HEDGE.finditer(text):
        findings.append(("NOTE", "hedged-null",
                         f"{match.group(0)!r}: a test either rejected or it did "
                         "not. Report the estimate and its interval and say what "
                         "the data could not resolve"))
    for match in POWER.finditer(text):
        findings.append(("NOTE", "post-hoc-power",
                         f"{match.group(0)!r} is a function of the p value and "
                         "adds nothing; report the interval, which says what "
                         "effect sizes remain compatible"))
    return findings


def report(findings, header=None):
    if header:
        print(header)
    if not findings:
        print("  no findings")
        return True
    seen = set()
    for severity, code, message in findings:
        if (code, message) in seen:
            continue
        seen.add((code, message))
        print(f"  {severity:<4}  {code:<16}  {message}")
    fails = sum(1 for f in findings if f[0] == "FAIL")
    notes = len(seen) - fails
    print(f"  -> {fails} FAIL, {notes} NOTE")
    return fails == 0


def main(argv):
    if not argv or {"-h", "--help"} & set(argv):
        print(__doc__)
        return 0 if argv else 2
    alpha, max_tests = 0.05, 10
    for flag in ("--alpha", "--max-tests"):
        if flag in argv:
            index = argv.index(flag)
            value = argv[index + 1]
            argv = argv[:index] + argv[index + 2:]
            if flag == "--alpha":
                alpha = float(value)
            else:
                max_tests = int(value)

    path = Path(argv[0])
    text = _strip(path.read_text(encoding="utf-8", errors="replace"))
    findings = (check_percentages(text)
                + check_pvalues(text, alpha, max_tests)
                + check_language(text))
    return 0 if report(findings, f"{path}") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
