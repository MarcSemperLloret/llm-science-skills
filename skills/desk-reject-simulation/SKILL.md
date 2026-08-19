---
name: desk-reject-simulation
description: >-
  Simulate the editor's first screen before a manuscript is submitted, and
  decide whether it would be desk rejected. Use when a paper is being prepared
  for submission, when choosing or changing the target journal, when a cover
  letter is being written, or when the user asks whether a draft is ready to
  send. Runs the mechanical submission checks that can be automated and then
  the judgement half of the screen: scope fit, whether the claim is new,
  whether it is supported, and whether the framing is honest. Returns DESK
  REJECT, BORDERLINE or SEND OUT with named reasons.
---

# Desk reject simulation

A handling editor decides in ten to twenty minutes, before any reviewer is
approached, and most journals reject half or more of submissions at that stage.
The decision is made from the title, the abstract, the figures, the last
paragraph of the introduction and a skim of the conclusions — roughly in that
order, and almost never by reading linearly.

Simulate that. The job is not to praise the paper; it is to find the reason an
editor would use to stop it, and to say whether that reason is fixable before
submission.

## Read it the way an editor does

Do not read from the first page. Read:

1. **Title and abstract.** Can you state the claim in one sentence, and does the
   abstract itself contain the evidence for it?
2. **The figures.** Editors look at figures early because they are fast. Are
   they legible, and does the main one show the result?
3. **The last paragraph of the introduction**, where the contribution is
   claimed.
4. **The conclusions**, checked against the abstract for consistency.
5. **The statements**: funding, competing interests, data availability, ethics
   where relevant.

Only then, if it is still alive, read the methods.

## The mechanical half

Run it first; it is free and it settles a third of the screen.

```bash
python deskcheck.py manuscript.tex manuscript.pdf
python deskcheck.py manuscript.tex --abstract-max 200   # journal's own limit
```

It checks the required statements, the abstract and title lengths, keyword
count, whether every figure and table is actually cited in the text, leftover
TODO and placeholder markers, undefined references and citations from the LaTeX
log, and whether the AI declaration names a product.

Two of these are worth naming because they are invisible while writing and
obvious to an editor: **a float that is never cited**, and **an abstract a few
words over the limit**. Both have appeared in real submissions from this group.

Figures are screened with the `scientific-figures` skill; the statements come
from `manuscript-starter`. If either has not been run, run it before this one.

## The three reasons editors actually give

Format and missing statements stop a submission, but the desk rejects that come
with a sentence of explanation are almost always one of three. The script checks
each as far as a script can.

**Too few references, or too old.** An editor who opens a submission to a strong
journal and finds thirteen citations has already decided. It is read as not
knowing the field, and it is said out loud in the rejection. Volume and currency
are separate: short and current fails, long and stale fails.

**Insufficient novelty.** The editor is not judging whether the work is new. They
are judging whether the paper *says* what is new and against what. A manuscript
that never states the claim leaves them to construct it, and the safe thing to do
with a paper you cannot place is return it. The check finds every novelty claim
and whether anything is cited around it — and reports when there is no claim at
all, which is the more common failure here.

**Poor fit.** The strongest mechanical signal is the bibliography: a submission
that cites nothing published in the journal it is being sent to reads as sent to
the wrong address, whatever its subject. Pass `--journal` or let the script read
`\journal{}` from the source.

```bash
python deskcheck.py manuscript.tex --journal "Water Research" --min-refs 40
```

Fixing fit by adding citations from the target journal is not gaming it. If the
paper genuinely belongs there, that conversation exists and should already be
cited; if it does not exist, that is the answer about fit.

## The judgement half

Answer each of these out loud, with the evidence, and name the ones that fail.

**Scope.** Is this the journal's subject, at the journal's level of generality?
The commonest desk reject is not a bad paper, it is a good paper at the wrong
address. If the answer is "it is close", the answer is no.

**Claim.** Can you state the contribution in one sentence without using the word
"novel"? Does the abstract's final sentence say what is now known that was not
known before? A paper that describes what was done rather than what was found
reads as a report, not a result.

**Support.** For each claim in the abstract, point at the figure, table or
number that establishes it. A claim with no anchor is the reason an editor
stops. Watch for the claim that grew between results and abstract.

**Novelty, honestly.** Has the literature check been done, and does the paper
say plainly how it differs from the closest published work? A paper that does
not position itself forces the editor to do it, and the safest thing an editor
can do with a paper they cannot place is reject it.

**Interest.** Would the journal's readership care about this result if it were
true? Being correct is not sufficient. A negative or null result needs an
explicit argument for why it matters, and that argument belongs in the abstract.

**Honesty of framing.** Are the limitations stated where a reader meets the
claim, or buried at the end? Is any correlation written as if it were a
mechanism? Is a subgroup result presented as if it had been pre-specified? An
editor who catches one instance of over-claiming re-reads everything else
suspiciously.

**Self-containment.** Does the abstract work alone, do the captions work alone,
does the first figure work alone? Editors read them alone.

**Presentation.** Enough grammatical noise to slow reading is itself a reason to
reject: it signals the paper was not finished.

## The verdict

Report one of three, with reasons, and never a bare score:

**DESK REJECT** — name the single reason an editor would use, and say whether it
is fixable before submission or requires a different journal.

**BORDERLINE** — say what tips it either way, and what change would move it.
This is the most useful verdict when it is true; do not inflate it to SEND OUT.

**SEND OUT** — the paper would go to review. Say what the reviewers will attack
first, because that is the next thing to strengthen.

For each finding give the location and the fix. "The abstract over-claims" is
not usable; "the abstract says the mechanism is established, and Section 4 shows
an association with no manipulation" is.

## Rules

State the verdict before the detail, so it cannot be softened by the reading.

An editor's screen is not a peer review. Do not audit the statistics line by
line here — that is the reviewer's job and it is not what stops a submission at
this stage.

Do not recommend a journal you have not checked the scope of. If the target is
not known, say the verdict is conditional on it.

Never soften the verdict because the work was effortful. The purpose of the
simulation is to spend the rejection here rather than at the journal.
