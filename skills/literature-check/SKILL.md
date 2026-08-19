---
name: literature-check
description: >-
  Check what a manuscript claims against what the literature actually says,
  and verify that every reference exists and says it. Use before claiming
  novelty, when assessing whether an idea is already published, when a
  bibliography is being assembled or cleaned, before submitting, and whenever
  research-feasibility needs its literature check. Verifies DOIs against the
  registry, finds references cited but missing and entries never cited, and
  locates every novelty claim so it can be defended. Do not use to write a
  related-work section from memory.
---

# Literature check

Two different jobs share this skill because they fail the same way.

**Before a project**, the question is whether the idea is already published, and
the honest answer decides whether to continue. `research-feasibility` will not
issue a GO without this and marks novelty UNVERIFIED when it has not been done.

**Before a submission**, the question is whether every reference exists, says
what it is cited for, and is actually cited. A fabricated or mismatched
reference is the one error a reader can verify in seconds, an author never
re-checks, and a journal treats as a serious matter.

## The four modes

This skill answers four different questions, and the caller usually needs one of
them rather than all four. Say which mode you are in; it decides what is run and
what a good answer looks like.

**Mode A — novelty.** Has this been done, and where does the closest work stop?
Called by `research-feasibility` before a pilot is designed, and again for every
signal the pilot turns up. Output: the closest published work, named, and the
classification of the overlap. Search with `--rank recent` and chain in both
directions. Nothing about a `.bib` file belongs here.

**Mode B — claim and citation audit.** Does each citation support the sentence
it is attached to, and does every novelty claim in the manuscript name what it
is new against? Called before submission. Output: the claims that are unplaced
and the citations that do not carry what they are cited for.

**Mode C — bibliography hygiene.** Does every DOI resolve to the work the entry
describes, is anything cited without an entry or entered without a citation, and
how large and how current is the bibliography? This is `litcheck.py` and it is
almost entirely mechanical.

**Mode D — venue landscape.** What has the target journal published on this
subject, and does the manuscript engage with it? Called by
`desk-reject-simulation` for the fit half of the screen. This is `--venue`.

Modes B and C run together before a submission. A and D do not: A is about the
field and D is about one journal, and mixing them produces a bibliography that
looks like an attempt to flatter an editor.

## Never assert a reference from memory

A citation is a factual claim about a document. Producing one without checking it
resolves is the single most damaging thing that can be done here, and it has
become common wherever drafting is assisted.

If a search tool is available, search. If it is not, say plainly that the
literature could not be checked and mark novelty **UNVERIFIED**. Do not fill the
gap with plausible-looking references, do not reconstruct a DOI, and do not
attach a citation to a claim without having seen that the work supports it.

## Searching

```bash
python litsearch.py "convective outflow detection citizen weather station"
python litsearch.py "urban heat accessibility" --rows 20 --mailto you@example.org
python litsearch.py --doi 10.5194/wcd-5-779-2024      # what that DOI actually is
python litsearch.py --cites 10.5194/wcd-5-779-2024    # forward: who cites it
python litsearch.py --refs  10.5194/wcd-5-779-2024    # backward: what it cites
python litsearch.py "sensor placement" --venue "Internet of Things"
python litsearch.py --bibtex 10.5194/wcd-5-779-2024   # the entry, ready to paste
```

It queries Crossref, OpenAlex, Europe PMC and arXiv together, merges duplicates
and prints the source that returned each row. No credentials; `--mailto` enters
the polite pools and is served faster.

**Ranking is a choice and it matters.** The default puts the most cited first,
which is right for mapping a field. It is wrong for a novelty question, and
wrong in the direction that flatters: the paper that destroys a novelty claim is
usually recent and lightly cited, because it has not had time to accumulate
citations — which is exactly why nobody has told you about it. Pass
`--rank recent` in mode A. Citation counts stay on every row as evidence of
centrality; they stop deciding the order.

Four sources rather than one because each has a blind spot: Crossref and
OpenAlex index what has a DOI, Europe PMC reaches the biomedical literature and
its preprints, arXiv holds the computing, physics and statistics that often
never acquire a DOI. A novelty claim checked against one database is not checked.

`--cites` and `--refs` are the two directions of chaining below, done for you.
Start from the closest paper you already know, not from a keyword: keyword search
returns the popular, chaining returns the relevant.

If a source does not answer, the run says so and continues; a silent database is
not the same as an empty field, and the report should say which ones answered.
The indexes rate-limit after a handful of queries in quick succession, and a
refusal is printed as a refusal rather than as an absence of results.

## Searching one journal

```bash
python litsearch.py "sensor placement deployment" --venue "Internet of Things"
```

`--venue` resolves the journal in the index and asks for its works, rather than
filtering a general search afterwards. That distinction is the whole feature: a
keyword search returns what is popular across the entire literature, and any one
journal contributes a row or two, so filtering after the fact finds almost
nothing and reads as though the journal has never published on the subject.

The name must match in full. `"Internet of Things"` is not `"IEEE Internet of
Things Journal"` and `"Water Research"` is not `"Water Research X"`; matching on
a substring would count a different journal as the target, which turns a failed
fit check into a pass. If no journal matches exactly, the run says so.

This is what answers the fit half of a desk reject. A manuscript that cites
nothing published in the journal it is being sent to reads as sent to the wrong
address, and the fix is to read what that journal has published on the subject
and cite what genuinely bears on the argument.

## Taking the entry from the registrar

```bash
python litsearch.py --bibtex 10.1016/j.watres.2024.121989 10.1038/s41467-024-49276-z
```

Never type a bibliography entry. Typing is where fabrication enters: the year
drifts, the volume is guessed, a word leaves the title, and none of it is
visible again. Ask doi.org for the record, which answers for Crossref, DataCite
and the rest.

Three things the emitted entry already handles. Capitals in the title are braced,
because a numeric style otherwise prints `SARS-CoV-2 RNA` as `Sars-cov-2 rna` in
the reference list, permanently and invisibly from the source. The key is built
from the first author and year with accents folded rather than deleted, so a name
survives as `munoz2018` instead of `muoz2018`. And a record deposited with no
title at all is filled from the index or refused, rather than emitted as an
anonymous line no reader can follow.

Diagnostics go to stderr, so redirecting stdout into a `.bib` gives only entries.
Check the DOIs afterwards with `litcheck --verify` anyway: generating an entry
proves the DOI resolves, not that the work says what you are about to cite it
for.

## The mechanical half

```bash
python litcheck.py references.bib manuscript.tex
python litcheck.py references.bib manuscript.tex --verify --mailto you@example.org
```

Without `--verify` it is offline: bibliography hygiene, entries cited but
missing, entries never cited, duplicate DOIs and titles, the self-citation share,
the recency profile, and every novelty claim with whether anything is cited
around it.

With `--verify` it resolves every DOI through doi.org content negotiation — which
answers for Crossref, DataCite and the rest, so Zenodo deposits resolve too — and
compares the registered title and year against the entry. That is what catches a
reference that does not exist, or exists and is a different paper.

It also reports **how many works are cited** and **how old they are**, which are
two different failures. A bibliography can be short and entirely current, or long
and entirely stale, and a reviewer reads both as not following the field. Thirteen
cited works in a submission to a strong journal is a problem regardless of how
recent they are; a median citation eight years behind the field is a problem
regardless of how many there are. Pass `--min-refs` to set the floor for the
venue.

Two things it will report that are worth understanding before acting on them.
**Entries never cited** do not reach the PDF, so they harm nothing; a large
number of them usually means the file was inherited from another manuscript, and
that is worth cleaning but is not a defect. **Novelty claims** are reported
whether or not they are placed, because whether the surrounding citation actually
supports the claim is not something a script can judge.

## Chaining

Work in both directions from what is already known:

* **backward** — the references of the closest paper, and their references;
* **forward** — what cites it since, which is where the field has moved.

Prefer the primary source for a specific claim. Use reviews to map a field, not
as the evidence that something is new. Read the paper you are about to say is
different from; an abstract is not enough to establish overlap.

## Classifying what you find

For each result that touches the idea, decide which it is:

* **the same thing** — the idea is published; the project needs redirecting;
* **the same question, different method** — the contribution is methodological
  and must be stated that way;
* **the same method, different question** — the contribution is the application,
  which is a weaker but legitimate claim;
* **adjacent** — worth citing so a reader is not left wondering;
* **unrelated** — do not cite it to look thorough.

Say which one applies, name the paper, and put the classification in the text
rather than leaving the reader to infer it.

## Placing a novelty claim

A novelty claim has to name what it is new against. "To our knowledge, no
previous study has X" is only defensible if the nearest studies are cited in the
same breath and the difference is stated.

The failure to watch for is a claim that distinguishes itself from several
established concepts and cites none of them. If a passage says the work must not
be confused with six known ideas, those six ideas each need a reference; a
reviewer who works on any of them will start there.

Prefer the specific form. "The gate is applied before the optimiser rather than
folded into it, unlike [refs]" survives review. "Novel framework" does not.

## Done

Every DOI resolves and its registered title matches the entry. Every citation
has an entry and every claim of novelty names what it is new against, with the
nearest work cited beside it. Where the literature could not be searched, the
report says so and novelty is marked UNVERIFIED rather than assumed.
