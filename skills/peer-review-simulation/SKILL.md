---
name: peer-review-simulation
description: Attack our own manuscript the way the reviewers will, before it is submitted, and fix what falls. Use when a draft is complete, before submission, after a major revision, or whenever the user asks how strong a paper is or what a reviewer would say. Runs the consistency checks a reviewer performs with a pencil, then writes real reviewer reports from several hostile perspectives, ranks the objections by how much damage each does, and says which are fatal, which are answerable and what to change now.
---

# Peer review simulation

This is for strengthening our own drafts. The purpose is to find the objection
that would cost the paper, while there is still time to remove it.

The failure mode of a simulated review is politeness. A report that lists small
improvements and concludes "minor revision" is worse than useless: it produces
the feeling of having been reviewed without the benefit. Write the review that
would sting.

Run it after `desk-reject-simulation`, which asks whether the paper survives ten
minutes. This one assumes it does, and asks what happens when somebody reads the
methods properly.

## The mechanical half

```bash
python reviewcheck.py manuscript.tex
```

It compares every quantity in the abstract against the body numerically, with
rounding — an abstract quoting one decimal is supported by a body carrying two —
and reports values that appear nowhere else. A headline number that cannot be
traced to the results is the cheapest possible way to lose a reader's trust, and
it is invisible to reading because both numbers look right where they sit.

It also flags proof language and causal verbs in the abstract of an
observational study, p-values with no mention of multiplicity, significance
claimed with no interval anywhere, and a paper with no limitations.

## Write the reports

Produce two or three reports, each from a reviewer with a different reason to be
unconvinced. Give each a real perspective rather than a label:

* **the methodologist**, who does not care about the domain and asks whether the
  design can support the claim at all;
* **the domain expert**, who knows the nearest published work and wants to know
  what is actually new;
* **the statistician**, who reads the numbers, the sample sizes and the
  multiplicity, and who is unimpressed by anything that rests on a handful of
  cases.

Each report: a paragraph of summary, then numbered major points, then minor
ones. Cite section and line. A major point is one that, unanswered, changes the
recommendation.

## What to attack

Go where our own designs are weakest.

**Observability versus absence.** Is "not detected" separated from "not
observable"? A negative result with no denominator is not a result.

**Pre-specification.** Which analyses were fixed before the data were seen, and
does the text make the boundary visible? Any result presented as confirmatory
that was in fact found by looking is the single most damaging thing a reviewer
can uncover. Check that exploratory findings are labelled as such in the
abstract too, not only in the methods.

**Power.** How many cases carry each headline claim? A prediction resting on
twelve blocks, or a subgroup on nineteen, is not evidence of absence when it
fails. If a null is reported, was the study able to detect the effect it failed
to find? Say so with a number.

**Multiplicity.** Count the comparisons actually made — groups, windows,
thresholds, radii, products — and ask what survives if they are counted
honestly.

**Analytic choices.** For every threshold, window or aggregation, what happens
under the other reasonable choice? A result that reverses when a daily mean
becomes a daily maximum is a finding about the choice, not about the world. Do
this before a reviewer does, and report it.

**Negative controls.** Is there a case where the method should find nothing, and
does it? If the control also fires, the positive means nothing.

**Causal language.** Every "because", "drives", "leads to" and "due to" against
an associational design is a point a reviewer will take.

**Generalisability.** One city, one network, one country, one season. What is
claimed beyond it, and on what basis?

**Reproducibility.** Does the number in the text match the number in the table
and in the deposited output? Can the analysis be re-run from what is deposited?

## Rank, then decide

List every objection with an estimate of the damage:

* **fatal** — the claim does not survive it; the paper needs a different claim,
  more data, or a different analysis;
* **answerable now** — an analysis or a sentence fixes it before submission;
* **answerable in review** — legitimate, but a response letter will settle it;
* **noise** — a reviewer might raise it and it costs nothing.

Then say what to do, in order, and what the paper looks like after.

Name the **strongest unresolved threat** explicitly, even when everything else
passes. A paper with no stated weakness has not been read hard enough.

## Rules

Do not soften. Do not pad the report with praise to balance the criticism; the
author is not the audience of a compliment here.

Do not invent a reference to support an objection. If the objection depends on
prior work, check it with `literature-check` or state that it is unverified.

Do not propose an analysis that the data cannot support just to answer a point.
"This cannot be answered with these data, and the paper should say so" is a
legitimate and often correct recommendation.

Separate what is wrong from what is merely unfashionable. A method is not weak
because it is simple.
