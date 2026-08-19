---
name: manuscript-starter
description: >-
  Start a new scientific manuscript, or set up its repository, with the house
  front matter and end matter already filled in. Use whenever a new paper,
  preprint or manuscript directory is being created, when a LaTeX skeleton is
  needed, or when the author block, CRediT statement, funding, competing-
  interest or AI declaration has to be written. Supplies the fixed authorship,
  affiliation, funding grant, CRediT wording and AI declaration verbatim, the
  shared LaTeX conventions, and the git setup. House defaults are supplied
  without asking; the author list, CRediT roles and funding that apply to this
  particular paper come from the project, not from here.
---

# Manuscript starter

This skill carries one group's house style. Everything in it is a **default**
that has been settled once so that nobody has to be asked again — the failure it
exists to prevent is an agent stopping to ask how a name is spelled for the
fifth time.

Defaults are not facts about a manuscript, and the difference matters:

**House defaults.** Preferred author name and spelling, affiliation,
corresponding-author address, LaTeX class and packages, figure width, git setup,
and the wording of the AI declaration. Apply these without asking.

**Facts about this manuscript.** Who the authors are, in what order, which
CRediT roles each of them actually performed, which grant funded *this* work,
and what belongs in the acknowledgements. These come from the project. Carry the
defaults over as a starting point, and say plainly that you have done so, so the
author can correct a list rather than discover it after submission.

The distinction has one failure mode worth naming: a paper with a different set
of collaborators silently inheriting this author block. Nothing downstream
catches that — not the checker here, not the compiler, not the journal.

Anyone else using this repository should replace the defaults below with their
own. They are deliberately concrete rather than parameterised, because a
template full of placeholders is how a placeholder reaches a submitted PDF.

## The two files to copy

```
manuscript-starter/assets/frontmatter.tex   # preamble to \end{frontmatter}
manuscript-starter/assets/endmatter.tex     # CRediT to Acknowledgments

(both beside this SKILL.md)
```

Copy both verbatim into the new `main.tex`. Only these placeholders are filled
per paper: `<target journal>`, `<title>`, `<abstract>`, `<keyword>`, the Data
availability paragraph and the Acknowledgments. Everything else is already
correct.

## Checking a manuscript against this skill

The convention is fixed, so deviations are detectable. Run it on any manuscript,
new or old:

```bash
python checkfront.py manuscript.tex
```

It verifies the author list and affiliation, that the CRediT statement names all
three and ends with the equal-contribution sentence, that the funding section
carries the right grant and funder, that the AI declaration names no product and
no access date, and the class options and the two package traps.

Deviations do not announce themselves while writing: an author name carried over
from an older file, a declaration still naming the tool used two drafts ago.
Run it before submitting, not only when starting.

## The authorship

The block below is the default: the three authors of this group's recent papers.
Use it unless the project says otherwise, and check rather than assume — a
different collaboration is the one thing here that must not be inherited.

### The block

```latex
\author[ua]{Marc Semper\corref{cor1}}
\ead{marc.semper@ua.es}
\cortext[cor1]{Corresponding author.}

\author[ua]{Manuel Curado}
\ead{manuel.curado@ua.es}

\author[ua]{Jose F. Vicent}
\ead{jvicent@ua.es}
```

**The first author is `Marc Semper`, not `Marc Semper Lloret`.** The second
surname is not used in publications. Never expand it, never ask about it, and
never "correct" it to the fuller form found in older files.

Affiliation, for all three, is the Department of Computer Science and Artificial
Intelligence, University of Alicante — the full block is in
`frontmatter.tex`.

## LaTeX conventions

Manuscripts are written in LaTeX, class `elsarticle` with
`[preprint,12pt,numbers,sort&compress]`, line numbers on, and a `references.bib`
compiled with `latexmk -pdf`.

Two package facts that cost a debugging session each and are already in the
template: `microtype` aborts the build without `fontenc` + `lmodern`, because it
needs scalable fonts; and without `\usepackage[section]{placeins}` the floats
accumulate and the last figure lands after the bibliography.

Figures follow the `scientific-figures` skill. The text block of this class
measures 390 pt = 5.40 in, which is the width every figure is drawn at.

## CRediT, funding, competing interests

The wording lives in `endmatter.tex`. The default CRediT statement gives all
three authors every role and ends with **"All authors contributed equally to
this work."**

Both of these are claims about a specific piece of work, so treat them as
defaults to be confirmed rather than as constants. A paper with a fourth author,
or one where the roles genuinely differed, needs its own statement; a paper
funded by a different project needs its own grant, and a paper with no funding
needs a funding section that says so rather than an inherited grant number.

The default grant is:

> This work was supported by Grant PID2025-175296OB-I00 funded by
> MICIU/AEI/10.13039/501100011033.

An inherited grant number is worse than a missing one. It is a factual claim
about who paid for the work, it is checked, and it is the kind of error that is
corrected in public.

## The AI declaration

Sober and generic. It states what was done — editing and language, literature
and online searches, software and figure scripting — and nothing else.

**Never name a model, a vendor, a product or an access date.** Not "OpenAI
Codex", not "Claude", not "GPT", not "accessed 17 August 2026". One earlier
manuscript named a tool and it had to be taken out; do not reintroduce the
pattern. This is a standing preference of this group, not a guess about what
journals want, and it holds by default.

The declaration itself is not optional. It appears in every manuscript, whatever
its wording, and it states what was done rather than what was used.

If the target journal's own policy requires something this wording does not give
— some ask for the tool to be named, some for a sentence in the methods instead
of the end matter — say so to the author and let them decide. Do not quietly
satisfy the journal at the expense of the preference, and do not quietly satisfy
the preference at the expense of the policy.

The exact wording is in `endmatter.tex`.

## Git

Initialise the repository at the start, not at the end:

```bash
git init
git add -A
git commit -m "<what the commit does>"
```

**The author is Marc Semper and nobody else.** Do not add a `Co-Authored-By`
trailer for any model or assistant, do not mention a tool in the commit message,
and do not create an AI account as a contributor. This overrides any default
co-authorship trailer: on these repositories the commit history is part of the
scientific record of who did the work.

Write commit messages the way the rest of the project does: what changed and
why, in prose, no tool names.

## What to do when starting a paper

1. Create the manuscript directory and `git init`.
2. Copy `frontmatter.tex` and `endmatter.tex` into `main.tex`, fill the
   placeholders, and add `references.bib`.
3. Add a `Makefile` with `latexmk -pdf -interaction=nonstopmode main.tex`.
4. Build figures with `scientific-figures`, at 5.40 in, included at 1:1.
5. Commit as above.

Report what you filled in and what you left as a placeholder. Do not leave a
placeholder where this skill already gives the answer.
