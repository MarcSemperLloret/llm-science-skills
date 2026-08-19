"""Deterministic quality control for publication figures.

Catches the mechanical defects so that visual inspection can be spent on
judgement instead of on measuring. Two entry points:

    from figcheck import check_figure
    findings = check_figure(fig, target_width=7.0)

    python figcheck.py fig01.pdf fig01.png              # audit exported files
    python figcheck.py --width 5.40 fig01.pdf           # against a journal width

Severities
    FAIL  objectively wrong; the figure is not publishable as is
    NOTE  needs a human judgement call; may be legitimate

Assumes the figure is placed in the manuscript at 1:1 scale.
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

MIN_FONT_PT = 7.5
COLUMN_WIDTHS_IN = {"single": 3.35, "onehalf": 5.5, "double": 7.0}
MAX_HEIGHT_IN = 9.0

_TAB10 = {
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
}
_BAD_CMAPS = {
    "jet", "rainbow", "gist_rainbow", "hsv", "nipy_spectral",
    "gist_ncar", "flag", "prism", "brg", "turbo",
}
_MANY_DECIMALS = re.compile(r"^-?[\d\s,]*\.\d{4,}$")


class Finding(tuple):
    """(severity, code, message)."""

    __slots__ = ()

    def __new__(cls, severity, code, message):
        return super().__new__(cls, (severity, code, message))

    severity = property(lambda self: self[0])
    code = property(lambda self: self[1])
    message = property(lambda self: self[2])

    def __str__(self):
        return f"{self[0]:<4}  {self[1]:<16}  {self[2]}"


def _hex(color):
    from matplotlib.colors import to_hex

    try:
        return to_hex(color).lower()
    except (ValueError, TypeError):
        return None


def _offscreen_tick_labels(fig):
    """Tick labels for ticks outside the view interval.

    Matplotlib keeps those Text objects alive and they carry a window extent
    even though nothing is drawn, so they must not be measured.
    """
    dead = set()
    for ax in fig.axes:
        # An axes with axis("off") still owns its tick labels, and they still
        # report a window extent, but nothing is drawn. Measuring them invents
        # clipping and overlaps in maps and schematics.
        if not getattr(ax, "axison", True):
            for axis in (ax.xaxis, ax.yaxis):
                for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                    dead.add(id(tick.label1))
                    dead.add(id(tick.label2))
            continue
        for axis, (lo, hi) in (
            (ax.xaxis, sorted(ax.get_xlim())),
            (ax.yaxis, sorted(ax.get_ylim())),
        ):
            span = (hi - lo) or 1.0
            eps = span * 1e-6
            try:
                ticks = list(axis.get_major_ticks()) + list(axis.get_minor_ticks())
            except (ValueError, AttributeError):
                continue
            for tick in ticks:
                if not (lo - eps <= tick.get_loc() <= hi + eps):
                    dead.add(id(tick.label1))
                    dead.add(id(tick.label2))
    return dead


def _visible_texts(fig, dead=None):
    from matplotlib.text import Text

    dead = _offscreen_tick_labels(fig) if dead is None else dead
    out = []
    for t in fig.findobj(Text):
        if not t.get_visible() or not t.get_text().strip() or id(t) in dead:
            continue
        try:
            if t.get_alpha() == 0:
                continue
        except AttributeError:
            pass
        out.append(t)
    # A quiver key keeps its label outside the artist tree, so findobj never
    # reaches it and the label can sit on a legend unnoticed.
    try:
        from matplotlib.quiver import QuiverKey

        for key in fig.findobj(QuiverKey):
            label = getattr(key, "text", None)
            if (label is not None and label.get_visible()
                    and label.get_text().strip() and id(label) not in dead
                    and not any(x is label for x in out)):
                out.append(label)
    except ImportError:
        pass
    return out


def _is_colorbar_axes(ax):
    return getattr(ax, "_colorbar", None) is not None or ax.get_label() == "<colorbar>"


def _titles(ax):
    """Every title artist of an axes, not just the centred one.

    `ax.title` is the centre title alone. A panel letter or a label set with
    loc="left" lives in `_left_title`, and a check that only looks at `ax.title`
    is blind to it.
    """
    out = []
    for name in ("title", "_left_title", "_right_title"):
        artist = getattr(ax, name, None)
        if artist is not None and artist.get_visible() and artist.get_text().strip():
            out.append(artist)
    return out


def _tick_labels(ax):
    """Tick labels actually drawn.

    `ax.axis("off")` leaves every tick label reporting get_visible() as True, so
    a check that trusts it believes a schematic has a scale.
    """
    if not getattr(ax, "axison", True):
        return []
    return [t for t in (*ax.get_xticklabels(), *ax.get_yticklabels())
            if t.get_visible() and t.get_text().strip()]


def _densify(pts, spacing=2.0):
    """Resample a polyline at roughly `spacing` pixels along its own length.

    A fixed number of samples per segment is not enough: a long riser crossing a
    label leaves only one or two samples inside it, and the crossing is missed.
    Runs separated by non-finite points are resampled independently, so a masked
    gap does not become a straight line through the middle of the plot.
    """
    import numpy as np

    out = []
    good = np.isfinite(pts).all(axis=1)
    for start, stop in _runs(good):
        run = pts[start:stop]
        if len(run) < 2:
            out.append(run)
            continue
        step = np.hypot(*np.diff(run, axis=0).T)
        total = float(step.sum())
        if total <= 0:
            out.append(run)
            continue
        n = int(min(max(total / spacing, len(run)), 20000))
        distance = np.concatenate([[0.0], np.cumsum(step)])
        sample = np.linspace(0.0, total, n)
        out.append(np.column_stack([
            np.interp(sample, distance, run[:, 0]),
            np.interp(sample, distance, run[:, 1]),
        ]))
    return out


def _runs(mask):
    """Start and stop indices of each run of True in a boolean array."""
    start = None
    for i, value in enumerate(mask):
        if value and start is None:
            start = i
        elif not value and start is not None:
            yield start, i
            start = None
    if start is not None:
        yield start, len(mask)


def _data_points(ax):
    """Display-space points along the drawn data of one axes.

    Lines are densified so a long segment between two vertices still registers.
    Filled fields and images are left out: text over a map is often deliberate
    and is the author's call, whereas text over a curve rarely is.
    """
    import numpy as np
    from matplotlib.collections import LineCollection, PathCollection

    chunks = []
    for line in ax.lines:
        # Only true data. axhline, axvline and the like are drawn in a blended
        # transform; they are reference rules, and a label crossing a hairline
        # rule is normal practice.
        if not line.get_visible() or line.get_transform() is not ax.transData:
            continue
        # get_path, not get_xydata: the path carries the drawstyle, so a step
        # plot is measured where it is actually drawn rather than along the
        # diagonal chords between its vertices.
        pts = line.get_transform().transform(line.get_path().vertices)
        chunks.extend(_densify(pts))
    for coll in ax.collections:
        if not coll.get_visible():
            continue
        if isinstance(coll, LineCollection):
            for seg in coll.get_segments():
                chunks.extend(_densify(coll.get_transform().transform(seg)))
        elif isinstance(coll, PathCollection):
            offsets = coll.get_offsets()
            if len(offsets):
                chunks.append(coll.get_offset_transform().transform(offsets))
    if not chunks:
        return None
    points = np.vstack(chunks)
    return points[np.isfinite(points).all(axis=1)]


def _text_on_data(fig, renderer, dpi):
    """Annotations and titles sitting on top of the data they annotate.

    Text given an explicit bbox is skipped: backing a label is how an author
    says the occlusion is intended.
    """
    findings = []
    for n, ax in enumerate(fig.axes):
        if _is_colorbar_axes(ax):
            continue
        points = _data_points(ax)
        if points is None or not len(points):
            continue
        candidates = [t for t in ax.texts if t.get_visible() and t.get_text().strip()]
        candidates.extend(_titles(ax))
        for text in candidates:
            if text.get_bbox_patch() is not None:
                continue
            # Short labels are allowed to touch the data: direct labelling and a
            # value beside its point are good practice, and both put a word next
            # to a line on purpose. What must not sit on the data is a block of
            # text, which is the thing a reader has to stop and parse.
            if len(" ".join(text.get_text().split())) <= 15:
                continue
            try:
                bb = text.get_window_extent(renderer)
            except (RuntimeError, ValueError):
                continue
            # Inset by a point, so a label merely resting against a curve does
            # not count as sitting on it.
            pad = dpi / 72.0
            inside = (
                (points[:, 0] >= bb.x0 + pad) & (points[:, 0] <= bb.x1 - pad)
                & (points[:, 1] >= bb.y0 + pad) & (points[:, 1] <= bb.y1 - pad)
            )
            if int(inside.sum()) >= 3:
                findings.append(Finding(
                    "NOTE", "text-on-data",
                    f"axes {n}: {text.get_text()[:40]!r} lies over the data; move it to "
                    "empty space, back it with a bbox, or send it to the caption",
                ))
    return findings


def _covering_data(fig, renderer, dpi):
    """Legends and backed labels sitting on top of the data.

    A white box behind a label hides the data rather than clearing it, and a
    legend dropped in the default corner lands on the series it names. Both are
    the commonest way a figure stops looking edited.
    """
    findings = []
    for n, ax in enumerate(fig.axes):
        if _is_colorbar_axes(ax):
            continue
        points = _data_points(ax)
        field = [im for im in ax.images if im.get_visible()]
        field += [c for c in ax.collections
                  if c.get_visible() and type(c).__name__ == "QuadMesh"]
        # Filled only: an unfilled circle is an outline whose bounding box is
        # mostly empty middle. Rectangles are bars, which are the data itself;
        # polygons are shaded bands and other background, which a label may
        # legitimately sit on.
        filled = [q for q in ax.patches
                  if q.get_visible() and getattr(q, "get_fill", lambda: True)()]
        bars = [q for q in filled if type(q).__name__ == "Rectangle"]
        field += [q for q in filled if type(q).__name__ != "Rectangle"]

        def hides(bb, pad):
            for bar in bars:
                try:
                    rb = bar.get_window_extent(renderer)
                except (RuntimeError, ValueError, TypeError):
                    continue
                if (min(bb.x1, rb.x1) - max(bb.x0, rb.x0) > pad
                        and min(bb.y1, rb.y1) - max(bb.y0, rb.y0) > pad):
                    return "the plotted data"
            if points is not None and len(points):
                inside = (
                    (points[:, 0] >= bb.x0 + pad) & (points[:, 0] <= bb.x1 - pad)
                    & (points[:, 1] >= bb.y0 + pad) & (points[:, 1] <= bb.y1 - pad)
                )
                if int(inside.sum()) >= 3:
                    return "the plotted data"
            for artist in field:
                try:
                    fb = artist.get_window_extent(renderer)
                except (RuntimeError, ValueError, TypeError):
                    continue
                if (min(bb.x1, fb.x1) - max(bb.x0, fb.x0) > pad
                        and min(bb.y1, fb.y1) - max(bb.y0, fb.y0) > pad):
                    return "the field beneath it"
            return None

        legend = ax.get_legend()
        if legend is not None and legend.get_visible():
            try:
                bb = legend.get_window_extent(renderer)
            except (RuntimeError, ValueError):
                bb = None
            if bb is not None:
                what = hides(bb, dpi / 72.0)
                if what:
                    # Over the plotted series this is not a judgement call: the
                    # legend is hiding the result. Over a filled field it can be
                    # deliberate, so that stays a NOTE.
                    findings.append(Finding(
                        "FAIL" if what == "the plotted data" else "NOTE",
                        "legend-over-data",
                        f"axes {n}: the legend covers {what}; move it outside the "
                        "panel, or label the series directly and delete it",
                    ))
        for text in ax.texts:
            if not text.get_visible() or text.get_bbox_patch() is None:
                continue
            if len(" ".join(text.get_text().split())) <= 8:
                continue
            try:
                bb = text.get_window_extent(renderer)
            except (RuntimeError, ValueError):
                continue
            what = hides(bb, dpi / 72.0)
            if what:
                findings.append(Finding(
                    "NOTE", "label-over-data",
                    f"axes {n}: {text.get_text()[:34]!r} is backed with a box that "
                    f"hides {what}; a box does not clear the data, it covers it",
                ))
    return findings


def _unclipped_data(fig, renderer):
    """Data drawn outside its own axes, landing on the tick labels.

    `clip_on=False` is how a rug, a bracket or a marker gets drawn in the margin,
    and the margin is where the tick labels live. Nothing else catches this pair:
    the tick labels are not annotations, and the marks are not text.
    """
    findings = []
    for n, ax in enumerate(fig.axes):
        if _is_colorbar_axes(ax):
            continue
        loose = []
        for artist in (*ax.lines, *ax.collections):
            if not artist.get_visible() or artist.get_clip_on():
                continue
            try:
                bb = artist.get_window_extent(renderer)
            except (RuntimeError, ValueError, TypeError):
                continue
            if bb.width > 0 and bb.height > 0:
                loose.append(bb)
        if not loose:
            continue
        hit = None
        for label in _tick_labels(ax):
            try:
                lb = label.get_window_extent(renderer)
            except (RuntimeError, ValueError):
                continue
            for bb in loose:
                if (min(lb.x1, bb.x1) - max(lb.x0, bb.x0) > 1.0
                        and min(lb.y1, bb.y1) - max(lb.y0, bb.y0) > 1.0):
                    hit = label.get_text()
                    break
            if hit:
                break
        if hit:
            findings.append(Finding(
                "FAIL", "data-outside-axes",
                f"axes {n}: something drawn with clip_on=False lands on the tick "
                f"label {hit!r}; keep it inside the axes, or move the marks clear "
                "of the labels",
            ))
    return findings


def _panel_size(fig, renderer):
    """Panels too small for what has been put in them."""
    findings = []
    width_in, height_in = fig.get_size_inches()
    for n, ax in enumerate(fig.axes):
        if _is_colorbar_axes(ax):
            continue
        box = ax.get_position()
        w, h = box.width * width_in, box.height * height_in
        blocks = [t for t in ax.texts
                  if t.get_visible() and len(t.get_text().strip()) > 8]
        if blocks and (w < 1.5 or h < 1.2):
            findings.append(Finding(
                "NOTE", "panel-too-small",
                f"axes {n} is {w:.2f} x {h:.2f} in and carries {len(blocks)} block(s) "
                "of text; either the text goes to the caption or the figure should "
                "be split so the panel can breathe",
            ))
    return findings


def _text_load(fig):
    """Prose the graphic is carrying that the caption should carry instead.

    A figure is a picture. Anything a reader has to *read* competes with what
    they came to see, and almost all of it belongs under the figure, where there
    is room to say it properly.
    """
    findings = []
    blocks = [(n, t) for n, ax in enumerate(fig.axes) for t in ax.texts
              if t.get_visible() and t.get_text().strip()]
    blocks += [(None, t) for t in fig.texts if t.get_visible() and t.get_text().strip()]
    for n, ax in enumerate(fig.axes):
        blocks.extend((n, t) for t in _titles(ax))
    for n, text in blocks:
        body = " ".join(text.get_text().split())
        where = "figure" if n is None else f"axes {n}"
        # A full stop is the tell. Labels, values and units do not end in one;
        # sentences do, and a sentence in a figure is a caption in the wrong
        # place. Length alone misses the short ones.
        sentence = body.endswith(".") and len(body.split()) >= 3
        if sentence or len(body) > 90:
            findings.append(Finding(
                "NOTE", "prose",
                f"{where}: {body[:60]!r} reads as a sentence, not a label; check "
                "whether the caption already says it and delete it here if so",
            ))
    per_axes = {}
    for n, text in blocks:
        per_axes[n] = per_axes.get(n, 0) + len(" ".join(text.get_text().split()))
    for n, total in sorted(per_axes.items(), key=lambda kv: -kv[1]):
        if total > 220 and n is not None:
            findings.append(Finding(
                "NOTE", "text-load",
                f"axes {n} carries {total} characters of annotation; cut it back to "
                "what the reader cannot get from the axes and the caption",
            ))
    # A "block" is prose, not a label. Counting any text would count the value
    # beside each point, which is direct labelling and exactly what a figure
    # should do; three alphabetic words is the line between the two.
    def is_block(text):
        words = [w for w in text.get_text().split() if sum(c.isalpha() for c in w) >= 2]
        return text.get_visible() and len(words) >= 3

    heavy = [n for n, ax in enumerate(fig.axes)
             if len([t for t in ax.texts if is_block(t)]) > 2]
    for n in heavy:
        findings.append(Finding(
            "NOTE", "text-load",
            f"axes {n} carries three or more separate blocks of text; a panel "
            "that needs that many is doing more than one job",
        ))
    return findings


def _ink_bbox(ax, renderer):
    """Bounding box of everything actually drawn inside one axes.

    The axes background patch is skipped: it covers the whole panel by
    definition and would make every panel look full.
    """
    from matplotlib.transforms import Bbox

    boxes = []
    # Lines and collections go through _data_points: Collection.get_window_extent
    # does not report the drawn extent of a scatter, and trusting it made whole
    # panels look empty.
    points = _data_points(ax)
    if points is not None and len(points):
        boxes.append(Bbox([[points[:, 0].min(), points[:, 1].min()],
                           [points[:, 0].max(), points[:, 1].max()]]))
    for artist in (*ax.images, *ax.texts, *ax.patches):
        if not getattr(artist, "get_visible", lambda: False)():
            continue
        try:
            bb = artist.get_window_extent(renderer)
        except (RuntimeError, ValueError, AttributeError, TypeError):
            continue
        if bb.width > 0 and bb.height > 0:
            boxes.append(bb)
    if ax.get_legend() is not None:
        try:
            boxes.append(ax.get_legend().get_window_extent(renderer))
        except (RuntimeError, ValueError):
            pass
    return Bbox.union(boxes) if boxes else None


def _shares(ax, which):
    try:
        return len(ax._shared_axes[which].get_siblings(ax)) > 1
    except (AttributeError, KeyError):
        return False


def _composition(fig, renderer):
    """Countable properties of a composed figure.

    None of this judges beauty. It catches the things that make a figure look
    unedited and that a number can settle: a band of empty panel, a canvas whose
    content sits off to one side, panels in a row that do not line up, and type
    or colour used in more variants than a reader can track.
    """
    findings = []
    inks = []
    for n, ax in enumerate(fig.axes):
        if _is_colorbar_axes(ax):
            continue
        ink = _ink_bbox(ax, renderer)
        if ink is None:
            continue
        inks.append(ink)
        box = ax.get_window_extent(renderer)
        if box.height <= 0:
            continue
        # A shared scale is allowed its empty half: that is the price of making
        # two panels comparable, and it is paid on purpose. So is an axis set
        # symmetric about zero, where the empty side is the point.
        low, high = ax.get_ylim()
        symmetric = abs(low + high) < 0.02 * max(abs(low), abs(high), 1e-12)
        if _shares(ax, "y") or ax.get_aspect() != "auto" or symmetric:
            continue
        for side, gap in (("top", box.y1 - ink.y1), ("bottom", ink.y0 - box.y0)):
            if gap / box.height > 0.22:
                findings.append(Finding(
                    "NOTE", "dead-space",
                    f"axes {n}: the {side} {gap / box.height:.0%} of the panel holds "
                    "neither data nor annotation; tighten the limits or use the room",
                ))

    # Matplotlib already knows the extent of everything it drew, colour bars,
    # tick labels and spines included. Rebuilding it by hand misses exactly
    # those and reports empty canvas that is not empty.
    try:
        ink = fig.get_tightbbox(renderer)
    except (RuntimeError, ValueError, TypeError):
        ink = None
    if ink is not None:
        fb = fig.bbox
        ink = ink.transformed(fig.dpi_scale_trans)
        margins = {
            "left": (ink.x0 - fb.x0) / fb.width,
            "right": (fb.x1 - ink.x1) / fb.width,
            "bottom": (ink.y0 - fb.y0) / fb.height,
            "top": (fb.y1 - ink.y1) / fb.height,
        }
        for side, margin in margins.items():
            if margin > 0.08:
                findings.append(Finding(
                    "NOTE", "canvas-margin",
                    f"{margin:.0%} of the canvas is empty on the {side}; the figure "
                    "does not fill the space it reserves on the page",
                ))

    # Panels meant to read as a row should line up. Fixed-aspect panels are
    # exempt: their geometry is set by the projection, not by the layout.
    rows = {}
    for n, ax in enumerate(fig.axes):
        if _is_colorbar_axes(ax) or ax.get_aspect() != "auto":
            continue
        box = ax.get_position()
        rows.setdefault(round(box.y0, 3), []).append((n, box))
    for _, members in rows.items():
        if len(members) < 2:
            continue
        heights = [b.height for _, b in members]
        if max(heights) - min(heights) > 0.004:
            names = ", ".join(str(n) for n, _ in members)
            findings.append(Finding(
                "NOTE", "panel-alignment",
                f"axes {names} sit in one row but differ in height; a row that does "
                "not line up reads as panels pasted together",
            ))

    sizes = {round(t.get_fontsize(), 1) for t in _visible_texts(fig)}
    if len(sizes) > 4:
        findings.append(Finding(
            "NOTE", "type-scale",
            f"{len(sizes)} different type sizes ({sorted(sizes)}); a figure needs "
            "three or four, and more reads as accident rather than hierarchy",
        ))

    used = set()
    for ax in fig.axes:
        if _is_colorbar_axes(ax):
            continue
        for artist in (*ax.lines, *ax.collections, *ax.patches):
            if not artist.get_visible():
                continue
            # A colormapped artist is one decision, not one colour per cell.
            if getattr(artist, "get_array", lambda: None)() is not None:
                used.add(f"cmap:{getattr(artist.get_cmap(), 'name', 'unknown')}")
                continue
            for getter in ("get_color", "get_facecolor", "get_edgecolor"):
                value = getattr(artist, getter, None)
                if value is None:
                    continue
                try:
                    raw = value()
                except (TypeError, ValueError):
                    continue
                for entry in (raw if hasattr(raw, "__len__") and not isinstance(raw, str)
                              and len(raw) and hasattr(raw[0], "__len__") else [raw]):
                    hexed = _hex(entry)
                    if hexed and hexed not in ("#ffffff", "#000000"):
                        used.add(hexed)
    if len(used) > 7:
        findings.append(Finding(
            "NOTE", "colour-count",
            f"{len(used)} distinct colours are drawn; unless every one carries a "
            "meaning the reader must hold, the figure is spending colour it does "
            "not need",
        ))
    return findings


def _decodable(fig):
    """Panels a reader cannot decode, because nothing on them says what they are.

    The rule "keep the text minimal" has a floor. A panel with data but no scale,
    no label, no legend and no annotation satisfies every text budget and
    communicates nothing on its own. Minimum sufficient is the target; minimum is
    not.

    A schematic whose caption names every element is the legitimate exception,
    which is why this is a NOTE.
    """
    findings = []
    for n, ax in enumerate(fig.axes):
        if _is_colorbar_axes(ax):
            continue
        points = _data_points(ax)
        drawn = (points is not None and len(points)) or ax.images or ax.patches
        if not drawn:
            continue
        ticks = _tick_labels(ax)
        labelled = bool(ax.get_xlabel().strip() or ax.get_ylabel().strip())
        annotated = any(t.get_visible() and len(t.get_text().strip()) > 1
                        for t in ax.texts)
        titled = any(len(t.get_text().strip()) > 2 for t in _titles(ax))
        if not (ticks or labelled or annotated or titled or ax.get_legend()):
            findings.append(Finding(
                "NOTE", "undecodable",
                f"axes {n} draws data but carries no scale, no axis label, no "
                "legend and no annotation; a reader cannot tell what it shows. "
                "Minimal text is the goal, but the minimum is not zero — check "
                "the caption names every element, or add the one label needed",
            ))
    return findings


# Function words that mark a Spanish or Catalan phrase. Matching needs two of
# them, so a proper noun keeps its own language: "Camins al Grau" is a place,
# "media por año" is a label that was never translated.
_NOT_ENGLISH = {
    "de", "del", "la", "el", "los", "las", "una", "un", "y", "en", "con", "por",
    "para", "segun", "según", "sobre", "entre", "cada", "que", "es", "son",
    "ano", "año", "años", "mes", "meses", "dia", "día", "días", "hora", "horas",
    "media", "número", "numero", "altura", "sombra", "árbol", "arbol", "red",
    "datos", "temperatura", "estación", "estacion", "estaciones", "ciudad",
    "i", "amb", "les", "dels", "què",
}


def _language(fig):
    """Labels left in the working language.

    The manuscript is in English and the figure is read with it. A label that
    was never translated is invisible to the author, who reads both.
    """
    findings = []
    for text in _visible_texts(fig):
        words = [w.strip(".,;:()[]%").lower() for w in text.get_text().split()]
        hits = sorted({w for w in words if w in _NOT_ENGLISH})
        if len(hits) >= 2:
            findings.append(Finding(
                "NOTE", "language",
                f"{text.get_text()[:44]!r} reads as Spanish or Catalan "
                f"({', '.join(hits[:3])}); figures go to the journal in English",
            ))
    return findings


def _crowded_ticks(fig, renderer, dpi):
    """Tick labels of one axis that touch each other.

    They do not overlap, so the overlap test passes, and they are on the same
    axes, so the cross-panel proximity test skips them. A run of years or
    categories set shoulder to shoulder reads as one string.
    """
    findings = []
    gap = 2.0 / 72.0 * dpi
    for n, ax in enumerate(fig.axes):
        if _is_colorbar_axes(ax):
            continue
        for which, labels in (("x", ax.get_xticklabels()), ("y", ax.get_yticklabels())):
            drawn = [t for t in labels if t in _tick_labels(ax)]
            boxes = []
            for t in drawn:
                try:
                    boxes.append((t, t.get_window_extent(renderer)))
                except (RuntimeError, ValueError):
                    pass
            boxes.sort(key=lambda b: b[1].x0 if which == "x" else b[1].y0)
            for (t1, b1), (t2, b2) in zip(boxes, boxes[1:]):
                clear = (b2.x0 - b1.x1) if which == "x" else (b2.y0 - b1.y1)
                if clear < gap:
                    findings.append(Finding(
                        "NOTE", "crowded-ticks",
                        f"axes {n}: {which} tick labels {t1.get_text()!r} and "
                        f"{t2.get_text()!r} are {max(clear, 0) / dpi * 72:.1f} pt "
                        "apart; thin the ticks, rotate them, or widen the panel",
                    ))
                    break
    return findings


def _wasted_width(fig):
    """Panels that leave most of the width they were given blank.

    A fixed aspect ratio makes an axes as small as its shorter side allows, so a
    square panel in a full-width row is drawn narrow and centred, with a band of
    empty page on each side. The figure paid for the width and did not use it.
    """
    findings = []
    for n, ax in enumerate(fig.axes):
        if _is_colorbar_axes(ax):
            continue
        spec = getattr(ax, "get_subplotspec", lambda: None)()
        if spec is None:
            continue
        try:
            cell = spec.get_position(fig)
        except (AttributeError, ValueError):
            continue
        drawn = ax.get_position()
        if cell.width < 0.45 or drawn.width <= 0:
            continue
        share = drawn.width / cell.width
        if share < 0.78:
            findings.append(Finding(
                "NOTE", "wasted-width",
                f"axes {n} is drawn at {share:.0%} of the width it was given; a "
                "fixed aspect leaves the rest of the row blank. Put the panel "
                "beside another one, or give the row only the width it uses",
            ))
    return findings


def _repeated_labels(fig):
    """The same axis label written on several panels.

    Panels that share a quantity should share one label. Repeating it says it
    twice and spends margin that the panels could have used.
    """
    findings = []
    for which, getter in (("y", "get_ylabel"), ("x", "get_xlabel")):
        seen = {}
        for n, ax in enumerate(fig.axes):
            if _is_colorbar_axes(ax):
                continue
            label = getattr(ax, getter)().strip()
            if label:
                seen.setdefault(label, []).append(n)
        for label, where in seen.items():
            if len(where) > 1:
                findings.append(Finding(
                    "NOTE", "repeated-label",
                    f"{which} label {label!r} is written on {len(where)} panels; "
                    "use one shared label (supylabel/supxlabel) instead",
                ))
    return findings


def check_figure(fig, target_width=None, min_font_pt=MIN_FONT_PT, max_overlaps=6):
    """Return a list of Finding for a live matplotlib Figure."""
    findings = []
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    dpi = fig.dpi
    w_in, h_in = fig.get_size_inches()

    # --- geometry -----------------------------------------------------------
    if target_width is not None:
        if abs(w_in - target_width) > 0.02:
            findings.append(Finding(
                "FAIL", "width",
                f"figure is {w_in:.2f} in wide, target is {target_width:.2f} in; "
                "text sizes are only valid at the designed width",
            ))
    else:
        near = [n for n, v in COLUMN_WIDTHS_IN.items() if abs(w_in - v) <= 0.05]
        if not near:
            opts = ", ".join(f"{n} {v} in" for n, v in COLUMN_WIDTHS_IN.items())
            findings.append(Finding(
                "NOTE", "width",
                f"figure is {w_in:.2f} in wide, which matches no standard column ({opts})",
            ))
    if h_in > MAX_HEIGHT_IN:
        findings.append(Finding(
            "FAIL", "height",
            f"figure is {h_in:.2f} in tall, beyond the usable height of a journal page",
        ))
    elif h_in > 6.5:
        findings.append(Finding(
            "NOTE", "height",
            f"figure is {h_in:.2f} in tall; with its caption it will take most of a "
            "page, which is a lot to spend on one figure. Check that it earns it or "
            "split it in two",
        ))
    if h_in > 1.45 * w_in:
        findings.append(Finding(
            "NOTE", "aspect",
            f"figure is {h_in / w_in:.2f} times taller than wide; a column of panels "
            "that tall usually reads better split",
        ))

    # --- typography ---------------------------------------------------------
    dead = _offscreen_tick_labels(fig)
    texts = _visible_texts(fig, dead)
    tiny = sorted(
        {(round(t.get_fontsize(), 2), t.get_text()[:40]) for t in texts
         if t.get_fontsize() < min_font_pt}
    )
    for size, sample in tiny[:6]:
        findings.append(Finding(
            "FAIL", "tiny-text",
            f"{size:g} pt text below the {min_font_pt:g} pt floor: {sample!r}",
        ))
    if len(tiny) > 6:
        findings.append(Finding(
            "FAIL", "tiny-text", f"...and {len(tiny) - 6} further text objects below the floor"
        ))

    families = {tuple(t.get_fontfamily()) for t in texts}
    if len(families) > 1:
        findings.append(Finding(
            "NOTE", "font-family",
            f"{len(families)} different font families in one figure: {sorted(families)}",
        ))

    # --- clipping and overlap ----------------------------------------------
    fb = fig.bbox
    boxes = []
    for t in texts:
        try:
            bb = t.get_window_extent(renderer)
        except (RuntimeError, ValueError):
            continue
        if bb.width <= 0 or bb.height <= 0:
            continue
        boxes.append((t, bb))
        edges = (
            ("left", fb.x0 - bb.x0),
            ("right", bb.x1 - fb.x1),
            ("bottom", fb.y0 - bb.y0),
            ("top", bb.y1 - fb.y1),
        )
        side, over = max(edges, key=lambda e: e[1])
        if over > 0.5:
            findings.append(Finding(
                "FAIL", "clipped",
                f"text runs {over / dpi * 72:.1f} pt past the {side} edge: "
                f"{t.get_text()[:40]!r}",
            ))

    gap_px = 2.5 / 72.0 * dpi
    overlaps, crowded = [], []
    for i in range(len(boxes)):
        ti, bi = boxes[i]
        for j in range(i + 1, len(boxes)):
            tj, bj = boxes[j]
            dx = min(bi.x1, bj.x1) - max(bi.x0, bj.x0)
            dy = min(bi.y1, bj.y1) - max(bi.y0, bj.y0)
            if dx > 1.5 and dy > 1.5:
                overlaps.append((dx * dy, ti.get_text()[:24], tj.get_text()[:24]))
            elif (
                dy > 1.5 and -gap_px < dx <= 1.5
                and ti.axes is not tj.axes
                and ti.axes is not None and tj.axes is not None
            ):
                # Two labels from different panels, not overlapping but close
                # enough that the eye reads them as one string.
                crowded.append((-dx, ti.get_text()[:24], tj.get_text()[:24]))
    overlaps.sort(reverse=True)
    for _, a, b in overlaps[:max_overlaps]:
        findings.append(Finding("FAIL", "text-overlap", f"{a!r} overlaps {b!r}"))
    if len(overlaps) > max_overlaps:
        findings.append(Finding(
            "FAIL", "text-overlap", f"...and {len(overlaps) - max_overlaps} further overlapping pairs"
        ))
    crowded.sort()
    for _, a, b in crowded[:max_overlaps]:
        findings.append(Finding(
            "NOTE", "text-crowding",
            f"{a!r} and {b!r} are from different panels and nearly touch; "
            "they will read as one label",
        ))

    findings.extend(_text_on_data(fig, renderer, dpi))
    findings.extend(_text_load(fig))
    findings.extend(_covering_data(fig, renderer, dpi))
    findings.extend(_unclipped_data(fig, renderer))
    findings.extend(_panel_size(fig, renderer))
    findings.extend(_repeated_labels(fig))
    findings.extend(_decodable(fig))
    findings.extend(_language(fig))
    findings.extend(_crowded_ticks(fig, renderer, dpi))
    findings.extend(_wasted_width(fig))
    findings.extend(_composition(fig, renderer))

    # --- colour -------------------------------------------------------------
    defaults = set()
    for obj in fig.findobj():
        getter = getattr(obj, "get_color", None)
        if getter is None:
            continue
        try:
            c = _hex(getter())
        except (TypeError, ValueError):
            continue
        if c in _TAB10:
            defaults.add(c)
    if defaults:
        findings.append(Finding(
            "NOTE", "default-colors",
            f"matplotlib default palette in use ({', '.join(sorted(defaults))}); "
            "assign colours by semantic role instead",
        ))

    bad = set()
    for obj in fig.findobj():
        cmap = getattr(obj, "get_cmap", None)
        if cmap is None:
            continue
        try:
            name = cmap().name
        except (TypeError, AttributeError):
            continue
        if name in _BAD_CMAPS:
            bad.add(name)
    for name in sorted(bad):
        findings.append(Finding(
            "FAIL", "colormap",
            f"{name!r} is not perceptually uniform; use viridis/magma/cividis "
            "or a diverging map centred on the reference value",
        ))

    # --- axes ---------------------------------------------------------------
    data_axes = [ax for ax in fig.axes if not _is_colorbar_axes(ax)]
    for n, ax in enumerate(data_axes):
        for which, label, ticks in (
            ("x", ax.get_xlabel(), ax.get_xticklabels()),
            ("y", ax.get_ylabel(), ax.get_yticklabels()),
        ):
            shown = [t for t in ticks
                     if t.get_visible() and t.get_text().strip() and id(t) not in dead]
            if shown and not label.strip():
                findings.append(Finding(
                    "NOTE", "axis-label",
                    f"axes {n}: {which} axis has tick labels but no axis label "
                    "(fine only if a shared label or the category names cover it)",
                ))
            for t in shown:
                if _MANY_DECIMALS.match(t.get_text().strip()):
                    findings.append(Finding(
                        "NOTE", "precision",
                        f"axes {n}: {which} tick label {t.get_text()!r} carries more "
                        "precision than a reader can use",
                    ))
                    break
        title = ax.get_title(loc="left") or ax.get_title(loc="center")
        if len(title) > 60:
            findings.append(Finding(
                "NOTE", "title",
                f"axes {n}: {len(title)}-character title; the manuscript caption "
                "should carry this text, not the graphic",
            ))
        if ax.xaxis.get_gridlines() or ax.yaxis.get_gridlines():
            heavy = [g for g in ax.xaxis.get_gridlines() + ax.yaxis.get_gridlines()
                     if g.get_visible() and g.get_linewidth() > 0.8]
            if heavy:
                findings.append(Finding(
                    "NOTE", "grid",
                    f"axes {n}: gridlines at {heavy[0].get_linewidth():g} pt compete with the data",
                ))
        leg = ax.get_legend()
        if leg is not None and len(leg.get_texts()) > 6:
            findings.append(Finding(
                "NOTE", "legend",
                f"axes {n}: {len(leg.get_texts())} legend entries; consider direct labelling",
            ))

    sup = getattr(fig, "_suptitle", None)
    if sup is not None and sup.get_visible() and len(sup.get_text()) > 60:
        findings.append(Finding(
            "NOTE", "title",
            "long suptitle; the manuscript caption should carry this text",
        ))

    return findings


# --------------------------------------------------------------------------
# exported-file audit
# --------------------------------------------------------------------------

def check_pdf(path, target_width=None):
    path = Path(path)
    findings = []
    data = path.read_bytes()
    if b"/Subtype /Type3" in data or b"/Subtype/Type3" in data:
        findings.append(Finding(
            "FAIL", "type3-font",
            f"{path.name} embeds Type 3 fonts, which many journals reject; "
            "set pdf.fonttype to 42",
        ))
    m = re.search(rb"/MediaBox\s*\[\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)", data)
    if m:
        x0, y0, x1, y1 = (float(v) for v in m.groups())
        w_in, h_in = (x1 - x0) / 72.0, (y1 - y0) / 72.0
        findings.append(Finding("INFO", "size", f"{path.name}: {w_in:.2f} x {h_in:.2f} in"))
        if target_width is not None:
            if abs(w_in - target_width) > 0.02:
                findings.append(Finding(
                    "FAIL", "width",
                    f"{path.name} is {w_in:.2f} in wide, target is {target_width:.2f} in; "
                    "LaTeX will rescale it and the type sizes with it",
                ))
        elif not [n for n, v in COLUMN_WIDTHS_IN.items() if abs(w_in - v) <= 0.05]:
            findings.append(Finding(
                "NOTE", "width",
                f"{path.name} is {w_in:.2f} in wide, matching no standard column width; "
                "pass --width if the journal specifies another",
            ))
    return findings


def check_png(path):
    path = Path(path)
    findings = []
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return [Finding("FAIL", "format", f"{path.name} is not a PNG")]
    w, h = struct.unpack(">II", data[16:24])
    dpi = None
    idx = data.find(b"pHYs")
    if idx > 0:
        ppux, _ppuy, unit = struct.unpack(">IIB", data[idx + 4:idx + 13])
        if unit == 1:
            dpi = ppux * 0.0254
    if dpi:
        findings.append(Finding(
            "INFO", "size",
            f"{path.name}: {w}x{h} px, {dpi:.0f} dpi, {w / dpi:.2f} x {h / dpi:.2f} in",
        ))
        if dpi < 300:
            findings.append(Finding(
                "FAIL", "resolution", f"{path.name} at {dpi:.0f} dpi is below the 300 dpi floor"
            ))
    else:
        findings.append(Finding("INFO", "size", f"{path.name}: {w}x{h} px, resolution not recorded"))
    return findings


def _say(text):
    """Print without dying on a legacy console codepage."""
    try:
        print(text)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "utf-8"
        print(text.encode(enc, "replace").decode(enc, "replace"))


def report(findings, header=None):
    """Print findings; return True when nothing FAILs."""
    if header:
        _say(header)
    if not findings:
        _say("  no findings")
        return True
    for f in findings:
        _say(f"  {f}")
    fails = sum(1 for f in findings if f.severity == "FAIL")
    notes = sum(1 for f in findings if f.severity == "NOTE")
    _say(f"  -> {fails} FAIL, {notes} NOTE")
    return fails == 0


def main(argv):
    if not argv or {"-h", "--help"} & set(argv):
        print(__doc__)
        return 0 if argv else 2
    target = None
    if argv[0] == "--width":
        target = float(argv[1])
        argv = argv[2:]
    ok = True
    for arg in argv:
        p = Path(arg)
        if not p.exists():
            print(f"{arg}: not found")
            ok = False
            continue
        if p.suffix.lower() == ".pdf":
            ok &= report(check_pdf(p, target), f"{p}")
        elif p.suffix.lower() == ".png":
            ok &= report(check_png(p), f"{p}")
        else:
            print(f"{p}: only .pdf and .png can be audited from disk")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
