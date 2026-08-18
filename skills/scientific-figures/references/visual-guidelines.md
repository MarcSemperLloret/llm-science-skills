# Visual guidelines

Decisions, not options. These are what the style file encodes; they are written
down so that a figure built outside `figstyle` can still be built to the same
system, and so that a reader of the code knows what was chosen on purpose.

A manuscript that has its own style file overrides all of this. Consistency
inside one manuscript beats consistency across a career, and journals impose
their own column widths, classes and sometimes fonts.

## Type

One family per figure, sans-serif by default (Arial, Helvetica, DejaVu Sans),
serif when the manuscript's own style asks for it.

Four sizes, no more, and they mean something:

| role | size | weight |
|---|---|---|
| panel letter | 10 pt | bold |
| axis label | 9 pt | regular |
| tick label, legend, annotation | 8 pt | regular |
| footnote-weight detail | 8 pt | regular, grey |

Never below 7.5 pt at final size. Never a fifth size to make something fit.

No figure title: the caption carries it. A panel letter set as a left title is
the exception, because the layout engine reserves room for it and it can never
be clipped.

## Colour

Okabe–Ito, assigned by role and fixed across the manuscript.

| role | token | hex |
|---|---|---|
| principal series | `C.blue` | `#0072B2` |
| second series / contrast | `C.vermillion` | `#D55E00` |
| third | `C.green` | `#009E73` |
| fourth | `C.orange` | `#E69F00` |
| context, reference, "everything else" | `C.grey` | `#949494` |
| scaffolding: gridlines, faint rules | `C.light` | `#D9D9D9` |
| ink: spines, ticks, text | `C.dark` / black | `#333333` |

Two or three colours carry almost every scientific figure. Six is a sign that
the encoding is doing work the layout should do.

Sequential data: `viridis`, `magma`, `cividis`. Diverging: `RdBu_r`, `BrBG`,
`PuOr`, centred on the reference value. Never a spectral map.

## Line and marker

| element | width |
|---|---|
| principal series | 1.5 pt |
| secondary, reference | 0.9–1.2 pt |
| spines, ticks | 0.7 pt |
| gridlines | 0.5 pt, `C.light` |
| hairline guides, scale bars | 0.6–0.8 pt |

Markers 4 pt, no edge unless they sit on a filled field, in which case white,
0.6 pt.

## Space

Top and right spines off. No gridlines unless the reader must recover values,
and then major only, behind the data.

Standard widths: 3.35 in single column, 5.5 in one and a half, 7.0 in double —
or whatever the manuscript's `\textwidth` measures, which takes precedence.

Height follows content. Above 6.5 in a figure and its caption take most of a
page, which is a lot to spend; above 9 in it does not fit one.

The figure is exported at exactly its designed width and included at 1:1.

## Labelling

Direct labels before a legend. A legend inside the panel before a legend
outside it. A legend outside the panel before an illegible one.

Units on every axis. Decimal places only where the measurement supports them.
The panel letter goes at the top left, bold, as a left-aligned title.

## Language

English, always, in every label, unit, category name, legend entry and
annotation — the language the manuscript is written in and the reviewer reads.
Place and station names keep their own spelling.

## Text

A figure is a picture. Inside the frame: axis labels with units, category names,
a direct label on a series, a value beside a point, the panel letter, the legend
or colorbar. Nothing else.

Sentences belong in the caption. So do definitions of the uncertainty, notes on
what was excluded, and how a quantity was computed. If a line inside a figure
ends in a full stop, it is in the wrong place.

## Export

PDF for the manuscript, PNG at 400 dpi for looking at, TIFF only when the
journal demands it. Fonts embedded as Type 42. Dense fields rasterised inside
the vector file; text and vectors left sharp.

Never retouch an exported figure. Fix the script.
