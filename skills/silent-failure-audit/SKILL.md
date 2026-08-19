---
name: silent-failure-audit
description: Find the analysis failures that return a plausible result instead of an error. Use when a result looks clean, when a pipeline has been re-run after a change, before freezing an analysis, before writing up a number, and whenever a figure seems too good. Provides a data-defect scanner and a protocol of deliberate provocations - negative controls, label permutation, saturation flags, recomputation from source - that make a quiet failure loud. Do not use as a substitute for a statistical review.
---

# Silent failure audit

An analysis that crashes costs an afternoon. An analysis that returns a tidy
number computed from a column of disguised missing values costs a paper, and it
costs it much later, when someone else finds it.

The failures worth hunting share one property: they produce a result that looks
right. Not a warning, not an exception, not an implausible value on the face of
it. A stability index of exactly 1.000. A median building height of eighty
metres. An empty result set, well formed, returned with HTTP 200.

## The result that is too clean

In a documented audit of sixteen such failures in one project, **thirteen of the
sixteen wrong results were cleaner than the correct ones**. That is not a
coincidence, it is the mechanism. A defect usually removes variation: it
collapses a comparison, empties a set, replaces a spread of measurements with
one repeated constant. Removing variation is exactly what makes a result look
decisive.

So the alarm is not an outlier or an impossible value. The alarm is **the absence
of a mechanical reason for the result you are looking at**. Before believing a
clean number, be able to say which physical or statistical process produced it.
If the only account you can give is "the effect is strong", keep going.

## The mechanical half

```bash
python datasmell.py table.csv
python datasmell.py table.csv --group station          # rates per group
python datasmell.py results.csv --metric jaccard,regret
python datasmell.py buildings.csv --expect height=2:60
```

It reads a CSV with the standard library alone and looks for the defects a
script can see: a value that means absence being read as a measurement, several
labels carrying one series, metrics pinned at a bound, dates whose day and month
cannot be told apart, columns that are empty or constant, and values outside a
range you declare.

Two of its findings are FAIL because they are wrong whatever the analysis does
with them.

**A structured sentinel.** A temperature archive that stores absent as `0.0` at
one rate in one station and a much higher rate in another does not add noise, it
adds a spatially organised bias — and one of the same order as the signal being
looked for, which it can imitate. Pass `--group` whenever a grouping exists; the
overall rate is the number that hides this.

**A duplicated series.** Distinct labels carrying identical values are one
measurement wearing several names. Every spatial statistic computed across them
is then a statement about one instrument, and nothing in the file looks wrong.

`--expect` is the answer to a field whose name is not its semantics: a column
called `value` that holds gross floor area rather than height gives a median of
eighty for a city of flats, and only a declared plausible range catches it. Say
out loud what the number should look like, before you look.

## The provocations

The rest is not automatable, because it requires knowing what the analysis
claims. Each of these is a way to make a quiet failure loud.

**Run the negative control.** Give the pipeline an input that cannot contain the
effect and check that it reports no effect. This is the single highest-yield
test in the set, and it is the one most often skipped because it costs a run and
returns nothing. A control that comes back positive has just saved the paper.

**Permute the labels.** Shuffle the outcome against the predictors and confirm
the result collapses. If a shuffled run keeps most of the effect, the effect is
in the machinery, not the data.

**Check the detector detects.** Inject a known signal at a known strength and
confirm it is recovered. A detector that has never been shown to detect anything
cannot support a claim about absence.

**Report the denominator beside every stability metric, in the same table.** A
Jaccard of 1.000 and a regret of zero are as often the arithmetic of an empty
comparison as they are agreement: nothing varied, so nothing disagreed. Add a
saturation flag, and add it to the results table rather than to a check nobody
reads afterwards.

**Restrict the comparison to where the variable can act.** If the worst quintile
is filled entirely by units the variable cannot reach, the metric measures
reachability, not the variable. This is the commonest way to conclude that
something has no effect.

**Never let the data choose a cut, a threshold or a weight.** A split at the
median maximises reclassification by construction. Either anchor the choice
externally, or report the whole curve and say which point is primary and why.

**Prefer intra-source validation.** Cross-source matching invents its own error:
joining heights from one inventory to floor counts from another produced an
impossible negative bias, while the subset of one source carrying both fields
gave exactly the expected value. Validate inside a source before you validate
across two.

**Name variables so they cannot be read backwards.** A warm bias of +1.85 was
written up as a cold bias of −1.85 because the correction was read as the error.
Use `raw_error_a_minus_b` and `correction_b_minus_a`, and assert at run time that
each still means what its name says.

**Bound an incomplete layer from both sides.** If a layer is missing a component,
compute the result with the component absent and with it maximal. If the
conclusion survives both, the missing component is not load-bearing; if it does
not, you have found the result rather than lost it.

**Do not call the best available representation the truth.** Naming it *ground
truth* converts your own uncertainty into everyone else's error. Call it the
highest-information reference available and list what is wrong with it.

## After a re-run

This deserves its own step because it is invisible and it is guaranteed.

When a pipeline is re-run after a change, every published number has to be
recomputed from its source, not re-read in the text. A figure that survived a
re-run is plausible **because it was once correct**, so reading the manuscript
cannot find it. In the audited project, four magnitudes survived a full
re-execution at their old values, and two of them sat exactly on the bounds the
analysis itself flags as suspicious.

Write the check as a script: recompute each published magnitude from its source
file and search for it literally in the manuscript. Run it before every
compile, not before submission.

The same applies to prose. A pipeline that applies two window-specific
corrections while the methods section describes one uniform scalar produces
correct outputs and an irreproducible description. Export the constants the code
actually used and assert that each appears in the text.

## Reporting

Say which failures were looked for and which were found, including the ones that
came back clean, because a control that passed is evidence and an audit that
reports only hits cannot be distinguished from an audit that looked once.

For anything found, give the defect, the consequence had it gone unnoticed, and
the safeguard now in place. "The station filter was too aggressive" is not
usable; "the first rule discarded a station for two zeros in half a million
parts, leaving one municipal station of nine, so the panel was unusable and for
the wrong reason; discard now requires a systemic defect" is.

## Rules

A clean run of `datasmell.py` means those particular defects are absent. It is
not evidence that the analysis is sound, and it must never be reported as such.

Do not fix a defect and move on. Ask what else the same cause could have
touched: a wrong destination layer is not preprocessing, and one of them here
reversed the sign of a comparison between two entirely different inputs.

Never repair a suspicious result by widening a filter until it looks reasonable.
That is the same failure with a better disguise.
