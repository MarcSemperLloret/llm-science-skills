# Encodings, axes, colour and legends

Detail behind the choices the toolkit cannot make for you. Read the section you
need; do not read the file end to end.

## Start from the relationship, not from the chart

Pick the form from what you are claiming about the data, not from what the data
looks like. This is the discipline behind the Financial Times *Visual
Vocabulary*: name the relationship first, and the form follows.

| the claim is about | good forms | avoid |
|---|---|---|
| change over time | line, connected scatter, slope chart | bars per time step |
| ranking | ordered dot plot, lollipop, ordered bars | pie, radar |
| magnitude compared | bars from zero, dot plot | area, bubble |
| deviation from a reference | diverging bars, dot plot with a zero rule | plain bars |
| an estimate and its uncertainty | point with interval, gradient interval | bar with error bar |
| distribution | histogram, ECDF, violin, box, strip | mean ± SD alone |
| correlation | scatter, with a fit only if you fitted one | dual axis |
| part of a whole | stacked bar (few parts), waffle | pie beyond three parts |
| spatial pattern | choropleth, dot density, field map | 3-D terrain |
| flow or transition | Sankey, slope chart, arrow map | chord for many nodes |
| two variables jointly | small multiples, bivariate scatter | dual y axis |

Two forms carry most scientific results honestly: the **line** for something
ordered and continuous, and the **point with an interval** for an estimate. When
in doubt, one of those is the answer.

Order categories by value, not alphabetically, unless the order itself is the
message.

## Choosing the figure type

Prefer:

* line plots for continuous ordered evolution;
* scatter plots for relationships between continuous variables;
* points with intervals for estimates and uncertainty;
* boxplots, violin plots, ECDFs or distribution plots for distributions;
* heatmaps for structured matrices;
* maps only when spatial location is scientifically relevant;
* grouped points or bars only when category comparison is genuinely clearer that way;
* small multiples or facets when comparison across groups matters more than overlaying many series.

Avoid by default: 3D plots, pie charts, donut charts, radar charts, stacked bars
beyond two or three levels, decorative gradients, shadows, background fills,
chartjunk, and dual y axes unless there is a compelling scientific reason.

Do not use a bar chart for continuous estimates when a point-and-interval
representation communicates the result more accurately.

## Axes and ticks

* include units in every axis label where applicable;
* use scientifically meaningful tick intervals;
* keep decimal precision to what a reader can act on;
* use consistent number formatting across comparable panels;
* use scientific notation only when it improves readability;
* never truncate a bar-chart quantitative axis in a misleading way;
* for line and scatter plots choose limits from the scientific question rather
  than forcing zero;
* prefer horizontal tick text; rotate only when genuinely needed.

Never shrink tick labels to fit more categories. Reduce the number of ticks
(`MaxNLocator`), change the layout, or redesign the encoding.

When two panels sit side by side, prune the last tick of the left panel or the
first of the right one if their labels come close to touching.

## Lines, markers and uncertainty

The style file sets the defaults; deviate deliberately.

* principal data lines 1.3–1.8 pt, secondary and reference lines 0.8–1.2 pt;
* markers large enough to stay distinguishable at final size;
* distinguish series by more than colour when practical — line style, marker
  shape, or direct labels;
* represent uncertainty explicitly when it exists: confidence or credible
  intervals, interquartile ranges, error bars, uncertainty bands;
* state in the caption what the uncertainty representation means.

Do not invent significance tests, confidence intervals or uncertainty estimates.

## Colour

`figstyle.C` carries the Okabe–Ito palette plus neutrals. The palette is the
starting point, not the design.

* same concept, same colour, in every figure of the manuscript;
* give the principal comparison the strongest colours and push context to
  `C.grey` or `C.light`;
* two or three colours are usually enough; do not spend six;
* avoid distinctions carried by red against green alone;
* check that the important distinction survives in greyscale when practical;
* use `figstyle.SEQUENTIAL` for magnitude and `figstyle.DIVERGING` for signed
  departures, centring the norm on the meaningful reference value
  (`matplotlib.colors.TwoSlopeNorm` or a symmetric `vmin`/`vmax`).

Never use `jet`, `rainbow`, `turbo` or other spectral maps for quantitative
data. The checker fails on them.

## Legends and direct labelling

In order of preference:

1. direct labelling at the end of a line or beside a cluster;
2. a compact legend in genuinely unused space inside the axes;
3. `figstyle.shared_legend(fig)` outside the panels for multi-panel figures.

Avoid legend boxes over data, a repeated legend in every panel, labels that
restate the caption, and more entries than a reader can hold at once.

## Grid and spines

Top and right spines are off in the style. Gridlines are off too; switch them on
only when the reader must recover values, and keep them at `C.light`, 0.5 pt,
behind the data.

## Annotations

Short, spatially separated from the data, consistently styled, connected with a
subtle leader line only when necessary. No paragraphs inside the figure, and no
annotation on every point.

## Multi-panel figures

* panel order follows the intended reading sequence;
* identical quantities keep identical encodings across panels;
* share scales when magnitude comparison is intended, and say so in the caption
  when they differ;
* drop redundant axis labels on shared axes (`sharex`, `sharey`);
* one legend and one colorbar for the whole figure where possible;
* keep information density comparable between panels.

Do not combine unrelated analyses simply to reduce the figure count.
