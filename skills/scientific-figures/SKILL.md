---
name: scientific-figures
description: Create, modify, review and polish publication-quality scientific figures, plots, charts, maps and multi-panel visualizations. Use when generating or editing figures for scientific papers, reports, theses, presentations of research results, or when the user asks to improve an existing scientific plot. Applies a shared matplotlib style, a final-size layout discipline and an automatic quality-control pass covering typography, colour, overlap, clipping, export format and font embedding. Do not trigger for decorative illustrations, UI charts, dashboards or casual exploratory plots unless publication-quality output is requested; for artifact, web or dashboard charts use the dataviz skill instead.
---

# Scientific Figures

A figure is publication-ready at its **final physical size**, or it is not ready.
Most figure failures are mechanical — text that is too small, a width that does
not match the column, Type 3 fonts, colliding labels. This skill makes those
mechanical, so that attention goes to the scientific message instead.

Do not hand-roll rcParams, palettes or export calls. Use the toolkit.

## The toolkit

```
scientific-figures/assets/     # the assets directory beside this SKILL.md
    publication.mplstyle   the style: final-size typography, Okabe-Ito, Type 42 fonts
    figstyle.py            figure(), label_panels(), shared_legend(), save(), palette C
    figcheck.py            deterministic QC; also a CLI for auditing exported files
    figtiles.py            cuts a rendered figure into tiles for close inspection
    figpage.py             scans a compiled PDF for captions running off the page
```

Put that `assets` directory on `sys.path`. Its location depends on where the
skills were installed — `~/.claude/skills/`, `~/.agents/skills/`, a plugin
directory, or a checkout inside the project — so use the path this SKILL.md was
read from rather than a hard-coded one.

```python
import sys
sys.path.insert(0, "<.../scientific-figures/assets>")
import figstyle as fs                       # importing applies the style

fig, axes = fs.figure("double", 3.2, ncols=2, sharey=True)
axes[0].plot(t, model, color=fs.C.blue, label="model")
axes[0].plot(t, ref, color=fs.C.grey, lw=1.0, label="reference")
axes[0].set_xlabel("Time (h)")
axes[0].set_ylabel("Anomaly (K)")
fs.label_panels(axes)                       # A, B, ... as layout-aware titles
fs.shared_legend(fig)                       # one legend, outside the panels
fs.save(fig, "figures/fig01")               # writes .pdf + .png, then prints QC
```

`fs.save()` prints a QC report. **FAIL means the figure is not publishable.**
Fix every FAIL. Each NOTE is a judgement call: act on it or decide it is
justified, but do not ignore it silently.

**A legend inside a panel is guilty until proven innocent.** Across three real
manuscripts, every single `legend-over-data` finding turned out to be a genuine
defect, and every one had been left as an accepted NOTE. A legend over the
plotted series is now a FAIL for that reason. When one fires, the fix is almost
never a different corner: on a panel small enough to have the problem, every
corner is occupied by something. Move the legend outside the panel, make it a
single figure-level key when several panels share the encoding, or label the
series directly and delete it.

The same holds for a key that serves more than one panel: it belongs to the
figure, not to whichever panel happened to create it.

**Read the whole report, and account for every NOTE out loud.** Do not grep the
output for `FAIL` and declare the figure done — the NOTEs are where the
judgement lives, and a legend sitting on the data comes back as a NOTE, not a
FAIL. When reporting to the user, list each NOTE and say what you did with it:
fixed, or declined and why. A count of failures is not a report.

To audit a figure produced elsewhere:

```python
from figcheck import check_figure, report
report(check_figure(fig, target_width=7.0))
```

```bash
python figcheck.py figures/fig01.pdf figures/fig01.png
```

Use another plotting library only when the project already uses it, when it
gives a clear technical advantage, or when the user asks. Never add a plotting
dependency for cosmetic reasons.

**Figures drawn in LaTeX** — TikZ, pgfplots — are outside the checker, which
inspects matplotlib objects. What still applies to them: every rule in this
skill, `figpage.py` on the compiled document, and looking at the rendered pages.
A pgfplots figure is automatically 1:1, since it is typeset in the document, and
its type sizes are the document's own (`ootnotesize` is 10 pt in a 12 pt
class), so the two commonest failures cannot happen. Check the rest by eye.

## Mandatory sequence

1. **Fix the message.** Name the claim the figure makes, the comparison that
   matters, and the encoding that shows it. Do not write a planning document.
2. **Fix the size.** Choose the column width first; everything else follows.
3. **Build it** with `fs.figure()` and constrained layout.
4. **Export with `fs.save()`** and clear every FAIL.
5. **Look at the PNG, then look at it in tiles.** Open the whole figure first to
   judge the composition. Then cut it up and look at each piece:

   ```bash
   python figtiles.py figures/fig01.png            # 2x2 tiles at 1.5x
   ```

   Open every tile and say what is in it. This is not optional and it is not the
   same as looking at the figure. A whole 5.4 in figure shown as one image is
   about a third of print resolution per region, and that is precisely the scale
   at which a tick label touching a marker, a scale bar resting on a coastline,
   a legend grazing a curve or a bracket cutting a value are invisible. Every
   one of those has survived a clean checker run and a full-figure look, and
   been obvious in a tile.

   Use a finer grid for dense multi-panel figures: `--grid 3 2`, or one tile per
   panel.
6. **Run the editorial pass** from the `figure-polish` skill, as a separate step
   with its own verdict. Do not skip it because step 4 came back clean and step 5
   showed no defects: zero FAIL means the figure is *correct*, and correct is the
   floor, not the goal. A figure can pass every check and still look like
   something a script produced. Steps 1–5 hunt for defects; step 6 asks whether
   anyone edited this.

## A figure is a picture, not a page of prose

The most common way a generated figure goes wrong is that it is talked into
existence: a sentence explaining the result, a note qualifying it, a line saying
what is not shown. All of that reads as clutter and none of it is what a figure
is for. The reader looks at a figure to *see* something.

Inside the graphic keep only what the eye needs: axis labels with units,
category names, a short direct label on a series, a value beside a point, the
panel letter, the legend or colorbar.

Everything else goes to the caption — what the intervals mean, what was excluded,
what the shading was computed from, how to read the comparison. The caption has
room and is set in the manuscript's own type; the figure has neither.

**The full stop is the tell.** Labels, values and units do not end in one;
sentences do. If a line of text inside a figure ends in a full stop, it is a
caption sentence in the wrong place, however short — "Brackets are the two
pre-specified primary comparisons." is 54 characters and still belongs under the
figure. The checker flags any text that ends in a full stop, and any block over
90 characters.

**Read the caption before you ship the figure.** This is not optional and it
cannot be automated: open the manuscript, read the caption, and delete from the
graphic everything the caption already says. Figures accumulate text that the
author later wrote into the caption as well, and nobody goes back to remove the
first copy. In one real manuscript, four of five figures each carried a block
that its own caption repeated word for word.

When a sentence has to come out and the caption does *not* already carry it, put
it there, and adjust any caption sentence that referred to what you removed.

**Figures are written in the language of the manuscript, which is English.**
Every label, unit, category, legend entry and annotation. This is the easiest
thing in a figure to leave half-done, because the author reads both languages
and never notices; the reviewer does. Proper nouns keep their own spelling —
station and place names are not translated. The checker flags any label with two
or more Spanish or Catalan function words in it.

**Minimum sufficient, not minimum.** The rule has a floor. A panel with no
scale, no axis label, no legend and no annotation satisfies every text budget
and tells the reader nothing; a cluster labelled `A`, `B`, `C` passes too, and
sends the reader to the caption to find out what A is. Strip text until removing
one more thing would make the panel unreadable on its own — then stop.

When a label has to stay, make it the name the rest of the figure already uses.
A second naming scheme (letters for one thing, words for the same thing in the
legend) costs the reader more than the words it saved. The checker flags a panel
with data and no text at all; that NOTE is legitimately declined when a shared
legend or the caption names every element, and only then.

## Size

`fs.figure(width, height)` takes `"single"` (3.35 in), `"onehalf"` (5.5 in),
`"double"` (7.0 in), or a number when the journal specifies one. Height defaults
to a sane ratio; override it from the content, not from a fixed aspect.

| layout | typical height |
|---|---|
| single column, one panel | 2.5–3.0 in |
| double column, one panel | 3.0–4.0 in |
| two panels side by side | 2.8–3.5 in |
| 2×2 panels | 5.5–6.5 in |

**The figure must enter the manuscript at 1:1.** Include it as
`\includegraphics{fig01}`, or as `[width=\linewidth]` only when the designed
width already equals `\linewidth`. Any other scaling shrinks the type below the
legibility floor and silently invalidates every size decision made here. When
the figure is too wide, redesign it at the narrower width; never rescale.

Never solve a layout problem by shrinking text until it fits. Reduce the number
of ticks or categories, change the layout, or drop information.

### Measure the text width, do not assume it

Every document class has its own. Compile a three-line stub with the manuscript's
own `\documentclass` line:

```latex
\documentclass[<the manuscript's options>]{<its class>}
\begin{document}\typeout{TEXTWIDTH=\the\textwidth}x\end{document}
```

The result is in TeX points; divide by 72.27 for inches. Then design at that
width and verify the export against it:

```bash
python figcheck.py --width 5.40 figuras/*.pdf
```

Then grep the manuscript for every `\includegraphics` of the figure and check for
a hidden scale factor — `[width=0.86\textwidth]` silently shrinks a 10 pt label
to 8.6 pt. Either remove the factor or design at the reduced width.

### Use the width you asked for

A figure claims the full text width, so it should fill it. The commonest way it
does not is a **fixed aspect ratio**: a square panel in a full-width row is drawn
as wide as it is tall, and the rest of the row is blank page. The checker
measures each panel against the cell it was given and flags anything under 78%.

The fix is not to stretch the panel — an equal aspect is usually there for a
reason, so that a 45-degree line reads as 45 degrees. Put the square panel
*beside* another one. A stacked figure whose lower panel is square is nearly
always better as one row of two, and it loses height at the same time, which is
what the caption needs.

A sparse panel is the same problem in another form: four bars do not need a
full-width row either.

### The figure must leave room for its caption

A figure is not sized against the text width alone. **Figure height + caption
height must fit the text block**, and the caption is often ten or fifteen lines
once everything that does not belong in the graphic has been moved into it. When
the two together exceed the page, the caption keeps setting past the bottom
margin and prints over the page number. LaTeX frequently does not warn: the
float box is not overfull, the caption has simply run into the margin.

Nothing in the figure itself can detect this, so it is checked on the compiled
document:

```bash
python figpage.py main.pdf
```

FAIL means a caption is printing over the folio. NOTE means a page runs deeper
than the rest of the document. Run it after every compile that touched a figure.

The fix is a trade between two levers. Shorten the figure first — a tall figure
usually has a stackable row or a repeated label to give up. If it will not go
far enough, shorten the caption, and prefer cutting what the body text already
says. Budget roughly 12.5 pt per caption line at 12 pt body type.

Expect the shrink to break the layout: fixed-size type moves closer to
everything positioned in axis fractions. Re-run the figure checks after every
resize.

### Never audit the file on disk

Exported figures go stale. A figure whose script has been fixed since the last
export tells you nothing about the current code, and the file that reaches the
journal is whatever is on disk. Regenerate first, then audit, then look.

## What the checker enforces

FAIL: text below 7.5 pt · text clipped at the canvas edge · overlapping text ·
width off target · `jet`/`rainbow`/`turbo` · Type 3 fonts in the PDF · PNG below
300 dpi.

NOTE: text that reads as a sentence · a panel carrying three or more blocks of
prose · the same axis label repeated across panels · text lying over the data ·
labels from adjacent panels that nearly touch · matplotlib default palette ·
missing axis label · excessive decimal precision · long titles inside the graphic
· heavy gridlines · more than six legend entries · mixed font families ·
non-standard width or excessive height.

The NOTEs need judgement and some are legitimately declined — a scale-bar label
resting on its own bar, a value crossing a hairline reference rule. Decide each
one; do not skip them.

Everything else is your judgement: whether the encoding fits the claim, whether
the hierarchy makes the result obvious, whether the colours mean something,
whether the figure is honest.

## Judgement, in brief

* Simplest encoding that carries the result; points with intervals rather than
  bars for continuous estimates.
* Units on every axis. Decimal precision a reader can act on.
* Same quantity, same colour, across the whole manuscript. Context in `C.grey`.
* Show uncertainty when it exists; never invent it.
* No figure title — the manuscript caption carries that text.
* Never retouch an exported file by hand; fix the script.

### Panels in a row must be visibly separate

Two panels side by side are read as two things only if the eye can see where one
ends. A title running into the next panel's letter, a value label abutting the
next panel's tick labels, a colour bar pressed against the neighbour — all read
as one crowded block even when nothing technically overlaps, and the checker's
overlap test will pass them.

When the gap looks tight, widen it: raise `wspace`, prune the last tick of the
left panel, shorten the title, or move a label inward. Do not shrink type to
make room.

Details when you need them:

* `references/encodings.md` — figure type, axes, uncertainty, colour, legends,
  multi-panel composition.
* `references/maps.md` — projections, geospatial layers, rasterisation.
* `references/visual-guidelines.md` — the decisions the style encodes: type
  scale, colour roles, line weights, spacing, labelling, export. Read it when
  building outside `figstyle` or when a project needs its own style.
* `references/traps.md` — matplotlib behaviour that silently breaks a figure:
  tight bboxes, colour bars in a gridspec, panel-letter offsets, phantom ticks.
  Read this one when a layout fails in a way that makes no sense.
* `references/integrity.md` — statistical honesty, captions, consistency across
  a manuscript, modifying an existing figure, journal overrides.

## Efficiency

Iteration is the expensive part. Before changing anything after a render, name
the specific defect and its cause, then make the smallest change that addresses
it. Do not tune values blindly, do not regenerate figures that did not change,
and do not re-run the analysis pipeline when cached inputs exist.

## Done

The figure is done when the code runs, `fs.save()` reports zero FAIL, every NOTE
has been acted on or consciously accepted, the PNG has been looked at, the
caption has been read and its duplicates removed from the graphic, the
`figure-polish` review has been applied and answered, and the analysis was not
touched on the way.

Zero FAIL is not done. It means nothing is broken. Quality is judged in
`figure-polish`, and that judgement is part of finishing, not an optional extra.
