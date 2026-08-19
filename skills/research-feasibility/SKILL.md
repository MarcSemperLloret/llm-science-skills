---
name: research-feasibility
description: >-
  Decide whether a research idea deserves a full project, using a small pilot
  rather than an argument. Use when an idea is proposed, when a dataset arrives
  looking promising, before committing weeks to an analysis, when a pilot has
  produced something unexpected, or when several possible directions have to be
  ranked. Runs a minimum viable experiment, registers every signal it finds
  including the ones nobody was looking for, tests each against the literature
  and against refutation, and returns GO, CONDITIONAL GO, REDIRECT, BRANCH or
  NO-GO with the evidence. Not a substitute for the full study.
---

# Research feasibility and signal discovery

The question is not whether the idea is interesting. It is whether a small,
cheap, honest experiment produces something that survives being attacked.

Two failures are equally common and this skill is built against both. Committing
months to an idea whose pilot never really tested it, and discarding a dataset
because the original hypothesis failed while something more interesting sat in
the same output, unregistered, because nobody was looking for it.

## What it returns

**GO** — a signal survives, it is not already published, and there is a credible
path to a full study.
**CONDITIONAL GO** — promising, with one decisive uncertainty named, and the
experiment that would settle it specified.
**REDIRECT** — the original hypothesis is weak or saturated, and another signal
found on the way is stronger.
**BRANCH** — the original idea and a discovered signal each justify a project.
**NO-GO** — nothing survives. Say so plainly, and do not soften it because the
work was effortful.

## The pipeline

```
idea
 └─ rapid literature check ─────────────→ literature-check, novelty mode
 └─ minimum viable experiment
 └─ original hypothesis, tested first
 └─ signal discovery beyond it
 └─ Signal Ledger
 └─ for EACH promising signal ──────────→ literature-check, novelty mode
 └─ adversarial validation ─────────────→ silent-failure-audit
 └─ independent replication
 └─ GO / CONDITIONAL GO / REDIRECT / BRANCH / NO-GO
```

Three of those stages belong to other skills and are not repeated here. Invoke
them; do not reimplement them.

| stage | skill | why it is not here |
|---|---|---|
| any literature question | `literature-check` | citation chaining, DOI verification and the venue landscape are one job, done properly in one place |
| attacking a surviving signal | `silent-failure-audit` | negative controls, permutation, saturation and denominators are the same protocol whatever produced the number |
| whether a reviewer would accept it | `peer-review-simulation` | only once a direction has been chosen |

## Define the question so it can fail

Write, before running anything:

* the question, in one sentence;
* the quantity that would answer it, and the direction that would count as a
  positive result;
* what result would make you drop the idea;
* the smallest dataset and analysis that could produce either.

If no result would make you drop the idea, the pilot is a demonstration rather
than a test, and its outcome is already decided.

## The rapid literature check

Run `literature-check` in novelty mode before designing anything: four databases,
chaining in both directions from the closest paper already known, and an explicit
answer to whether this has been done and where the closest work stops.

An idea that is already published is a NO-GO now rather than after the pilot,
and this is the cheapest stage at which to find out.

## The minimum viable experiment

Small, fast, complete end to end. It must be able to return a negative, it must
produce the quantity defined above, and it must be reproducible from a script
before anything is read off it.

**Computational feasibility.** Assess whether the experiment can run with the
resources actually available in the current environment — check them, do not
assume them. If it cannot, redesign the minimum viable experiment until it can,
rather than making the pilot conditional on hardware that would have to be
acquired first. A pilot that requires a purchase is not a pilot.

## What counts as a signal

Fix this before looking, in the units of the problem:

* the effect size that would matter scientifically, not statistically;
* the uncertainty that would still leave it useful;
* the stability required across the obvious variations of the analysis.

A signal that exists only at one arbitrary threshold, in one subgroup, or under
one choice of preprocessing is not a signal. A *p* value is not a signal.

## Test the original hypothesis first, and say what happened

Run the pre-registered question before anything exploratory and record the
result whatever it is. Reporting a discovered signal while quietly dropping the
question you set out to answer is the commonest way a feasibility study turns
into a sales document.

## Then look for what you were not looking for

This is the stage most pilots skip and it is where the value usually is. Examine
the same outputs for structure nobody predicted: an unexpected grouping, a
covariate behaving oddly, a subgroup moving against the rest, a relationship
between two quantities that were both meant to be controls.

Everything found here is exploratory and stays labelled exploratory until it has
been through the ledger.

## The Signal Ledger

Every candidate signal is registered, including the ones later rejected — a
ledger containing only survivors cannot be told apart from a ledger written
afterwards.

```text
S-001
  Signal:
  Origin:                    (pre-registered / exploratory)
  Observation:
  Magnitude:
  Uncertainty:
  Possible explanation:
  Alternative explanations:
  Potential importance:
  Literature status:
  Validation status:
  Current decision:
```

Statuses: `OBSERVED`, `LITERATURE CHECK REQUIRED`, `KNOWN`, `PROMISING`,
`TESTING`, `ARTEFACT`, `REPLICATED`, `FAILED REPLICATION`, `CANDIDATE PROJECT`,
`REJECTED`.

A signal cannot advance past `PROMISING` without a literature check of its own.
The check run on the original idea does not cover a signal that was not part of
the original idea.

## Classify the overlap, for every signal

Ask what the closest published work actually establishes, and name which of
these applies:

* **novel, or very limited prior evidence** — no convincing direct
  demonstration;
* **mentioned but not tested** — proposed or discussed, never quantified;
* **partially studied** — demonstrated under restricted conditions;
* **phenomenon known, consequence untested** — established, but an important
  implication has not been looked at;
* **phenomenon known, mechanism unresolved** — the result stands, the
  explanation does not;
* **broadly established** — substantial literature already supports it;
* **saturated** — the finding, its interpretation and its consequences are all
  covered.

The last two are NO-GO for that signal. The middle three are where most real
projects live, and each is a legitimate contribution when stated as what it is.

**Novelty is not created by a different dataset, location, method, model or
period.** Those are differences. Whether a difference produces knowledge that
did not exist has to be argued, not asserted.

## Attack what survives

Hand every surviving signal to `silent-failure-audit`. Its provocations —
negative control, label permutation, injected signal, denominators and
saturation flags, no cut chosen by its own result, recomputation from source —
are what separate a finding from an artefact, and they do not change with the
field.

Two more belong to a pilot specifically.

**Sensitivity.** Vary every arbitrary choice — preprocessing, inclusion window,
threshold, model family — and report the whole range rather than the best cell.
A signal that survives only its original settings is a setting.

**Independent replication.** A different period, region, cohort or instrument,
chosen before it is run. Replication on the data that produced the signal is not
replication.

## Convert what survives into a hypothesis

An exploratory finding becomes a project when it can be stated as a prediction
that could fail, with the experiment that would test it and the observation that
would refute it. Write that down and seal it before the full study starts. The
seal is the point: a prediction is only informative if it could have been wrong,
and one that is falsified is often worth more than one that is confirmed,
because it says the model was wrong somewhere specific.

## Deciding

Judge the original idea and each discovered signal **separately**. That is what
makes REDIRECT and BRANCH available instead of forcing everything into one
verdict.

**GO** requires all of: a signal meeting the threshold set beforehand; the main
alternative explanations challenged rather than mentioned; a novelty
classification that is neither `broadly established` nor `saturated`; a
replication that worked or is clearly within reach; and a full study that fits
the resources actually available.

**NO-GO** when no signal survives, when the result depends on an arbitrary
analytical choice, when alternative explanations dominate, when the data cannot
answer the question, when replication keeps failing, or when the contribution is
saturated.

A NO-GO reached in a week is the most valuable outcome this skill produces. It
is also the one that gets argued with, so state it first and give the evidence
after.

## Anti-bias rules

Never search until a positive appears; never choose the subgroup, period or
sample after seeing its effect; never redefine the primary hypothesis after
seeing the result; never present exploratory work as confirmatory; never omit a
failed robustness test or a failed replication; never treat significance as
sufficient; never claim novelty without a literature check; never stop searching
once supportive papers appear; and never inflate novelty because the dataset is
different.

The objective is signal discovery under discipline, not result optimisation.

## Keep the log as you go

Record findings in a running log — question, what was run, what came out, dead
ends included — while the work happens rather than at the end. A log written
afterwards records the story you now believe, and the discarded branch that
turns out to matter is exactly what it leaves out.

## The report

State the verdict first, then:

* the research question, and what would have falsified it;
* the initial literature landscape and the closest prior work;
* the minimum viable experiment, why it was adequate, and that it ran within
  available resources;
* the original hypothesis and its outcome, stated plainly;
* the Signal Ledger in full, rejected entries included;
* the literature classification for each surviving signal;
* the sensitivity range and the replication result;
* the candidate projects, ranked, with the reason for the ranking;
* the strongest unresolved threat to the conclusion;
* the next decisive experiment;
* the verdict again, with what would change it.

## Done

The verdict is stated before the detail. Every signal reached the ledger,
rejected ones included. Every surviving signal has a literature check of its
own, not the one run on the original idea. Nothing exploratory is described as
confirmatory. The strongest threat to the conclusion is named by you rather than
left for a reviewer. And NO-GO was available throughout: if it was not, this was
not a feasibility study.
