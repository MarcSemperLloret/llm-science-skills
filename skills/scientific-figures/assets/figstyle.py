"""Publication figure toolkit for the scientific-figures skill.

    import sys; sys.path.insert(0, r"<skill>/assets")
    import figstyle as fs

    fig, axes = fs.figure("double", 3.2, ncols=2, sharey=True)
    axes[0].plot(x, y, color=fs.C.blue, label="observed")
    fs.label_panels(axes)
    fs.save(fig, "figures/fig01")           # exports, then reports QC findings

Importing the module applies the publication style. Sizes in the style are
final-size points, so the exported file must be included in the manuscript at
1:1 scale -- never rescaled by \\includegraphics[width=...].
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

from figcheck import check_figure, report

_ASSETS = Path(__file__).resolve().parent
STYLE = _ASSETS / "publication.mplstyle"

#: Standard column widths in inches. Override when the journal specifies others.
WIDTH = {"single": 3.35, "onehalf": 5.5, "double": 7.0}


class C:
    """Okabe-Ito, plus neutrals for contextual material.

    Assign by semantic role and keep the mapping fixed across the manuscript:
    the same quantity must keep the same colour in every figure.
    """

    blue = "#0072B2"
    vermillion = "#D55E00"
    green = "#009E73"
    orange = "#E69F00"
    purple = "#CC79A7"
    sky = "#56B4E9"
    yellow = "#F0E442"
    black = "#000000"

    #: quieter tones for reference series, context and annotation
    grey = "#949494"
    light = "#D9D9D9"
    dark = "#333333"


#: Perceptually uniform maps. Sequential for magnitude, diverging for signed
#: departures from a meaningful reference (centre the norm on it).
SEQUENTIAL = ("viridis", "magma", "cividis", "rocket_r")
DIVERGING = ("RdBu_r", "BrBG", "PuOr", "coolwarm")


def use():
    """(Re)apply the publication style."""
    plt.style.use(STYLE)


use()


def figure(width="double", height=None, **kwargs):
    """Create a constrained-layout figure at a real publication width.

    width   key of WIDTH, or a number of inches
    height  inches; defaults to a sane ratio for the panel grid
    kwargs  passed to plt.subplots (nrows, ncols, sharex, sharey, ...)

    Returns (fig, ax) or (fig, axes) exactly as plt.subplots does.
    """
    w = WIDTH.get(width, width) if isinstance(width, str) else float(width)
    if height is None:
        nrows = kwargs.get("nrows", 1)
        ncols = kwargs.get("ncols", 1)
        height = min(9.0, 0.78 * (w / max(ncols, 1)) * nrows + 0.45)
    fig, axes = plt.subplots(figsize=(w, height), layout="constrained", **kwargs)
    fig._target_width = w
    return fig, axes


def label_panels(axes, labels=None, inside=False, **kwargs):
    """Label panels A, B, C ... in reading order.

    By default the label is set as a left-aligned bold axes title, so
    constrained layout reserves room for it and it can never be clipped.
    Use inside=True for panels with no spare vertical room, such as maps.
    """
    try:
        flat = list(axes.flat)
    except AttributeError:
        flat = list(axes) if isinstance(axes, (list, tuple)) else [axes]
    if labels is None:
        labels = [chr(ord("A") + i) for i in range(len(flat))]
    style = dict(fontsize=10, fontweight="bold")
    style.update(kwargs)
    for ax, lab in zip(flat, labels):
        if inside:
            ax.text(
                0.025, 0.975, lab, transform=ax.transAxes,
                va="top", ha="left", zorder=6,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.5),
                **style,
            )
        else:
            ax.set_title(lab, loc="left", **style)
    return flat


def shared_legend(fig, handles=None, labels=None, loc="outside upper center", **kwargs):
    """One legend for the whole figure, placed outside the panels.

    Prefer direct labelling when it is unambiguous; use this when several
    panels share the same encoding.
    """
    kwargs.setdefault("frameon", False)
    if handles is None:
        handles, labels = fig.axes[0].get_legend_handles_labels()
    kwargs.setdefault("ncols", min(len(handles), 4))
    return fig.legend(handles, labels, loc=loc, **kwargs)


def save(fig, path, formats=("pdf", "png"), check=True, target_width=None, **kwargs):
    """Export the figure and run deterministic quality control.

    Writes one file per format next to `path` (any extension in `path` is
    replaced). Vector output carries no creation timestamp, so a rerun does not
    differ merely because the clock moved.

    Returns the list of QC findings.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs.setdefault("bbox_inches", None)  # constrained layout already fits it
    for ext in formats:
        out = path.with_suffix(f".{ext}")
        opts = dict(kwargs)
        if ext in ("pdf", "eps", "ps"):
            opts["metadata"] = {"CreationDate": None}
        elif ext == "svg":
            opts["metadata"] = {"Date": None}
        fig.savefig(out, **opts)
    if not check:
        return []
    findings = check_figure(fig, target_width=target_width or getattr(fig, "_target_width", None))
    report(findings, f"QC {path.with_suffix('.' + formats[0])}")
    return findings


def context(ax, *artists, alpha=0.9):
    """Push artists into the visual background so the main result dominates."""
    for a in artists:
        a.set_color(C.grey)
        a.set_alpha(alpha)
        a.set_zorder(1)
    return ax


__all__ = [
    "C", "WIDTH", "SEQUENTIAL", "DIVERGING", "STYLE",
    "use", "figure", "label_panels", "shared_legend", "save", "context",
    "mpl", "plt",
]
