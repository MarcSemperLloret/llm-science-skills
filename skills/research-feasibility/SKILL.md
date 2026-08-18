---
name: research-feasibility
description: Evaluate whether a scientific research idea has sufficient empirical signal, robustness, novelty, and relevance to justify a full project. Test the original hypothesis efficiently, actively identify unexpected scientifically meaningful signals, verify every promising signal against the current literature, challenge alternative explanations, and recommend whether to pursue, redirect, branch, or stop the research project. Applicable across empirical, computational, data-intensive, and quantitative scientific fields.
---

# Research Feasibility & Signal Discovery

## Objective

Determine whether a research idea deserves further scientific investment.

The goal is **not** to prove the original hypothesis.

The goal is to identify the strongest scientifically defensible and potentially
valuable research direction supported by the available evidence.

A feasibility study may conclude that:

* the original hypothesis is promising;
* the original hypothesis should be rejected;
* the original hypothesis is already well covered by the literature;
* an unexpected signal deserves further investigation;
* an unexpected signal is stronger than the original idea;
* multiple independent research directions have emerged;
* no current signal justifies a full project.

All of these are valid outcomes.

---

# Core Research Principle

Follow the evidence rather than the original idea.

However, distinguish rigorously between:

* **pre-specified hypotheses**;
* **exploratory observations**;
* **derived hypotheses**;
* **independently validated findings**.

Never present a signal discovered during exploration as though it had been
predicted beforehand.

---

# Mandatory Workflow

Use this workflow unless the scientific context clearly requires a justified
variation:

```text
Research question & Scientific Story Initialization
        ↓
Rapid literature check (Backward & Forward Chaining)
        ↓
Minimum viable experiment & Hardware Feasibility Audit
        ↓
Test original hypothesis
        ↓
Inspect for additional meaningful signals
        ↓
Register candidate signals in Signal Ledger & Scientific Story
        ↓
Literature check for EVERY promising signal
        ↓
Challenge signal / alternative explanations
        ↓
Independent validation when feasible
        ↓
Deep novelty assessment
        ↓
Scientific relevance assessment
        ↓
GO / REDIRECT / BRANCH / NO-GO
```

Do not skip the literature checks.

---

# Scientific Story Log (`research_log.md`)

Maintain a continuous, high-level scientific narrative log (`research_log.md`) throughout the project.

This log is **not** a raw dump of every terminal output or minor code debug. It is a **curated scientific chronicle** capturing the evolution of the research.

Record only key milestones:
1. **Initial Hypotheses**: The original motivation and pre-specified questions.
2. **Key Experiments**: High-level design and purpose of pivotal pilots/tests.
3. **Discarded Hypotheses**: What failed or was refuted, along with the empirical reason why.
4. **Unexpected Signals & Pivots**: Key findings that led to new derived hypotheses or project branching.
5. **Decisions & Milestones**: Major GO / REDIRECT / BRANCH / NO-GO transitions.

This log ensures transparency, prevents context drift, and provides a clear historical narrative of how the evidence led to the final conclusion.

---

# 1. Define the Research Question

Translate the initial idea into a clear scientific question.

Identify:

* the phenomenon being investigated;
* the proposed explanation or mechanism, if any;
* the relevant variables;
* the unit of analysis;
* the expected comparison or relationship;
* the main outcome;
* the intended scientific contribution.

State the initial hypothesis as precisely as possible in `research_log.md`.

Where appropriate, define what observation would:

* support it;
* weaken it;
* falsify it.

Do not broaden the hypothesis after seeing the results merely to preserve the
project.

---

# 2. Perform a Rapid Literature Check

Before substantial computation or data collection, check whether the central
idea is already established.

The purpose of this first search is triage, not a full literature review.

Determine:

1. whether the phenomenon is already known;
2. whether essentially the same experiment has been performed;
3. whether the proposed contribution is already saturated;
4. which terminology the field uses;
5. which methodological problems are already recognized.

### Search Protocol: Forward & Backward Citation Chaining

Search using:

* direct terminology, synonyms, and related mechanisms;
* **Backward Chaining**: Inspect foundational studies and reviews cited by key papers to understand historical context.
* **Forward Chaining**: Search for recent papers (last 12–24 months) that cite those foundational studies to check if the space has been saturated recently.

Do not assess novelty using only model memory when literature-search tools are
available.

If the contribution is clearly saturated, do not automatically stop.
Determine whether a different unresolved question remains.

---

# 3. Design the Minimum Viable Experiment

Use the smallest scientifically credible experiment capable of determining
whether the idea has potential.

Avoid beginning with the largest possible analysis.

Prefer a pilot that is:

* representative;
* computationally manageable;
* sufficiently powered to reveal a meaningful effect;
* reproducible;
* easy to inspect;
* capable of exposing major methodological problems.

Select important analytical choices before inspecting the main result whenever
possible.

Record those choices in `research_log.md`.

The purpose of the pilot is to maximize **information gained**, not dataset
size.

---

# 4. Audit Data and Experimental Feasibility (Hardware & Data Checks)

Before interpreting results, determine whether the experiment can actually
answer the research question and run efficiently within hardware limits.

### Local Hardware Constraints Audit
Ensure that pilots, data preprocessing, and initial models are designed to execute within the available local compute setup:
* **CPU**: Intel Core i9
* **RAM**: 128 GB
* **Storage**: 2 TB SSD/Disk
* **GPU**: NVIDIA RTX 4070

If an experiment or dataset exceeds these local limits, re-scope the pilot to fit comfortably within these bounds or explicitly flag the requirement for external/cloud scaling before proceeding.

### Data Quality & Methodological Checks
Check relevant issues such as:

* data availability and licensing;
* data quality and missingness;
* measurement uncertainty;
* sampling bias;
* temporal and spatial coverage;
* class or regime imbalance;
* variable definitions and alignment;
* independence of observations;
* potential confounding or data leakage.

If a serious data or hardware limitation prevents the research question from being
answered, report it before interpreting downstream results.

---

# 5. Define What Counts as a Meaningful Signal (Generic Quantitative Rigor)

Do not equate statistical significance (`p < 0.05`) with scientific importance.

Every scientific domain requires specific, domain-appropriate quantitative metrics (e.g., effect sizes like Cohen's $d$, $R^2$, physical tolerances, Bayes Factors $BF_{10}$, signal-to-noise ratios, or domain benchmark margins).

Define meaningful signals using domain-appropriate quantitative criteria:

* **Effect Magnitude**: Is the effect large enough to matter in the domain?
* **Uncertainty & Precision**: Are confidence or credible intervals sufficiently narrow?
* **Signal-to-Noise Ratio**: Does the signal stand out clearly against measurement error or baseline noise?
* **Consistency & Reproducibility**: Does the pattern hold across subsets or conditions?
* **Explanatory/Predictive Consequences**: Does the signal change domain interpretation or outcomes?

Where scientifically possible, define the expected quantitative threshold before examining many alternative analyses.

Avoid defining success as merely:

* `p < 0.05`;
* any non-zero correlation;
* any minor model improvement;
* any arbitrary subgroup difference;
* any visually striking pattern without quantitative backing.

A useful signal should have a plausible scientific interpretation and quantitative backing.

---

# 6. Test the Original Hypothesis First

Run the main pre-specified analysis before extensive exploratory analysis.

Report enough information to judge the effect, including where applicable:

* effect magnitude;
* uncertainty;
* sample structure;
* relevant baseline;
* variability;
* sensitivity to obvious methodological choices.

Report null and contradictory results honestly and log them in `research_log.md`.

Do not modify the hypothesis retrospectively to match the result.

Classify the original hypothesis provisionally as:

```text
SUPPORTED
WEAK
NOT SUPPORTED
INCONCLUSIVE
```

This classification does not determine whether the entire feasibility study
has succeeded.

---

# 7. Actively Search for Additional Scientific Signals

After evaluating the initial hypothesis, inspect the results for unexpected
patterns that may represent stronger research opportunities.

This stage is explicitly exploratory.

Potential signals may include:

* unexpected associations;
* subgroup or regime effects;
* nonlinear relationships;
* threshold behavior;
* systematic residual patterns;
* failure modes;
* contradictions between measurement systems;
* temporal or spatial structure;
* scale dependence;
* model or method instability;
* unexpected interactions;
* extreme-case behavior;
* previously hidden heterogeneity.

Do not enumerate every possible statistical combination.

Prioritize signals with some combination of:

1. meaningful magnitude;
2. internal consistency;
3. plausible mechanism;
4. potential scientific consequence;
5. potential generalizability;
6. unexpectedness relative to current knowledge.

A smaller but interpretable effect can be more valuable than a large arbitrary
correlation.

---

# 8. Maintain a Signal Ledger

Every potentially important signal must be registered.

Use sequential identifiers:

```text
S-001
S-002
S-003
...
```

For each signal record:

```text
Signal:
Origin:
Observation:
Magnitude:
Uncertainty:
Possible explanation:
Alternative explanations:
Potential scientific importance:
Literature status:
Validation status:
Current decision:
```

Use statuses such as:

```text
OBSERVED
LITERATURE CHECK REQUIRED
KNOWN
PROMISING
TESTING
ARTEFACT
REPLICATED
FAILED REPLICATION
CANDIDATE PROJECT
REJECTED
```

The Signal Ledger prevents potentially important observations from being lost
and keeps exploratory findings distinguishable from validated results.

---

# 9. Search the Literature for Every Promising Signal

This is mandatory.

Whenever a potentially meaningful signal is identified, investigate whether it
is already known **before investing heavily in developing it**.

Do this for:

* the original signal;
* unexpected findings;
* apparent mechanisms;
* methodological effects;
* anomalies;
* secondary patterns that could become new projects.

Ask:

> Has this phenomenon already been demonstrated?

> Has the proposed explanation already been established?

> Has its scientific consequence already been quantified?

> Has essentially the same analysis already been performed?

### Deep Literature Search Protocol
Use both **Backward Chaining** (examining foundational citations of relevant papers) and **Forward Chaining** (searching recent literature that cites those works) across:
* alternative terminology and synonyms;
* related mechanisms;
* methodological descriptions;
* neighboring disciplines;
* broader and narrower versions of the phenomenon.

The literature search must be **adversarial**.

Actively seek the strongest prior work that could invalidate the novelty claim.

Do not stop after finding papers that support the interpretation.

---

# 10. Classify Literature Overlap

For each candidate signal, classify the closest prior literature.

### NOVEL OR VERY LIMITED PRIOR EVIDENCE

No convincing direct demonstration is found.

### MENTIONED BUT NOT TESTED

The phenomenon has been proposed or discussed but not adequately quantified.

### PARTIALLY STUDIED

The signal has been demonstrated under restricted conditions.

### PHENOMENON KNOWN, CONSEQUENCE UNKNOWN

The phenomenon is established but an important implication has not been tested.

### PHENOMENON KNOWN, MECHANISM UNCLEAR

The result is established but its explanation remains unresolved.

### BROADLY ESTABLISHED

The core result is already supported by substantial literature.

### SATURATED

The proposed finding, interpretation, and main consequences are already well
covered.

Do not claim novelty merely because the current project uses:

* another dataset;
* another location;
* another method;
* another model;
* another time period.

Determine whether those differences create new scientific knowledge.

---

# 11. Look for Genuine Novelty

A known phenomenon may still support important new research.

Evaluate whether the contribution instead lies in:

* a new phenomenon;
* a new mechanism;
* an unexplored consequence;
* stronger empirical evidence;
* broader generalization;
* previously unknown boundary conditions;
* a change of scale;
* a new methodological implication;
* a contradiction with accepted knowledge;
* a stronger benchmark;
* a new connection between known phenomena.

Novelty should refer to the **scientific contribution**, not superficial
differences in implementation.

---

# 12. Try to Refute Every Promising Signal

Once a candidate survives its initial literature check, switch from discovery
to adversarial validation.

Ask:

> What is the strongest plausible explanation other than the proposed one?

Test relevant alternatives.

Depending on the domain, these may include:

* sampling artefacts;
* measurement error;
* confounding;
* dependence between observations;
* preprocessing choices;
* multiple comparisons;
* data leakage;
* selection bias;
* dataset shift;
* temporal effects;
* spatial effects;
* resolution mismatch;
* model specification;
* outliers;
* batch effects;
* inappropriate baselines;
* arbitrary thresholds.

Do not apply a fixed checklist blindly.

Identify the threats most capable of explaining the observed effect.

A convincing signal should survive the strongest reasonable alternatives.

---

# 13. Perform Sensitivity and Robustness Tests

Test whether conclusions depend excessively on arbitrary analytical choices.

Possible tests include reasonable alternatives for:

* sample definition;
* preprocessing;
* metrics;
* thresholds;
* temporal windows;
* spatial subsets;
* model specifications;
* reference datasets;
* aggregation;
* exclusion criteria.

Use a **small set of scientifically defensible alternatives**.

Do not search a large specification space until a desirable result appears.

Report failed robustness tests in `research_log.md`.

---

# 14. Use Negative Controls When Appropriate

Whenever feasible, design a test under which the proposed signal should:

* disappear;
* weaken;
* reverse;
* or behave predictably.

Examples may include:

* shuffled correspondence;
* irrelevant variables;
* control groups;
* negative outcomes;
* inappropriate temporal periods;
* regions or regimes where the proposed mechanism should not operate.

If an appropriate null or control reproduces the signal, reconsider the
interpretation.

---

# 15. Convert Exploratory Findings into Hypotheses

A promising exploratory signal should be converted into a testable derived
hypothesis.

Before examining independent validation data, specify in `research_log.md`:

```text
Observation:
Proposed explanation:
Prediction:
Falsification condition:
Validation data:
```

Example logic:

> We observed X.

> If mechanism M explains X, then Y should occur under independent condition Z.

This converts data exploration into a falsifiable scientific hypothesis.

---

# 16. Seek Independent Validation

Whenever realistically possible, do not confirm an exploratory signal solely
using the data that revealed it.

Prefer validation using an independent:

* sample;
* experiment;
* dataset;
* time period;
* location;
* population;
* instrument;
* model;
* cohort;
* laboratory;
* environmental regime.

The relevant notion of independence depends on the scientific domain.

Report unsuccessful validation attempts.

A failed replication may reveal boundary conditions and should not
automatically be hidden or discarded.

---

# 17. Perform a Deep Novelty Audit

Once a signal survives robustness testing and initial validation, perform a
deeper literature assessment.

Identify:

* closest direct precedent;
* closest methodological precedent;
* relevant competing explanations;
* contradictory evidence;
* recent advances;
* unresolved questions.

For the most relevant papers record:

```text
Study:
Research question:
Data or experiment:
Methods:
Main result:
Overlap with current finding:
Important differences:
What remains unresolved:
```

Then explicitly identify where the current contribution differs.

Do not use vague novelty statements when a precise comparison is possible.

---

# 18. Assess Scientific Relevance

Novelty alone is insufficient.

Ask:

* Does this change scientific understanding?
* Does it resolve an unresolved problem?
* Does it expose an important methodological limitation?
* Does it affect interpretation of existing evidence?
* Does it alter meaningful predictions or decisions?
* Does it generalize?
* Does it reveal a useful mechanism?
* Would researchers in the field care if the result were correct?

Classify relevance as:

```text
LOW
MODERATE
HIGH
VERY HIGH
```

Explain the classification.

Do not inflate relevance because a result happens to be novel.

---

# 19. Allow Project Branching

Do not force every useful signal into the original project.

A feasibility analysis may produce several possible projects.

Create a new project branch when a signal:

* answers a substantially different question;
* implies a different mechanism;
* requires substantially different validation;
* has greater scientific importance than the original idea;
* would produce a clearer independent scientific story.

For example:

```text
P-001 — Original hypothesis
Status: NO-GO

P-002 — Derived from S-003
Status: CANDIDATE PROJECT

P-003 — Derived from S-007
Status: VALIDATION REQUIRED
```

Do not combine unrelated findings merely to increase the apparent amount of
results in one manuscript.

---

# 20. Prioritize Research Directions

When multiple signals survive, rank them primarily by:

1. scientific importance;
2. robustness;
3. novelty;
4. replicability;
5. generalizability;
6. methodological defensibility;
7. feasibility of further testing;
8. coherence as a scientific contribution.

Do not rank opportunities primarily by:

* largest effect;
* smallest p-value;
* easiest publication;
* most convenient dataset.

Use:

```text
PRIORITY A — pursue
PRIORITY B — validate first
PRIORITY C — retain as secondary finding
DROP — insufficient evidence, novelty, or importance
```

---

# 21. Think Like a Skeptical Reviewer

Before recommending substantial further work, identify the strongest potential
criticism of each Priority A or B project.

Ask:

> What could make this finding disappear?

> What could make the interpretation wrong?

> What prior study could make the novelty incremental?

> What experiment would a strong reviewer immediately request?

Design the next experiment around the strongest unresolved threat.

Do not scale the study merely by adding more data.

Prefer experiments that discriminate between competing explanations.

---

# 22. Decision Rules

Evaluate the original project and newly discovered directions separately.

## GO

Recommend GO when:

* a meaningful signal exists;
* major alternative explanations have been challenged;
* novelty remains substantive;
* scientific relevance is sufficient;
* validation is successful or strongly feasible;
* experiment fits comfortably within local hardware limits (i9, 128GB RAM, 2TB storage, RTX 4070);
* there is a credible path to a full study.

## CONDITIONAL GO

Use when the signal is promising but a decisive uncertainty remains.

Specify exactly what experiment or evidence is required next.

## REDIRECT

Use when the original hypothesis is weak or saturated but another signal
provides a stronger scientific direction.

## BRANCH

Use when both the original project and a newly discovered signal justify
separate research projects.

## NO-GO

Use when:

* no meaningful signal survives;
* results depend on arbitrary analytical choices;
* alternative explanations dominate;
* data cannot answer the question;
* hardware limits prevent practical execution;
* replication consistently fails;
* the scientific contribution is already saturated;
* or remaining novelty is too weak.

Do not soften a NO-GO because considerable effort has already been invested.

---

# Anti-Bias Rules

Never:

* search indefinitely until a positive result appears;
* select only successful subgroups;
* select periods or samples after inspecting their effect;
* redefine the primary hypothesis after seeing the result;
* report exploratory findings as confirmatory;
* hide failed robustness tests;
* hide failed replications;
* treat statistical significance as sufficient evidence;
* declare novelty without literature verification;
* stop literature searching after finding supportive papers;
* exaggerate novelty because a different dataset was used.

The objective is **signal discovery under scientific discipline**, not
result optimization.

---

# Tool Use

When appropriate tools are available:

* search current scientific literature using both backward and forward citation chaining rather than relying only on internal knowledge;
* prefer primary scientific sources for specific claims;
* use reviews to map a field, not as the sole evidence for novelty;
* inspect original papers when determining overlap;
* use computational tools configured to run within local hardware bounds (i9, 128GB RAM, 2TB SSD, RTX 4070);
* preserve intermediate results and maintain `research_log.md`.

If current literature cannot be searched, clearly mark novelty as
**UNVERIFIED**.

Do not issue a strong GO recommendation based on novelty until that check has
been performed.

---

# Required Signal Ledger Output

Maintain a table or equivalent structured record:

| ID    | Signal | Origin              | Strength | Literature status | Validation | Decision |
| ----- | ------ | ------------------- | -------- | ----------------- | ---------- | -------- |
| S-001 | ...    | Primary/Exploratory | ...      | ...               | ...        | ...      |

Update the ledger as evidence changes.

A signal should never silently change from exploratory to confirmed.

---

# Required Final Feasibility Report

At the end of the feasibility phase report:

## Research question

State the original question precisely.

## Initial literature landscape

Summarize what was already known.

## Minimum viable experiment & Hardware audit

Describe the pilot, why it was adequate, and confirm execution within local hardware constraints (i9, 128GB RAM, 2TB storage, RTX 4070).

## Scientific Story summary

Brief overview of the main milestones logged in `research_log.md`.

## Original hypothesis

Report the evidence and current status.

## Signal Ledger

Include all scientifically meaningful signals discovered.

## Literature assessment

For every surviving signal state:

* closest prior work;
* degree of overlap;
* remaining novelty.

## Robustness

State which important alternative explanations were tested.

## Validation

State which findings were independently reproduced and which remain
exploratory.

## Candidate research projects

Separate distinct scientific directions.

## Priority

Assign each:

```text
A — pursue
B — validate first
C — secondary
DROP
```

## Strongest unresolved threat

Identify the single most important weakness for each serious candidate.

## Next decisive experiment

Recommend the smallest experiment most likely to change the decision.

## Final decision

Use:

```text
Original project:
GO / CONDITIONAL GO / REDIRECT / BRANCH / NO-GO

Best candidate signal:
...

Best research direction:
...

Reason:
...
```

---

# Final Research Standard

The goal of feasibility analysis is not to generate a publishable-looking
result.

It is to reduce uncertainty about **which scientific question is worth
pursuing**.

Always prefer:

**robust evidence over attractive evidence;**

**scientific relevance over statistical significance;**

**generic, domain-appropriate quantitative rigor over superficial p-values;**

**independent validation over retrospective explanation;**

and

**the strongest defensible research direction over loyalty to the original
idea.**
