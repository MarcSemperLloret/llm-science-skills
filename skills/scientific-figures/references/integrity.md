# Scientific integrity, captions and manuscript consistency

## Integrity

Do not alter the visual representation to exaggerate an effect. Specifically:

* do not choose axis limits that amplify a small difference;
* do not hide outliers for aesthetic reasons;
* do not drop unsuccessful models or conditions merely because they clutter;
* do not imply statistical significance without a valid test;
* do not draw error bars whose definition is unstated;
* do not connect unrelated categorical observations with lines;
* do not encode a one-dimensional quantity as area or volume.

If a requested visual choice would materially mislead, say so and propose the
safer representation. Flag it in one or two sentences and carry on with the work.

A visual task must never change the numbers. Keep data preparation, statistical
analysis and figure generation separate, and do not touch the first two while
fixing the third.

Never retouch an exported figure by hand. If the output is wrong, the script is
wrong. Hand edits break regeneration under audit and are lost on the next run.

## Captions

Do not duplicate the manuscript caption inside the graphic. Inside the figure
keep only axes, units, category labels, short annotations, panel labels and the
legend or colorbar.

When you also write the caption, make sure it defines the panels, the encodings,
any abbreviation, what the uncertainty representation means, the sample size
where relevant, and the statistical test where one was used. Do not invent
methodological detail that is not in the analysis.

## Consistency across a manuscript

Treat all figures of one manuscript as a single visual system. Before assigning
a colour or encoding to a recurring variable or model, open the earlier figures
and reuse what is already established.

Keep consistent: font family and sizes, panel-label format, colour semantics for
models and observations, line styles, marker meanings, terminology, units,
spacing and export width.

## Modifying an existing figure

1. find the script or function that generates it;
2. look at the current rendered output;
3. change only what was asked;
4. preserve valid scientific encodings;
5. re-render and re-run QC.

Do not redesign an established figure merely because another design is possible.
Fix adjacent problems only when they materially affect readability or
interpretation.

If the figure predates the toolkit and uses its own style, do not force
`figstyle` onto it — that would break consistency with its siblings. Run
`figcheck.check_figure(fig)` on it anyway and fix what fails.

## Project and journal overrides

Explicit project or journal instructions beat every default here: mandated
dimensions, required fonts, greyscale production, a prescribed raster
resolution, a required file format, or established manuscript colour semantics.
Pass the journal width to `figstyle.figure()` and `save()` and let the checker
verify against it.
