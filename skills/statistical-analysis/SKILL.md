---
name: statistical-analysis
description: >-
  Decide whether an inference is valid before it becomes a claim. Use when
  choosing how to analyse data, when a model or test is being selected, when a
  result is about to be written up, when uncertainty has to be reported, and
  whenever a number will be used to support a conclusion. Covers the unit of
  analysis, dependence, the estimand, effect sizes, multiplicity, power,
  uncertainty and sensitivity, with a checker for the reporting defects a
  script can settle. Not a pipeline audit and not a substitute for a
  statistician on a genuinely novel design.
---

# Statistical analysis

Between finding a signal and writing it up sits the question that decides
whether the number means anything: **is the inference valid?**

That is not the same as whether the code is right. A pipeline can compute
exactly what it was asked to compute, on the wrong unit, against an estimand
nobody chose, and report an interval that answers a question no one asked.

| that job | belongs to |
|---|---|
| did the pipeline compute what we think | `silent-failure-audit` |
| how the conclusion is stated | `scientific-thinking` |
| does the idea deserve a project | `research-feasibility` |
| would a reviewer accept it | `peer-review-simulation` |

## Start with the unit, not the test

The commonest fatal error in applied statistics is not choosing the wrong test.
It is analysing at a finer unit than the one that actually varies.

Ask: **what is the independent replicate?** Not what each row is — what could
have come out differently, independently, on a repeat of the study. Rows within
a station, a patient, a country, a plate, a site or a year are usually not
independent of each other, and treating them as though they were inflates the
sample size, shrinks the interval, and produces significance from nothing.

The symptom is a denominator far larger than the number of things that were
really sampled: 3,946 rows from 58 countries is 58, not 3,946, for anything that
varies at country level.

The fixes, in order of preference: aggregate to the unit that varies; model the
dependence explicitly; or resample at the level of the unit, which is what a
country-level bootstrap does and why it gives wider intervals than a naive one.

Validation follows the same rule. If the unit is the country, the held-out set
is a set of countries, and a split that puts two rows from the same country on
both sides has leaked.

## Name the estimand before choosing a method

Write down, in words, the quantity you are trying to estimate, on what
population, under what conditions. Most disagreements about a method dissolve
once this is written, because they turn out to be disagreements about the
question.

The distinction that matters most in practice: **an association, a change, and a
prediction are three different estimands.** That a quantity ranks units
correctly says nothing about whether it tracks change within a unit, and neither
says anything about whether it predicts the next period. Each needs its own
validation, and a paper that establishes the first while claiming the third is
the ordinary way this goes wrong.

Watch also for the estimand shifting with the weighting. A mean over rows and a
mean over units are different quantities, and if the answer changes between them
say which one the claim is about, rather than reporting whichever is cleaner.

## Report an effect size, and its uncertainty, always

A *p* value is a statement about the data given a null hypothesis. It is not a
measure of size, importance, or probability that the hypothesis is true, and a
result reported as significant with no estimate beside it cannot be judged at
all.

Report the estimate in the units of the problem, with an interval. Then say what
the interval means for the decision: which effect sizes remain compatible with
the data, and whether the smallest one that would matter is among them.

**Never report post-hoc power.** It is a deterministic function of the *p* value
and adds nothing. The interval already says what the study could and could not
resolve.

## Multiplicity is about how many were run, not how many were reported

Correcting only the tests that made it into the paper is not correcting. Count
every test performed, including the ones abandoned, and decide in advance which
are confirmatory.

The useful structure is a small set of pre-specified primary comparisons,
corrected or not by an explicit rule, and everything else declared exploratory
and reported as such. That structure survives review; a family of twenty tests
with three highlighted does not.

Where the tests are many and related, a false discovery rate is usually more
useful than a family-wise correction, and either is better than silence.

## Sensitivity is part of the result, not an appendix

Every analysis contains choices that could have gone another way: inclusion
window, transformation, threshold, model family, how missing data were handled.
Vary each and report the range. A conclusion that holds across those choices is
a finding; a conclusion that holds only under the original settings is a
setting.

Two specific traps.

**A transformation can change the sign.** Whether abundances enter raw or as
`log1p` is not cosmetic, and if the direction of the result depends on it, that
dependence is the headline rather than a footnote.

**A cut chosen after looking maximises the effect by construction.** A split at
the median maximises reclassification. Either anchor the cut externally or
report the whole curve and say which point is primary and why.

## The mechanical half

```bash
python statcheck.py manuscript.tex
python statcheck.py manuscript.tex --max-tests 5
```

It settles the part that needs no knowledge of the design: a percentage no whole
number out of its stated denominator could produce, a *p* value printed as zero
or outside `[0, 1]`, a claim of significance with no interval or effect size in
the same sentence, many tests with no mention of multiplicity anywhere, a
"trend towards significance", and post-hoc power.

The percentage check earns its place because it catches something invisible: a
figure that survived a re-run while its denominator changed underneath it. A
stale number is plausible by construction, because it was once correct.

The checker is deliberately quiet. An earlier version matched a percentage
against the hour in "64.4% fall in 12:00–20:00" and against the integer part of
"an odds ratio of 2.74", and reported both as arithmetically impossible. A FAIL
that is wrong costs more than the finding is worth, because the next real one is
believed less.

## Before writing the number up

* Is the unit of analysis the unit that varies, and does the validation split
  respect it?
* Is the estimand written down, and is it the one the claim is about?
* Is there an effect size with an interval beside every claim?
* How many tests were run, and which were pre-specified?
* Does the conclusion survive the obvious alternative analytical choices?
* Does the interval exclude the smallest effect that would matter, or merely
  exclude zero?
* If the result is null, could the study have detected the effect if it were
  there? Say so with the interval, not with power.

## Rules

Do not choose the method after seeing which one gives the desired answer. If
several are defensible, report several.

Do not describe a non-rejection as a trend, a tendency, or approaching
significance. Report the estimate and the interval, and say what the data could
not resolve.

Do not report more decimal places than the measurement supports, and do not
report a percentage to one decimal from a denominator of twelve.

Where the design is genuinely unusual — nested, adaptive, censored, sequential,
strongly confounded — say that the analysis needs a specialist rather than
improvising a method and reporting it confidently.

## Done

The unit of analysis is stated and matches what varies. The estimand is written
in words. Every claim carries an estimate and an interval. Multiplicity is
declared in terms of what was run. Sensitivity to the arbitrary choices is
reported as a range. Nulls are reported as what the data could not resolve
rather than as absence. And `statcheck.py` reports no FAIL.
