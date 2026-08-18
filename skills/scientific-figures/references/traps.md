# Matplotlib traps that silently ruin a publication figure

Each of these was found in a real manuscript. They pass without an error and are
invisible until the figure is measured or placed on the page.

## `bbox_inches="tight"` destroys the designed width

A tight bbox crops to the drawn content, so the saved file comes back at whatever
width the labels happened to need — 5.13 in here, 5.77 in there, from scripts
that all asked for the same width. LaTeX then rescales each one by a different
factor, and a set of figures designed as one typographic system reaches the page
at five different type sizes.

Set `savefig.bbox` to `standard` and let constrained layout or explicit margins
do the fitting. The exported width then equals `figsize` exactly.

## A colour bar attached to a gridspec axes is placed by the gridspec

`figure.colorbar(mesh, ax=axis)` defaults to `use_gridspec=True`, so the bar
becomes part of the layout. A later `subplots_adjust(right=0.985)` moves it flush
against the canvas edge, and its ticks and label — which live *outside* the bar —
fall off the page.

`use_gridspec=False`, or creating the bar after the margins, does not help: the
bar is still placed inside the panel's cell. The right margin has to be wide
enough to hold the bar plus roughly 27 pt for its ticks and label. Size the
margin for that, or put the bar horizontally under the panel instead.

## A panel letter offset into the margin needs the margin to exist

The usual `annotate(letter, xytext=(-30, 10), textcoords="offset points")` assumes
a panel with a y axis, whose tick labels have already opened 30 pt of margin. A
map has no tick labels and sits flush against the text block, so the letter lands
off the canvas. Make the offset a parameter and pass a shorter arm for panels
with no y axis, or anchor those letters in figure coordinates.

## Tick labels exist for ticks outside the view

Matplotlib keeps the `Text` object for a tick that falls outside the current
limits, and it still reports a window extent. Any geometry check that walks
`fig.findobj(Text)` must filter them out or it will report phantom overlaps far
from anything drawn.

## `plot` with `linestyle="none"` still takes a colour from the cycle

A marker-only `plot` call consumes the property cycle, so a figure with a fully
curated palette can still be carrying `#1f77b4`, `#ff7f0e` and friends on
invisible lines. Harmless to look at, but it makes a default-palette check fire.
Set the colour explicitly if the check's noise matters.

## Text set against the panel edge collides with the neighbour

An annotation at `xy=(0.98, …), ha="right"` sits at the panel's right edge, which
is exactly where the next panel keeps its y tick labels. `= 88%` and `20` end up
a point apart and read as one number. Leave the last few per cent of the panel
free, or move the annotation to the side the data leaves empty.

## Shortening a figure moves fixed-size type into things placed by fraction

Brackets, guide lines and annotations positioned in axis fractions scale with the
panel; text does not. Trim the height and a bracket that cleared a value label by
a comfortable margin will land on it. The same applies to `wspace`: widening the
gap between two columns narrows both, and a colour-bar label that fitted its bar
no longer does. Re-run the checks and look at the figure after every resize.

## Long right-aligned annotations reach the far side of the axes

A two-line note set right-aligned across a narrow panel runs its first line into
the y tick labels on the *left*. Break it into more, shorter lines, or move it —
and check whether it should be in the caption instead.

## A quiver key is invisible to `findobj`

`Axes.quiverkey` keeps its label outside the artist tree, so a sweep over
`fig.findobj(Text)` never sees it. The key can sit on top of a legend or a tick
label and no text check will notice. The same caution applies to anything else
that stores a `Text` privately.

## Removing a label moves whatever was positioned relative to it

A quiver key placed below a panel sits where the x label was. Delete the x label
to save height and the key lands on the row underneath. When you remove an
element, look for what was anchored to the space it occupied.

## A gap in data units is not a gap

`ax.text(value + 0.008, ...)` looks like it leaves a margin beside a marker. It
does not: 0.008 is a distance on the data axis, so when the value is small the
label starts inside the marker, and when the axis is rescaled the gap changes
with it. Anchor the label at the data point and offset it in points:

```python
ax.annotate(label, (x, y), xytext=(9, 0), textcoords="offset points")
```

That keeps the same clearance whatever the limits are.

## Adding a legend does not replace the old one

`ax.legend()` called twice leaves only the last call's legend. Insert a new
legend earlier in the function than the existing call and nothing changes, which
looks like the fix failed. Delete the old call.
