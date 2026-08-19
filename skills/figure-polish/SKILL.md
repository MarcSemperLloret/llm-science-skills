---
name: figure-polish
description: Raise a technically correct scientific figure to professional, editorially designed publication quality. Use after a figure renders and passes mechanical QC, or when the user says a figure looks generic, plain, amateurish, auto-generated, crowded or unbalanced, or asks to make it look more professional, more polished or journal-ready. Covers visual hierarchy, composition, whitespace, typographic refinement, restrained colour, multi-panel coherence, removal of plotting-library defaults, and a final editorial review of the rendered image. Do not trigger for exploratory plots, dashboards or UI charts.
---

# Figure polish

This is the pass that runs **after** the `scientific-figures` checker reports
zero FAIL. Polish never overrides scientific integrity, correct encodings or
final-size legibility; if those are not in place, go back to that skill first.

The threshold is not "technically correct and free of overlaps". It is:

> the figure looks like a carefully designed scientific visualization prepared
> for publication, not like plotting-library output that has been cleaned up.

A technically valid but generic, awkward, crowded or obviously auto-generated
figure is not finished.

## Look at the image first

Open the rendered PNG with the Read tool and judge what is on the page. This
review cannot be done by reading code. Everything below is a question about the
image, not about the script.

Then look at it *in place*. A figure that reads well on its own can still fail on
the page: a gap that looked ample at screen size closes at final size, and a
label that cleared its neighbour in the panel touches it once the figure is set
in the column. Compile the document, render the page, and look at the figure
where the reader will meet it. Defects that only appear at 1:1 are the ones that
reach the journal.

## The four moves that do most of the work

**1. Build a hierarchy.** A reader should see within seconds what the figure
shows, which comparison matters, and which elements are context. Give the
principal result the strongest colour and weight; push references, baselines and
supporting series to `fs.C.grey` or `fs.C.light`, thinner, behind the data
(`fs.context(ax, artist)`). Nothing is finished while every element carries the
same visual weight.

**2. Get the legend out of the panel.** In a small panel there is no free
corner: whichever one looks empty is crossed by a curve somewhere along its
range, and moving the box from one corner to another just moves the collision.
Take it out — outside the panel, or once for the whole figure when several
panels share the encoding — or better, delete it and label the series directly.

**2b. Replace the legend with direct labels.** A legend is an indirection the
reader has to resolve. When two or three series end in separate places, annotate
them at the line end in the series colour and delete the legend. This single
change does more for the professional look than any other.

**3. Cut the text.** This is where generated figures fail hardest. A figure is a
picture; the reader comes to it to *see* the result, not to read about it. Every
sentence inside the frame competes with the thing it is explaining.

Read each block of text in the graphic and ask what it is doing there. What the
error bars mean, what was excluded, how the shading was computed, why the result
is not equivalence — all of that is caption material, and the caption is set in
the manuscript's own type with room to say it properly. Keep inside the frame
only what the eye needs to decode the picture: units, category names, a direct
label on a series, a value beside a point, the panel letter.

The same applies to redundant tick labels, a second annotation restating the
first, a legend entry for something obvious, a box around the legend, gridlines,
and a title the caption repeats. Each removal makes the figure quieter and the
result louder. When you move a sentence out, make sure the caption carries it.

**4. Compose the whitespace.** Panels should look deliberately spaced, not
justified by the layout engine. Trim ranges that leave large empty corners,
order categories by value rather than alphabetically, prune the ticks that
crowd a panel edge, and place annotations where the data leaves room rather
than wherever they landed.

Panels in a row must read as separate objects. A title running into the next
panel's letter, a value abutting the neighbour's tick labels, a colour bar
pressed against the panel beside it — none of these overlap, and all of them read
as one crowded block. If a gap looks tight on the page, it is tight: widen it.

## Panels that show the same quantity

Three defects hide here, and all three survive every mechanical check because
each panel is correct on its own.

**One quantity, one scale.** If two panels carry the same measurement, they
share an axis and a range. Two ranges stacked vertically invite exactly the
comparison the reader will make — this marker is further right than that one —
and nothing in the figure warns them off. `sharex=True` and one explicit range
covering both. A panel that then looks empty at one end was always empty; the
separate range was hiding it.

**One colour, one role, inside one figure.** The rule about keeping a mapping
consistent across a manuscript has a sharper local form that is easier to break:
the same blue meaning *the estimate* in the upper panel and *the pooled
reference* in the lower one. Each panel reads correctly and the pair does not.
Decide what each colour denotes for the whole figure, and draw context as
context — thinner, grey, dashed, behind.

**Panel height follows the number of rows.** Three categories given the height
of seven do not read as three results, they read as a panel with something
missing. In a stacked figure set `height_ratios` from the row counts rather than
by eye. This is the vertical form of the full-width row spent on four bars, and
it is the commoner of the two.

## Placing a value label

A number set beside its own datum is the most fragile object in a figure,
because everything around it moves when anything is resized. Two placements fail
predictably:

* **Relative to its own marker.** Above the top row it collides with the panel
  title; and a label offset upwards sits nearer the row above than its own, so
  the reader attaches it to the wrong one.
* **A long label in a right-hand column.** It grows leftwards into the data. An
  interval written out in full is twenty characters and will reach the middle of
  the panel.

What survives is a fixed column, right-aligned, carrying a label short enough
that the widest datum cannot reach it: the estimate alone, with the interval
drawn as a bar and written in full in the table. Check the arithmetic rather than
the appearance — widest datum, label width, column position — because at screen
size everything looks like it fits.

A left-aligned title has the same trap. It is aligned to the axes, not to the
figure, and when long category names push the axes two thirds of the way across,
the title has a third of the width you were looking at. Measure it there.

## Signs of an auto-generated figure

Look for these specifically, and fix what you find:

* default matplotlib colours, or six saturated colours where three would do;
* a legend in the default upper-right corner, sitting over the data;
* a default figure size that matches no column;
* a generic title inside the graphic;
* gridlines competing with the data;
* a crowded or rotated x axis that should have had fewer categories;
* markers chosen arbitrarily rather than by meaning;
* more decimal places than the measurement supports;
* annotations positioned without regard to composition;
* panels with visibly different density or margins;
* an oversized legend, or a box around it;
* explanatory sentences inside the figure;
* a footnote under the axes, which is a caption that lost its way;
* a note saying what is *not* shown, which the caption already says;
* the same axis label written once per panel;
* "n = " before a number that is obviously a count;
* text lying across the curve it describes;
* a label pressed against the panel next door;
* a square panel in a full-width row, with blank page on both sides;
* a full-width row spent on four bars;
* primary and secondary results drawn with identical weight.

## Typography

Sizes come from the style file; what needs judgement is the hierarchy. Axis
labels should read as distinct from tick labels. Panel letters should be
prominent but not shouting. Capitalisation, units, notation and terminology
should match across every panel and every figure of the manuscript. Long
category names deserve a considered break, not a squeeze. Never use small text
to rescue a layout.

## Colour

A colourblind-safe palette is where you start, not where you finish. Assign
colours by semantic role, keep the mapping identical across the manuscript,
prefer moderate saturation, and let neutral tones carry context. When two or
three colours are enough, do not use six.

## Multi-panel figures

A multi-panel figure must read as one designed object, not as several plots
pasted together. Coordinate panel dimensions, margins, typography, colour
semantics, legends, panel labels and density. Shared elements should genuinely
look shared. If one panel is far denser than the others, the layout is wrong,
not the panel.

## Editorial review

This is a distinct pass with its own verdict, run after the technical checks come
back clean. Passing the checks means nothing is broken; it says nothing about
whether the figure was edited. Work through these and answer each one out loud,
naming the change or the reason for declining:

1. **Count the text, in both directions.** List every block of prose in the
   figure and say where each belongs — here, or in the caption. Then go the
   other way: for each panel, ask whether a reader could decode it without the
   caption. Too little text fails as surely as too much, and it fails silently,
   because no rule about excess catches it. Opaque tokens (`A`, `B`, series 1)
   are the usual symptom: they look economical and cost the reader a trip to
   the caption.
2. **Count the repeats.** The same axis label on two panels, the same unit on
   four, a legend entry for something a direct label already says, a title the
   caption repeats. One of each is enough.
3. **Find the dead space.** Which regions carry nothing? Is that deliberate
   breathing room or a band left over by the layout? A figure that ends in a
   loose stack of text rows at the bottom was not composed, it was accumulated.
4. **Check the hierarchy.** Squint at it. What do you see first? Is that the
   result, or is it a legend, a grid, or a block of grey type?
5. **Check the density.** Is any panel doing more work than its neighbours? Is
   any panel an inch across and carrying three lines of type?
6. **Compare it.** Would it look composed beside a figure from a strong
   published paper, or would it look like output that was tidied up?

If any answer is unsatisfactory, fix it and look again.

Refinement is bounded. Each pass must name one specific defect and the specific
change that addresses it. When a pass produces no defect worth naming, stop —
do not keep adjusting values, and do not restart the design.

A caution learned the hard way: tightening a figure's height brings fixed-size
type closer to everything positioned in axis fractions. Brackets, annotations and
value labels that cleared each other at the old height can collide at the new
one. Re-check after every resize, and look at the result rather than assuming the
proportions carried over.

The same applies to changing a range. Widening an axis to share it with another
panel takes away the room a label was using, and the label does not move. If a
pass changes a limit, look at every annotation in that panel before doing
anything else.

If two attempts at a placement both collide, stop moving it. The position is not
the problem; the object is too big for where it is being asked to go. Shorten it,
or give it a region of its own where nothing else can arrive.

## Done

The figure is complete when the message is faithful and the encoding suits it;
the mechanical QC reports zero FAIL; it was rendered at final size and looked
at; typography, colour and composition are coherent; the main result has clear
visual hierarchy; nothing unnecessary remains; it no longer resembles library
defaults; this editorial review has been answered; and the analysis was not
changed along the way.

When output that is technically correct still looks generic, awkward or weak,
keep refining it.
