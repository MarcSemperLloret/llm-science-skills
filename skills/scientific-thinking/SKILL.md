---
name: scientific-thinking
description: >-
  Reason about a scientific question with the discipline the question deserves,
  rather than producing the most fluent account of it. Use when interpreting a
  result, when asked what something means or why it happened, when a mechanism
  is being proposed, when deciding what a finding supports, and whenever a
  conclusion is about to be stated. Separates observation from inference from
  speculation, forces competing explanations before commitment, and keeps
  confidence proportional to evidence. Not a substitute for a statistical
  review or a pipeline audit.
---

# Scientific thinking

A language model's characteristic failure in science is not ignorance. It is
**fluency**: a coherent, confident, well-written account of why the result came
out that way, produced just as readily when the account is wrong. Nothing in the
prose distinguishes the two, which is why the discipline has to be imposed from
outside the writing.

This skill is about the moment a conclusion is formed and stated. It does not
run experiments, audit pipelines or review manuscripts.

| that job | belongs to |
|---|---|
| did the pipeline compute what we think | `silent-failure-audit` |
| does the idea deserve a project | `research-feasibility` |
| what has been established already | `literature-check` |
| would a reviewer accept the draft | `peer-review-simulation` |

## The sequence

1. **State the observation** — what was measured, in what units, on what units
   of analysis, under what conditions.
2. **Say what it supports** on its own, before any explanation is attached.
3. **Generate competing explanations**, at least two that are not the obvious
   one, before committing to any.
4. **Name the assumptions** each explanation needs in order to be true.
5. **Derive a prediction that separates them** — an observation the explanations
   disagree about.
6. **Look for the evidence that would disconfirm the preferred one**, not the
   evidence that would support it.
7. **Quantify the uncertainty**, including the part that is not statistical.
8. **State a conclusion proportional to all of that**, and say what would change
   it.

The order matters. Steps 3 and 4 done after step 8 produce a defence of a
conclusion already reached, which is a different activity that reads the same.

## Eight rules, and why each one

**Do not inherit the user's hypothesis as the default explanation.** When
someone asks "why does X cause Y?", the question has already supplied the
answer, and the fluent reply accepts the frame and explains the mechanism. Treat
the proposed explanation as one candidate among those generated in step 3, and
say so. If the observation does not support X causing Y at all, that is the
answer to give.

**Do not confuse plausibility with evidence.** A mechanism that sounds right,
fits what is known, and would explain the data if true has exactly zero
evidential weight from any of those properties. Plausibility determines what is
worth testing. It never determines what is true, and an account is not stronger
for being easier to tell.

**Do not convert association into mechanism.** The slide happens inside a single
sentence — "wastewater abundance tracks clinical resistance, so sewage reflects
the clinical burden" — and once made it is rarely revisited. Say what was
measured. A correlation across countries is a correlation across countries, and
it does not license a claim about what produces it, nor about what will happen
next year in one of them.

**Distinguish a capability from an association.** This is the same slide one
level up and it is the more expensive one. That a quantity ranks units correctly
does not mean it tracks change within a unit, and does not mean it predicts.
Those are three different claims, they need three different validations, and a
paper that establishes the first while claiming the third is the ordinary way
this goes wrong.

**Generate competing explanations before committing.** The alternative that
eventually kills a result is usually mundane: composition, coverage, selection,
a covariate that carries everything the interesting variable was supposed to
carry. Write down what would have to be true for the boring explanation to
account for the whole effect, then test that rather than the interesting one.

**Ask what observation would make the preferred explanation less likely** — and
go and look for it. An explanation nobody tried to break is not supported, it is
merely unchallenged, and the difference is invisible in the write-up.

**Distinguish absence of evidence from evidence of absence.** A test that did
not detect a difference has not shown equivalence. Say "no difference was
detected, and the interval still spans N" rather than "there is no difference".
The two are separated only by the power of the test, which means the honest
version requires knowing whether the test could have found the thing at all.

**Update confidence, do not switch between certainty and rejection.** A result
that weakens a hypothesis moves it down; it rarely eliminates it, and the next
result rarely restores it completely. State confidence in words that admit
degrees, and say which way the last piece of evidence moved it.

## Separate the three registers, in the text

Most damage happens because observation, inference and speculation are written
in the same voice. Mark them:

* **Observed** — this is in the data. Anyone can check it.
* **Inferred** — this follows from the observation given stated assumptions.
  Name the assumptions.
* **Speculative** — this is a hypothesis worth testing. It has not been tested
  here.

A reader who cannot tell which is which will assign the confidence of the
strongest sentence to all three. When drafting, the sentence that most needs the
label is the one that felt most natural to write.

## Predictions that could fail

The strongest form of this discipline is to write the prediction down, with a
date, before the analysis that tests it. Sealing it is not ceremony: it removes
the possibility of the prediction quietly becoming whatever the data showed.

**A falsified prediction is often worth more than a confirmed one.** It says the
model was wrong somewhere specific, which is information; a confirmation says
the model was not wrong in the one way that was checked, which is much less. A
prediction of "3 to 6 identifiable cases" that returns 20 of 24 has not wasted
the exercise — it has located the error in the calibration, which is a result.

Treat a prediction that cannot fail as a defect in the prediction.

## Uncertainty that is not statistical

Report the interval, and then report what the interval does not cover:

* the choices in preprocessing that could have gone another way;
* the units that were excluded, and whether their exclusion is related to the
  outcome;
* the reference taken as truth, which has its own error;
* whether the measurement means the same thing across groups, sites or years;
* how far the result travels — the population, region or period it was
  established on, versus the one it is being applied to.

A confidence interval is a statement about sampling. Most of what is uncertain
about a scientific result is not sampling.

## When asked to interpret a result

Answer in this order, briefly:

1. what the result is, in plain terms;
2. what it supports;
3. what it does not support, especially the interpretation most likely to be
   read into it;
4. the strongest alternative explanation, and whether it has been ruled out;
5. what would settle it.

Point 3 is the one that gets dropped under time pressure, and it is the one
carrying the value.

## Rules

Do not manufacture an explanation because one was asked for. "The data do not
distinguish these explanations" is a complete answer, and often the correct one.

Do not describe a result as consistent with a hypothesis without saying what
else it is consistent with. Consistency is cheap; almost everything is
consistent with almost everything.

Do not let the quality of the writing carry the confidence. If the evidence is
thin, the sentence must sound thin.

## Done

The observation is stated separately from its explanation. At least two
competing explanations were considered before one was preferred, and the boring
one was tested rather than dismissed. Assumptions are named. What would change
the conclusion is stated. Nothing speculative is written in the voice of
something observed. And the confidence expressed matches the evidence rather
than the fluency of the account.
