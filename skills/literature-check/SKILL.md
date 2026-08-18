---
name: literature-check
description: Check what a manuscript claims against what the literature actually says, and verify that every reference exists and says it. Use before claiming novelty, when assessing whether an idea is already published, when a bibliography is being assembled or cleaned, before submitting, and whenever research-feasibility needs its literature check. Verifies DOIs against the registry, finds references cited but missing and entries never cited, and locates every novelty claim so it can be defended. Do not use to write a related-work section from memory.
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

## Never assert a reference from memory

A citation is a factual claim about a document. Producing one without checking it
resolves is the single most damaging thing that can be done here, and it has
become common wherever drafting is assisted.

If a search tool is available, search. If it is not, say plainly that the
literature could not be checked and mark novelty **UNVERIFIED**. Do not fill the
gap with plausible-looking references, do not reconstruct a DOI, and do not
attach a citation to a claim without having seen that the work supports it.

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

Two things it will report that are worth understanding before acting on them.
**Entries never cited** do not reach the PDF, so they harm nothing; a large
number of them usually means the file was inherited from another manuscript, and
that is worth cleaning but is not a defect. **Novelty claims** are reported
whether or not they are placed, because whether the surrounding citation actually
supports the claim is not something a script can judge.

## Searching, when a search tool is available

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
