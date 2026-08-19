"""Look for the defects that produce a clean, plausible, wrong result.

An analysis that crashes costs an afternoon. An analysis that returns a tidy
number computed from a column of disguised missing values costs a paper. The
checks here are the mechanical half of that problem: the source defects and
saturation signatures that a script can see without knowing the science.

    python datasmell.py table.csv
    python datasmell.py table.csv --group station     # rates per group, not overall
    python datasmell.py table.csv --expect height=2:60
    python datasmell.py results.csv --metric jaccard,regret

FAIL is a defect that will change a result. NOTE is something to look at before
believing the number. Nothing here proves an analysis is sound; a clean run
means only that these particular failures are absent.

Standard library only, so it runs wherever the data does.
"""

from __future__ import annotations

import csv
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Values that mean "no observation" in some archive and "a real measurement" to
# whatever reads the file next. Zero is on the list because it is the one that
# looks least like a sentinel and does the most damage: a temperature archive
# storing absent as 0.0 biases a spatial field by degrees, and structures the
# bias by station.
SENTINELS = (0.0, -1.0, -9.0, -99.0, -999.0, -9999.0, -99.99, -999.9,
             9999.0, 99999.0, -32768.0, 32767.0, 6999.0)

MISSING_TOKENS = {"", "na", "n/a", "nan", "null", "none", "-", "--", "?"}


def _rows(path, limit=None):
    with open(path, newline="", encoding="utf-8", errors="replace") as handle:
        sample = handle.read(8192)
        handle.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(handle, dialect=dialect)
        for index, row in enumerate(reader):
            if limit and index >= limit:
                break
            yield row


def _number(text):
    if text is None:
        return None
    text = text.strip()
    if text.lower() in MISSING_TOKENS:
        return None
    # A decimal comma is a decimal point everywhere the data was written.
    if re.fullmatch(r"[+-]?\d{1,3}(\.\d{3})*,\d+", text):
        text = text.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"[+-]?\d+,\d+", text):
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def _columns(path, limit=None):
    values = defaultdict(list)
    order = []
    for row in _rows(path, limit):
        for name, raw in row.items():
            if name is None:
                continue
            if name not in values:
                order.append(name)
            values[name].append(raw)
    return order, values


def _median(numbers):
    ordered = sorted(numbers)
    middle = len(ordered) // 2
    if not ordered:
        return None
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def check_missing(order, values):
    """Columns that are empty, constant, or missing in a suspicious pattern."""
    findings = []
    for name in order:
        column = values[name]
        present = [v for v in column if (v or "").strip().lower() not in MISSING_TOKENS]
        if not present:
            findings.append(("NOTE", "all-missing",
                             f"{name!r} is empty in every row; harmless if nothing "
                             "reads it, and a defect the moment something does"))
            continue
        if len(set(present)) == 1 and len(present) > 3:
            findings.append(("NOTE", "constant",
                             f"{name!r} takes one value, {present[0]!r}, in all "
                             f"{len(present)} rows that have it"))
        share = 1 - len(present) / len(column)
        if 0.8 <= share < 1:
            findings.append(("NOTE", "mostly-missing",
                             f"{name!r} is missing in {share:.0%} of rows"))
    return findings


def check_sentinels(order, values, group=None):
    """A value that means absence and is being read as a measurement.

    Reported per group when one is given, because the damage is done by the
    structure rather than the rate: a defect at 0.001% in one station and 5.5%
    in another is a spatially organised bias, and it can imitate the signal
    being looked for. An overall rate hides exactly that.
    """
    findings = []
    groups = values.get(group) if group else None
    for name in order:
        if name == group:
            continue
        numbers = [(index, _number(v)) for index, v in enumerate(values[name])]
        numbers = [(i, n) for i, n in numbers if n is not None]
        if len(numbers) < 20:
            continue
        plain = [n for _, n in numbers]
        distinct = len(set(plain))
        if distinct < 5:                      # a coded category, not a measurement
            continue
        # Compute the centre once. Calling _median inside the comprehension
        # sorts the column once per row, which is fine on a test fixture and
        # hangs on a real archive.
        centre = _median(plain)
        spread = _median([abs(n - centre) for n in plain]) or 0.0
        for sentinel in SENTINELS:
            hits = [i for i, n in numbers if n == sentinel]
            if not hits:
                continue
            share = len(hits) / len(numbers)
            # A sentinel is a spike: far more frequent than the values around it
            # and, for zero, out of keeping with the spread of the column.
            neighbours = sum(1 for n in plain
                             if n != sentinel and abs(n - sentinel) <= max(spread / 8, 1e-9))
            if len(hits) < 3 or len(hits) <= neighbours:
                continue
            message = (f"{name!r} contains {sentinel:g} {len(hits)} times "
                       f"({share:.2%}), far more often than any neighbouring "
                       "value; check it is a measurement and not a coded absence")
            if groups:
                rates = Counter()
                totals = Counter()
                for index, number in numbers:
                    key = groups[index]
                    totals[key] += 1
                    if number == sentinel:
                        rates[key] += 1
                per = sorted(((rates[k] / totals[k], k) for k in totals if totals[k] > 5),
                             reverse=True)
                if per and per[0][0] > 4 * (per[-1][0] + 1e-9):
                    message += (f"; the rate runs from {per[-1][0]:.2%} in "
                                f"{per[-1][1]!r} to {per[0][0]:.2%} in {per[0][1]!r}, "
                                "so the bias is structured, not random")
                    findings.append(("FAIL", "sentinel-structured", message))
                    continue
            findings.append(("NOTE", "sentinel", message))
    return findings


def check_duplicate_series(order, values):
    """Distinct labels carrying one series.

    A network can publish nine station names that are all the same instrument,
    and every spatial statistic computed over them is then a statement about one
    sensor. Nothing about the file looks wrong.
    """
    findings = []
    signatures = defaultdict(list)
    for name in order:
        numbers = [_number(v) for v in values[name]]
        present = [(i, n) for i, n in enumerate(numbers) if n is not None]
        if len(present) < 20 or len({n for _, n in present}) < 5:
            continue
        signatures[tuple(present)].append(name)
    for names in signatures.values():
        if len(names) > 1:
            findings.append(("FAIL", "duplicate-series",
                             f"{', '.join(repr(n) for n in names)} are the same "
                             "series value for value; they are one measurement "
                             "under several labels, not several measurements"))
    return findings


def check_saturation(order, values, metrics=()):
    """Metrics pinned at a bound.

    A stability index of exactly 1.000, or a regret of exactly zero, is usually
    read as agreement. It is at least as often the arithmetic of an empty
    comparison: nothing varied, so nothing disagreed. The distinction is the
    denominator, and the denominator is what the table never shows.
    """
    findings = []
    wanted = [m.strip().lower() for m in metrics if m.strip()]
    for name in order:
        low = name.lower()
        if wanted and not any(m in low for m in wanted):
            continue
        numbers = [_number(v) for v in values[name]]
        numbers = [n for n in numbers if n is not None]
        if len(numbers) < 10:
            continue
        for bound in (0.0, 1.0, 100.0):
            share = sum(1 for n in numbers if n == bound) / len(numbers)
            if share >= 0.25:
                findings.append((
                    "NOTE", "saturated",
                    f"{name!r} is exactly {bound:g} in {share:.0%} of rows; if this "
                    "is a stability or regret metric, report the denominator and a "
                    "saturation flag beside it, because an empty comparison and a "
                    "perfect agreement print the same number"))
    return findings


def check_dates(order, values):
    """Date strings whose day and month cannot be told apart."""
    findings = []
    pattern = re.compile(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})|"
                         r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})")
    for name in order:
        parsed = [pattern.match((v or "").strip()) for v in values[name]]
        parsed = [m for m in parsed if m]
        if len(parsed) < 20:
            continue
        ambiguous = 0
        for match in parsed:
            if match.group(1):
                first, second = int(match.group(2)), int(match.group(3))
            else:
                first, second = int(match.group(4)), int(match.group(5))
            if 1 <= first <= 12 and 1 <= second <= 12:
                ambiguous += 1
        share = ambiguous / len(parsed)
        if share > 0.2:
            findings.append(("NOTE", "ambiguous-date",
                             f"{name!r}: in {share:.0%} of rows both components are "
                             "12 or less, so a transposed day and month is "
                             "undetectable here; rebuild the timestamp from the "
                             "source payload rather than from this string"))
    return findings


def check_expected(order, values, expectations):
    """Columns whose values sit outside the range their name implies.

    A field called `value` that holds gross floor area rather than height gives
    a median of eighty for a city of flats. The name is not the semantics, and
    the only defence is to say out loud what the number should look like.
    """
    findings = []
    for name, (low, high) in expectations.items():
        matches = [c for c in order if c.lower() == name.lower()]
        if not matches:
            findings.append(("NOTE", "expect",
                             f"no column named {name!r} to check against "
                             f"{low:g}--{high:g}"))
            continue
        numbers = [_number(v) for v in values[matches[0]]]
        numbers = [n for n in numbers if n is not None]
        if not numbers:
            continue
        middle = _median(numbers)
        outside = sum(1 for n in numbers if not low <= n <= high) / len(numbers)
        if not low <= middle <= high:
            findings.append(("FAIL", "semantics",
                             f"{matches[0]!r} has median {middle:g}, outside the "
                             f"stated range {low:g}--{high:g}; the field probably "
                             "does not hold what its name suggests"))
        elif outside > 0.25:
            findings.append(("NOTE", "out-of-range",
                             f"{matches[0]!r}: {outside:.0%} of values fall outside "
                             f"{low:g}--{high:g}"))
    return findings


def report(findings, header=None):
    if header:
        print(header)
    if not findings:
        print("  no findings")
        return True
    for severity, code, message in findings:
        print(f"  {severity:<4}  {code:<20}  {message}")
    fails = sum(1 for f in findings if f[0] == "FAIL")
    notes = sum(1 for f in findings if f[0] == "NOTE")
    print(f"  -> {fails} FAIL, {notes} NOTE")
    return fails == 0


def main(argv):
    if not argv or {"-h", "--help"} & set(argv):
        print(__doc__)
        return 0 if argv else 2
    group, metrics, limit = None, (), None
    expectations = {}
    for flag in ("--group", "--metric", "--limit", "--expect"):
        while flag in argv:
            index = argv.index(flag)
            value = argv[index + 1]
            argv = argv[:index] + argv[index + 2:]
            if flag == "--group":
                group = value
            elif flag == "--metric":
                metrics = value.split(",")
            elif flag == "--limit":
                limit = int(value)
            else:
                name, _, span = value.partition("=")
                low, _, high = span.partition(":")
                expectations[name] = (float(low), float(high))

    path = Path(argv[0])
    order, values = _columns(path, limit)
    if not order:
        print(f"{path}: no columns read")
        return 2
    findings = (check_missing(order, values)
                + check_sentinels(order, values, group)
                + check_duplicate_series(order, values)
                + check_saturation(order, values, metrics)
                + check_dates(order, values)
                + check_expected(order, values, expectations))
    rows = len(values[order[0]])
    return 0 if report(findings, f"{path}  ({rows} rows, {len(order)} columns)") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
