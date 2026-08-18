---
name: manuscript-starter
description: Start a new scientific manuscript, or set up its repository, with the house front matter and end matter already filled in. Use whenever a new paper, preprint or manuscript directory is being created, when a LaTeX skeleton is needed, or when the author block, CRediT statement, funding, competing-interest or AI declaration has to be written. Supplies the fixed authorship, affiliation, funding grant, CRediT wording and AI declaration verbatim, the shared LaTeX conventions, and the git setup. Do not ask the user for any of these; they do not change between papers.
---

# Manuscript starter

Everything in this skill is settled and does not change from paper to paper.
Copy it. Do not ask which authors, which affiliation, which grant, how to word
CRediT, or whether to name the AI tools — asking is the failure this skill
exists to prevent.

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

## The authorship, verbatim

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

Fixed, in `endmatter.tex`. All three authors share every role and the statement
ends with **"All authors contributed equally to this work."**

The grant is always:

> This work was supported by Grant PID2025-175296OB-I00 funded by
> MICIU/AEI/10.13039/501100011033.

## The AI declaration

Sober and generic. It states what was done — editing and language, literature
and online searches, software and figure scripting — and nothing else.

**Never name a model, a vendor, a product or an access date.** Not "OpenAI
Codex", not "Claude", not "GPT", not "accessed 17 August 2026". One earlier
manuscript named a tool and it had to be taken out; do not reintroduce the
pattern.

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
