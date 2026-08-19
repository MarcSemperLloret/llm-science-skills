---
name: editorial-figures
description: >-
  Build a chart that carries its own conclusion, for a report, README, slide
  deck, poster, blog post or social image — anywhere the figure travels
  without a caption underneath it. Uses an editorial style with a headline, a
  standfirst, direct annotation of the finding and a source line, in the
  manner of the Financial Times or The Economist but with our own palette and
  type. Do NOT use for journal or manuscript figures, where the caption
  carries the title and an in-figure headline is wrong; use scientific-figures
  for those.
---

# Editorial figures

A manuscript figure is read with its caption underneath and a reader who has the
method section. An editorial figure is read alone, on a screen, by someone who
will give it four seconds. That difference sets everything here.

**This skill and `scientific-figures` are opposites on one axis.** There, a
title inside the graphic is wrong and a sentence is caption material. Here, the
title *is* the finding and one sentence of annotation is the point. Never let
these rules cross: a headline in a journal submission is a defect, and journals
strip or reject in-figure titles.

If the figure is going into a paper, stop and use `scientific-figures`.

## The style

```
editorial-figures/assets/editorial.mplstyle   (beside this SKILL.md)
```

Same identity as the paper style — same Okabe–Ito palette, same neutrals, same
restraint — with the medium's differences: 11 pt base type instead of 8, a bold
left title, no left or top spine, a horizontal grid doing the work of the y
ticks, and heavier lines that survive a slide.

```python
from pathlib import Path
import matplotlib.pyplot as plt

SKILLS = Path("<... the directory holding these skills ...>")
plt.style.use(SKILLS / "editorial-figures/assets/editorial.mplstyle")
```

The checker still applies. Import `figcheck` from the `scientific-figures`
assets and run it: overlap, clipping, tiny type and font embedding are wrong in
any medium.

```python
import sys
sys.path.insert(0, str(SKILLS / "scientific-figures/assets"))
from figcheck import check_figure, report
report(check_figure(fig))
```

Four of its findings are expected here and are declined out loud, with the
reason. `width`, because the sizes in this skill are screen sizes and match no
journal column deliberately. `prose` twice, once for the standfirst and once for
the source line, both of which are sentences on purpose. And `axis-label` when
the category names carry the axis, which is the usual case in an editorial bar
or dot chart.

Everything else it reports is a defect, including every overlap. FAIL is never
declined here.

## The anatomy

Four elements, in this order down the page:

1. **Headline** — the finding, as a sentence. Not "Model accuracy by reference"
   but "Model rankings change when the observational reference changes". If you
   cannot write the headline, the figure has no point yet and no amount of
   styling will give it one.
2. **Standfirst** — one line, lighter and smaller, saying what the reader is
   looking at or qualifying the headline.
3. **The chart**, with the series labelled directly and the one thing that
   matters annotated in place. No legend if two or three series can be named on
   the plot.
4. **Source line** — small, grey, at the foot: where the data came from, and the
   date if it moves.

Reserve the two bands before drawing anything. The style turns on
`constrained_layout`, which knows about axes, titles and colour bars and knows
nothing about a `fig.text` you place at a figure fraction. It re-packs the axes
at draw time to fill the figure, and the standfirst then lands on the top row
while the source line lands on the x axis label.

`fig.subplots_adjust` does not fix this. `constrained_layout` discards those
margins silently — no warning, no error, and the saved image looks like the code
was ignored, because it was. Tell the layout engine the rectangle it may fill:

```python
fig, ax = plt.subplots(figsize=(8.0, 4.4))
fig.get_layout_engine().set(rect=(0.0, 0.07, 1.0, 0.74))   # left, bottom, w, h

fig.suptitle("Model rankings change when the reference changes",
             x=0.012, y=0.95, ha="left")
fig.text(0.012, 0.855, "Skill of six forecast systems against ERA5 and "
                       "against stations",
         ha="left", va="top", color="#666666", fontsize=10)
fig.text(0.012, 0.035, "Source: AVAMET, ERA5. 2019–2025.",
         ha="left", va="bottom", color="#888888", fontsize=9)
```

The numbers are a starting point, not a constant: a two-line standfirst or a
long source line needs a taller band. Run the checker and look at the image.

## Hierarchy

One thing is the point. Draw it in `#0072B2` or `#D55E00` at full weight and put
everything else in `#949494`. A reader should be able to see the finding with
the labels blurred.

Annotate the finding where it happens — an arrow to the crossing point, a word
at the end of the line that reverses — rather than describing it underneath.
One annotation, not four.

## What does not change from the paper style

* the palette, and colour assigned by role rather than by order;
* no spectral colormaps, ever;
* direct labelling before legends;
* units on every axis, and decimal places the measurement supports;
* a value that rounds to a signed zero is written as what it means — `no gain`,
  `no change` — because `-0.00` is not a quantity a reader can do anything with;
* no chartjunk, no 3-D, no pie beyond three slices;
* honest axes: no truncated bar baselines, no cherry-picked limits;
* the figure is regenerated from a script, never retouched by hand.

Statistical integrity is not a house style. It applies here exactly as it does
in a manuscript: see `scientific-figures/references/integrity.md`.

## Sizes

| use | width |
|---|---|
| README, blog, report body | 8.0 in at 200 dpi |
| slide, full bleed | 13.3 in, 16:9 |
| social card | 8.0 x 4.2 in, exported PNG |

Screens are not paper: export PNG at 200 dpi rather than PDF, unless the report
is itself typeset.

## Done

The headline states a finding. A reader who sees only the figure understands it.
The main series is visually dominant. Nothing is unlabelled and nothing is
labelled twice. The checker reports no FAIL. You have looked at the rendered
image — and at its tiles, with `figtiles.py`, if it is dense.
