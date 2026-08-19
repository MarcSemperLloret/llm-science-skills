---
name: scientific-writing
description: >-
  Write a manuscript as continuous scientific prose, and produce it in LaTeX
  cleanly. Use when drafting or revising any section of a paper, when a section
  reads like documentation rather than an argument, when tables overflow, when
  results are hard to follow, and before a manuscript is considered finished.
  Covers section and paragraph architecture, numerical density, redundancy,
  calibrated claims, and the LaTeX that encodes structure rather than
  decorating it. Not for slides, README files or outreach writing.
---

# Scientific writing

The problem is recognisable. A section arrives looking like this:

```latex
\subsection{Robustness Analysis}

\textbf{Station-level results.}
The results indicate...

\textbf{Regional analysis.}
Furthermore...

\textbf{Temporal results.}
Additionally...
```

That is technical documentation, not a paper. Every paragraph has been given a
label because the section has no argument running through it, and the labels
make the absence look like organisation.

**Prose carries the argument. Formatting must not substitute for narrative
structure.** If consecutive paragraphs need labels to explain their purpose,
the section is organised wrongly, and adding the labels hides that rather than
fixing it.

Two neighbouring skills own the parts this one does not. `scientific-thinking`
owns how a claim is formed and how observation, inference and speculation are
separated. `scientific-figures` owns figures and captions. This skill is about
the prose and its production.

## Continuous prose by default

The normal shape is a subsection followed by paragraphs, connected by their
sense. Bold or italic lead-ins are not transitions and do not become transitions
by being repeated.

A small number of structural labels is legitimate — a list of named cases, a
glossary-like passage, a set of parallel definitions. The test is whether
removing every one of them would leave the argument still followable. If it
would, they were structure. If it would not, they were doing the structure's job.

## Emphasis is meaning, not stress

Bold belongs to headings the document class defines, and to the rare label that
is genuinely structural. Italics belong to notation, taxa, variables, and a term
at the moment it is defined.

Neither belongs to stress. Italicising *not*, *and*, *different* or *where* marks
the word you would lean on when speaking; written prose does that with word
order, and a page carrying many of them reads as insistent rather than precise.

The audit: strip every manually added bold and italic. If the text is still
perfectly comprehensible, they were decoration.

## A subsection answers one question

Before writing, name the question each subsection answers:

```
3.1  Overall performance      What is the main result?
3.2  Dependence on X          Under what conditions does it change?
3.3  Robustness               Does it survive plausible alternatives?
```

Then check the sequence: **does subsection N create the need for subsection
N+1?** If it does not, the order is arbitrary and the reader is being asked to
hold things in suspense for no reason.

A sequence that usually works is: main finding, then characterisation, then
explanation, then robustness, then implication.

**The manuscript follows the scientific argument, not the chronology of the
analysis.** Ordering the results by the order the scripts were run is the
commonest cause of a section that has no shape, and it is invisible to the
author, who lived through that order.

## Each paragraph has one job

Decide what each paragraph is for — context, question, method, result,
interpretation, limitation, implication, transition — and give it one. The
labels never appear in the text; they are for deciding what belongs.

The failure this prevents is the paragraph that opens on one subject, delivers
seven numbers, and closes on a limitation belonging somewhere else.

Then check the joins. For each pair, ask **why does this paragraph follow that
one?** The answer must be a relation — cause, contrast, extension, consequence,
qualification, a new question. If the answer is "both are about the paper", the
transition is missing.

## Numerical density

Distinguish two kinds of number: the ones the argument needs, and the ones
reproducibility needs. The first go in prose. The second go in a table, a figure
or the supplement.

Do not narrate a table. A paragraph should communicate a pattern, not a sequence
of measurements. Instead of

> A was 0.81, B 0.79, C 0.76 and D 0.74, corresponding to improvements of 2.5%,
> 6.6% and 9.5% respectively, while RMSE changed from...

write

> A performed best, though its advantage over B was small; the separation was
> larger against C and D (Table 2).

and then give only the figures the sentence actually rests on. By the third such
sentence in the first version, the reader has stopped holding the numbers.

## Calibrate the claim to the evidence

Match the verb to what the evidence supports:

| evidence | verbs |
|---|---|
| direct, measured here | shows, demonstrates, is associated with |
| strong but inferential | supports, indicates, is consistent with |
| plausible interpretation | suggests, may reflect |
| speculation | could be explained by, one possibility is |

**Hedging must match epistemic uncertainty, not anxiety about reviewers.** Being
told to avoid over-claiming pushes writing into the opposite failure, which
reviewers also object to, and which costs the paper its own results.

If the analysis showed that a ranking changed when the reference dataset was
replaced, write:

> The ranking changed when the reference dataset was replaced.

Not "the results may suggest that the ranking could potentially be sensitive
to" — that weakens a fact the study establishes directly. But equally not "the
reference dataset biases model rankings", which asserts a mechanism the
comparison did not test. The line between those two is the subject of
`scientific-thinking`; the job here is to write the sentence that sits on it.

## Redundancy

The characteristic pattern is one claim restated in four places: the
introduction says X matters, the methods open by recalling that X matters, the
results close by highlighting it, and the discussion opens with it again.

Audit for: the same statement in consecutive paragraphs; the same
interpretation in results and discussion; results repeated in the discussion
with all their numbers again; the objective stated at the end of the
introduction and again at the start of the methods; the conclusion given three
times in slightly different words.

**Each paragraph must advance the argument. If removing it loses no information
and no reasoning, remove it or merge it.**

## Narrative compression

After a section is written, try to cut 10–20% without losing a single
scientific statement. This is a test rather than a length rule: if a quarter of
the text can go without losing content, that quarter was redundancy. The
introduction and the discussion improve most.

## The Discussion is not a second Results

It has its own architecture: the principal finding, its interpretation, its
relationship to previous work, the mechanism or explanation, the consequences,
the limitations, and the broader implication.

Do not restate results with their numbers; refer to them. Do not open every
paragraph with "Our results show".

## Lists

Prefer prose for scientific argument. Use a list when the items are genuinely
enumerable and parallel — a set of criteria, a sequence of steps, named cases.
Three consecutive lists of contributions, findings and limitations make a paper
read like a README.

## Tables

Check the width at final size, in the class the journal uses, before deciding
anything else.

When a table is too wide, work in this order:

1. remove information that is not needed;
2. reduce decimal places to what the measurement supports;
3. shorten the headers;
4. split the table;
5. redesign the columns, or move detail to the supplement;
6. consider landscape;
7. only then, a minor reduction in type size.

**Never solve an oversized table primarily by shrinking the font.** `\tiny` is
not a layout decision, `\resizebox` scales the type to whatever fits and makes
it unpredictable across the paper, and both are the first things a copy editor
reverses — at which point the table overflows in production instead.

## LaTeX

**Use LaTeX to encode document structure, not to decorate the manuscript.**

Respect the journal's class and change its formatting only when scientifically
or technically necessary. Do not add `titlesec`, `xcolor`, `soul`, `enumitem`
and their relatives without a reason that survives being stated out loud; a
submission that has fought its own template is visible immediately.

Do not reach for `\resizebox` as a general solution to anything that does not
fit, and do not compensate for an unreadable figure with a caption that explains
what it should have shown.

## The mechanical half

```bash
python prosecheck.py manuscript.tex
python prosecheck.py manuscript.tex --max-columns 6
```

It measures the habits: paragraphs opening with a label, emphasis rate and
emphasis on function words, the densest paragraph in the paper, tables by
column count, type shrunk inside a float, `\resizebox`, statements repeated in
substantially the same words, hedging per thousand words, and paragraphs that
all begin alike.

It reads the prose only — front matter, floats and end matter are excluded,
because a tabular counted as a paragraph reports its own cells as numeric
density.

Its thresholds are conventions rather than findings, and it reports the worst
instance so that it can be judged rather than obeyed. `\small` and
`\footnotesize` are ordinary table sizes and are not flagged; `\tiny` and
`\scriptsize` are.

## The final audit

**Prose.** Every paragraph has a clear job. The joins are relations, not
adjacency. No mini-headings standing in for structure. Bold and italics are
minimal and meaningful. No paragraph recites a table. Results and discussion do
different jobs. Claims are calibrated in both directions — nothing over-claimed,
nothing defensively weakened below what the data show. Redundant statements are
gone.

**Structure.** The subsection order follows the argument rather than the
analysis. Every subsection earns its existence. The manuscript is organised
around questions and findings, not around scripts.

**LaTeX.** It compiles without warnings that affect the output. Tables fit at
final size without shrunken type. Figures are legible. No unnecessary packages.
The journal's formatting is intact. Every reference, label and citation
resolves.
