"""Smoke tests for the checkers, offline and fast.

Every case here exists because the behaviour it pins broke silently at least
once. That is the selection rule: not coverage, but the specific failures that
produced a plausible wrong answer rather than an error, because those are the
ones nobody notices. A checker that cannot fail loudly will fail quietly.

    python selftest.py

No network, no fixtures, a second or two. Run it after editing any asset.
"""

from __future__ import annotations

import importlib.util
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FAILURES: list[str] = []


def load(relative):
    path = ROOT / "skills" / relative
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(label, condition):
    if condition:
        print(f"  ok    {label}")
    else:
        print(f"  FAIL  {label}")
        FAILURES.append(label)


print("every skill's frontmatter is valid YAML")
# One description contained a colon followed by a space, which a plain YAML
# scalar cannot hold. It parsed nowhere strict and nothing said so.
import re as _re
try:
    import yaml as _yaml
except ImportError:
    _yaml = None
for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
    block = _re.match(r"---\n(.*?)\n---", skill.read_text(encoding="utf-8"), _re.S)
    ok = block is not None
    if ok and _yaml is not None:
        try:
            data = _yaml.safe_load(block.group(1))
            ok = bool(data.get("name")) and bool(data.get("description"))
        except Exception:
            ok = False
    check(f"{skill.parent.name} frontmatter", ok)

print("\nevery script answers --help")
# --help is how an agent discovers a tool. These treated it as a filename and
# died with a traceback.
import subprocess as _sub
for script in sorted((ROOT / "skills").rglob("*.py")):
    done = _sub.run([sys.executable, str(script), "--help"],
                    capture_output=True, text=True)
    check(f"{script.name} --help", done.returncode == 0 and bool(done.stdout.strip()))

print("\nno control characters in any asset")
# A backslash escape eaten before it reaches the file turns \b into a backspace.
# The pattern then requires a control character that never appears, matches
# nothing, and reports every manuscript as making no claim. This happened twice.
for source in sorted(list((ROOT / "skills").rglob("*.py"))
                     + list((ROOT / "skills").rglob("*.md"))):
    text = source.read_text(encoding="utf-8")
    stray = {c for c in text if ord(c) < 9 or 11 <= ord(c) < 32}
    check(f"{source.parent.name}/{source.name}", not stray)

print("\nnovelty is recognised in both registers")
deskcheck = load("desk-reject-simulation/scripts/deskcheck.py")
litcheck = load("literature-check/scripts/litcheck.py")
for pattern_name, pattern in (("deskcheck", deskcheck.NOVELTY),
                              ("litcheck", litcheck.NOVELTY)):
    check(f"{pattern_name}: boastful register",
          bool(pattern.search("To our knowledge, no previous study has done this")))
    check(f"{pattern_name}: gap register",
          bool(pattern.search("a gap remains, in that none of them couples A to B")))
    check(f"{pattern_name}: not ordinary methods prose",
          not pattern.search("none of these observations enters the field"))

print("\nbibliography entries are found however they are laid out")
ONE_LINE = "@article{k2024, title={{A} {T}itle}, journal={Water Research}, year={2024} }"
HOUSE = """@article{k2024,
  title   = {A Title},
  journal = {Water Research},
  year    = {2024}
}"""
for name, module in (("deskcheck", deskcheck), ("litcheck", litcheck)):
    for layout, text in (("one line", ONE_LINE), ("house style", HOUSE)):
        check(f"{name}: {layout}", len(list(module.split_entries(text))) == 1)

print("\nfield values survive brace-protected capitals")
fields = litcheck._fields(
    ' title = {{E}urope and the {W}orld}, year = {2019}, doi = {10.1/x} ')
check("title kept whole", fields.get("title") == "{E}urope and the {W}orld")
check("year not lost after the protected brace", fields.get("year") == "2019")

print("\na journal is not a journal whose name contains it")
litsearch = load("literature-check/scripts/litsearch.py")
key = litsearch._venue_key
check("Internet of Things != IEEE Internet of Things Journal",
      key("Internet of Things") != key("IEEE Internet of Things Journal"))
check("Water Research != Water Research X",
      key("Water Research") != key("Water Research X"))
check("The Lancet == Lancet", key("The Lancet") == key("Lancet"))

print("\ntitles keep their capitals and keys keep their letters")
protected = litsearch._protect_caps("SARS-CoV-2 RNA in wastewater anticipated COVID-19")
check("acronyms braced", "{SARS-CoV-2}" in protected and "{RNA}" in protected)
check("ordinary words left alone", " in wastewater " in protected)
entry = '@article{X_2018, title={T}, author={Muñoz, Ana and Celiński-Mysław, B}, year={2018}}'
check("accents folded, letters kept", litsearch._citekey(entry) == "munoz2018")
entry2 = '@article{X_2020, title={T}, author={Celiński-Mysław, B}, year={2020}}'
check("stroked l survives folding", litsearch._citekey(entry2) == "celinskimyslaw2020")

print("\nan abstract percentage matches a fraction in the body")
# 55.8% in front and 0.558 behind are the same number. Reporting a drift that is
# not there is how a checker gets ignored when the drift is real.
reviewcheck = load("peer-review-simulation/scripts/reviewcheck.py")
sample = ROOT / "_selftest_sample.tex"
sample.write_text(
    "\\begin{abstract}The design forfeits 55.8\\% of the attainable range.\n"
    "\\end{abstract}\nThe empirical design lost a median 0.558 of the test range.\n",
    encoding="utf-8")
try:
    drift = [f for f in reviewcheck.check(sample) if f[1] == "abstract-drift"]
finally:
    sample.unlink()
check("no false drift on a percentage/fraction pair", not drift)

print("\nthe statistics checker fires on errors and not on prose")
# It first reported a percentage as impossible because it had matched the hour
# in "64.4% fall in 12:00-20:00" and the integer part of "an odds ratio of 2.74".
# A FAIL that is wrong is worse than a miss, so both directions are pinned.
statcheck = load("statistical-analysis/scripts/statcheck.py")
BAD = ("We found 43.5\\% of the 106 evaluable episodes, with p = 0.000. "
       "The effect was statistically significant.")
GOOD = ("Of the cold episodes 64.4\\% fall in 12:00--20:00, and the odds ratio "
        "was 2.74. Strong detections were 43.4\\% of the 106 evaluable episodes "
        "(95\\% CI 1.65--5.36). No injection-level significance test was performed.")
check("an unreachable percentage is a FAIL",
      any(f[0] == "FAIL" for f in statcheck.check_percentages(statcheck._strip(BAD))))
check("a clock time is not a denominator",
      not statcheck.check_percentages(statcheck._strip(GOOD)))
check("p = 0.000 is caught",
      any(f[1] == "p-zero" for f in statcheck.check_pvalues(statcheck._strip(BAD))))
check("a mention of significance is not a claim",
      not any(f[1] == "no-effect-size"
              for f in statcheck.check_pvalues(statcheck._strip(GOOD))))

print("\ndata smells fire on the failures they were written for")
datasmell = load("silent-failure-audit/scripts/datasmell.py")
import csv as _csv, random as _random
_random.seed(7)
fixture = ROOT / "_selftest_smell.csv"
rows = []
for i in range(600):
    station = "A" if i % 2 else "C"
    temp = round(_random.gauss(22, 4), 1)
    if station == "C" and _random.random() < 0.08:
        temp = 0.0
    shared = round(_random.gauss(15, 3), 2)
    rows.append({"station": station, "temp": temp,
                 "sensor_1": shared, "sensor_2": shared})
with open(fixture, "w", newline="", encoding="utf-8") as handle:
    writer = _csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
try:
    order, values = datasmell._columns(fixture)
    codes = {c for _, c, _ in datasmell.check_sentinels(order, values, "station")}
    check("a sentinel structured by group is a FAIL", "sentinel-structured" in codes)
    dup = datasmell.check_duplicate_series(order, values)
    check("one series under two labels is caught", any(c == "duplicate-series" for _, c, _ in dup))
finally:
    fixture.unlink()

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILED: " + "; ".join(FAILURES))
    sys.exit(1)
print("all checks passed")
