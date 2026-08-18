# Third-party skills

Four skills in `skills/` are not mine. They are vendored from
[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)
at commit `9e8b0cb0b090` (17 August 2026), unmodified, under the MIT licence:

| skill | why it is here |
|---|---|
| `paper-lookup` | `research-feasibility` requires a literature check before it will issue a GO, and marks novelty UNVERIFIED without one. This is what performs that check: 11 literature APIs, standard library only, no credentials needed. |
| `statistical-power` | The recurring limitation in our own results has been power, not method: one primary prediction rested on 12 candidates and one subgroup on 19. A priori power and minimum detectable effect belong in the design, not the discussion. |
| `statistical-analysis` | Test selection, assumption checking, effect sizes and reporting, for the hypothesis testing every one of our manuscripts does. |
| `geopandas` | Used directly in three of our manuscripts for census sections, station points, boundary polygons and projections. |

They keep their own frontmatter, including their `license:` field.

## Upstream licence

```
MIT License

Copyright (c) 2025 K-Dense Inc.
```

The full text is at
<https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/LICENSE.md>.
Individual skills upstream may declare a different licence in their own
`SKILL.md` metadata; the four vendored here declare MIT.

## Why vendored and not installed alongside

Vendoring pins them: they will not change under us, and one clone of this
repository carries everything. The cost is that upstream fixes do not arrive on
their own. Installing both packages instead — `npx skills add` for each — keeps
them current at the price of a second dependency. Either is defensible; this
repository chose the pinned copy.

To refresh one, replace its directory from upstream and update the commit
recorded above.

## What was deliberately left out

The upstream catalogue holds 163 skills. Most are library wrappers for fields we
do not work in — bioinformatics, cheminformatics, proteomics, lab automation,
quantum computing — and installing them would spend context on every session and
dilute which skill fires.

Two were considered and rejected on merit. `geomaster` covers "30+ scientific
domains and 8 programming languages", which is too broad to trigger reliably and
overlaps `geopandas` where we actually work. Its own `matplotlib` and
`scientific-visualization` skills teach library use, which is not what
`scientific-figures` does; keeping both would put two different answers in front
of the same question.
