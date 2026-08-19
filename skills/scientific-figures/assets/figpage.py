"""Check a compiled manuscript for figures whose caption runs off the page.

A tall figure with a long caption overflows the text block: the caption keeps
setting past the bottom margin and ends up printed over the page number. LaTeX
does not always warn, because the float box itself is not overfull -- the
caption simply extends into the margin. The symptom is only visible in the
compiled PDF, which is why this is a separate tool.

    python figpage.py main.pdf

Reports pages where body text reaches the folio, and pages whose content sits
well below the document's own text bottom.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

FOLIO = re.compile(r"^\s*\d{1,4}\s*$")


def _blocks(page):
    out = []
    for x0, y0, x1, y1, text, *_ in page.get_text("blocks"):
        if text.strip():
            out.append((x0, y0, x1, y1, text.strip()))
    return out


def check_document(path, slack=10.0):
    """Return (findings, body_bottom) for a compiled PDF."""
    import fitz

    path = Path(path)
    doc = fitz.open(path)
    findings = []

    # The document's own text bottom: the deepest a normal page of prose goes.
    # Taken as the median over pages, so one overflowing page cannot define it.
    bottoms = []
    for page in doc:
        rest = [b for b in _blocks(page) if not FOLIO.match(b[4])]
        if len(rest) >= 3:
            bottoms.append(max(b[3] for b in rest))
    if not bottoms:
        return findings, None
    bottoms.sort()
    body_bottom = bottoms[len(bottoms) // 2]

    for number, page in enumerate(doc, start=1):
        blocks = _blocks(page)
        # The folio is a bare number in the bottom margin. Testing "is a number"
        # alone picks up the tick labels of any plot drawn in the document, as
        # pgfplots figures are, and calls a perfectly good page broken.
        margin = page.rect.y0 + page.rect.height * 0.85

        def is_folio(b):
            return FOLIO.match(b[4]) and b[1] > margin

        folios = [b for b in blocks if is_folio(b)]
        rest = [b for b in blocks if not is_folio(b)]
        if not rest:
            continue
        for folio in folios:
            for block in rest:
                if (min(folio[2], block[2]) - max(folio[0], block[0]) > 1
                        and min(folio[3], block[3]) - max(folio[1], block[1]) > 1):
                    findings.append((
                        "FAIL", number,
                        f"the page number is printed over the text "
                        f"({block[4].split(chr(10))[0][:44]!r}); the float and its "
                        "caption are taller than the text block",
                    ))
                    break
            else:
                continue
            break
        deepest = max(b[3] for b in rest)
        # Only on a page that actually carries a float. A text page can end a
        # line or two low for ordinary reasons -- a display, a float above it
        # pushing the block down -- and reporting that as a figure overrunning
        # the page sends the author looking for a figure that is not the
        # problem. This check exists for figure plus caption.
        has_float = bool(page.get_images(full=False)) or any(
            d["rect"].width > 40 and d["rect"].height > 40
            for d in page.get_drawings())
        if has_float and deepest > body_bottom + slack:
            findings.append((
                "NOTE", number,
                f"content runs {deepest - body_bottom:.0f} pt below the text bottom "
                "of the rest of the document; shorten the caption or the figure",
            ))
    return findings, body_bottom


def main(argv):
    if not argv or {"-h", "--help"} & set(argv):
        print(__doc__)
        return 0 if argv else 2
    bad = 0
    for arg in argv:
        findings, bottom = check_document(arg)
        print(f"{arg}  (text bottom at y={bottom:.0f} pt)" if bottom else arg)
        if not findings:
            print("  no findings")
            continue
        for severity, page, message in findings:
            print(f"  {severity:<4}  page {page:<4}  {message}")
            bad += severity == "FAIL"
        fails = sum(1 for f in findings if f[0] == "FAIL")
        print(f"  -> {fails} FAIL, {len(findings) - fails} NOTE")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
