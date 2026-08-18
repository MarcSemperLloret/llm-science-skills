# Scientific Skills

Agent Skills for producing scientific manuscripts. They encode standards and
procedures, not library tutorials: how a publication figure is built and
verified, how it is judged once it is correct, what goes in the front and end
matter of every paper, and whether a research idea deserves a project at all.

Written and calibrated against real manuscripts. Every mechanical check exists
because a defect reached a compiled PDF.

## Skills

| skill | what it is for |
|---|---|
| [`scientific-figures`](skills/scientific-figures/) | Any figure for a paper, report or thesis. Ships a matplotlib style, a helper module and three command-line checkers: figure QC, tiling for close visual inspection, and a page-level check of figure plus caption against the text block. |
| [`figure-polish`](skills/figure-polish/) | The editorial pass, run after the mechanical checks come back clean. Hierarchy, composition, text budget, and the question of whether anyone actually edited the figure. |
| [`editorial-figures`](skills/editorial-figures/) | A chart that travels without a caption: README, slides, posters, outreach. Its rules on text are the opposite of the manuscript ones, deliberately. |
| [`manuscript-starter`](skills/manuscript-starter/) | Starting a paper or its repository. Front matter and end matter as files to copy, plus the LaTeX and git conventions. |
| [`desk-reject-simulation`](skills/desk-reject-simulation/) | The editor's first screen, before submitting. Mechanical submission checks as a script, then the judgement half: scope, claim, support, honesty of framing. Returns DESK REJECT, BORDERLINE or SEND OUT. |
| [`literature-check`](skills/literature-check/) | What the manuscript claims against what the literature says. Resolves every DOI against the registry, finds citations without entries and entries without citations, and locates every novelty claim so it can be defended. |
| [`research-feasibility`](skills/research-feasibility/) | Deciding whether an idea has enough signal, robustness and novelty to justify a full project: GO, REDIRECT, BRANCH or NO-GO. |

## Install

This repository is an Agent Plugins 1.0.0 package: a root `plugin.json` and
skills under `skills/`. Every immediate child of `skills/` that contains a
`SKILL.md` is a skill.

```bash
npx skills add <owner>/scientific-skills          # Claude Code, Codex, Cursor, Gemini CLI
gh skill install <owner>/scientific-skills        # or, with the GitHub CLI
```

Manual installation, for any host: copy the contents of `skills/` into whichever
directory that host reads.

| host | path |
|---|---|
| Claude Code | `~/.claude/skills/` |
| generic / Open Agent Skills | `~/.agents/skills/`, or `.agents/skills/` in a project |
| Cursor | symlink or copy the repo into `~/.cursor/plugins/local` |
| Codex | `codex plugins install .` from a local checkout |

```bash
git clone <repo> /tmp/scientific-skills
cp -r /tmp/scientific-skills/skills/* ~/.claude/skills/
```

Nothing inside the skills depends on where they end up: paths are resolved
relative to each `SKILL.md`.

## Requirements

The figure toolkit needs Python with `matplotlib` and `numpy`. `figtiles.py`
also needs `pillow`, and `figpage.py` needs `pymupdf`. Everything else is
markdown.

Manuscripts are LaTeX, class `elsarticle`, built with `latexmk`.

## Using them without automatic discovery

Hosts that do not discover skills on their own can still use these: point the
agent at this repository and tell it to read `SKILL.md` for the task at hand.
The table above is enough of an index — each `SKILL.md` opens with a
`description` in its frontmatter saying exactly when it applies.

## Licence

MIT. See [LICENSE](LICENSE).
